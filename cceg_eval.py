#!/usr/bin/python3
import os, subprocess, tempfile, shutil
import re
import argparse
import json
from enum import Enum

import opt.util as util

from plugin import *

import io

import pandas as pd

class Dest(Enum):
    ERR = 'ERR'
    ERR_NUM = 'ERR_NUM'
    DEBUG = 'DEBUG'
    RESULT = 'RESULT'
    GRP_NUM = 'GRP_NUM'
    RULES = 'RULES'

### ログ出力制御用クラス
class Logger:
    def __init__(self, debug):
        self.__debug = debug
        self.__log = {}
        for mode in Dest:
               self.__log[mode.value] = ''

    def print(self, *args, end='\n', mode=Dest.DEBUG):
        if self.__debug:
                with io.StringIO() as s:
                        print(*args, file=s,end=end)
                        str = s.getvalue()
                        self.__log[mode.value] += str
        return

    def save(self, s):
        for mode in Dest:
                if mode != Dest.RULES:
                        s = pd.concat([s, pd.Series([self.__log[mode.value]], index = [mode.value])])
                else:
                        s = pd.concat([s, pd.Series([self.__log[mode.value].split()], index = [mode.value])])
        return pd.DataFrame(s).T
               
### 修正可否を示すための列挙子
class Status(Enum):
    NONE = 0
    ALL_SOLVED = 1
    PARTIALLY_SOLVED = 2

### シーケンス番号で始まるファイル名を管理するためのクラス
class Fname:
    def __init__(self):
        self.__seq = 0
        self.__seqinit = self.__seq

    def srcfname(num):
        return str(num) + '.c'

    def outfname(num):
        return str(num) + '.out'

    def names(self):
        return (Fname.srcfname(self.__seq), Fname.outfname(self.__seq))

    def next(self):
        self.__seq += 1
        return self.names()

    def prev(self):
        self.__seq -= 1
        return self.names()
    
    def seq(self):
        return self.__seq
    
    def get_orig_err_fname(self):
        return Fname.outfname(self.__seqinit)
           
### ファイルをオープンして，行単位で配列に格納する
def open_file(fname):
        lines = []
        # ファイルを開く
        with open(fname, encoding="utf-8") as f:
                for line in f:
                        lines.append(line)
        return lines

### ルールにマッチした文字列から正規表現の後方参照として指定された部分を抜き出し，パラメータを作成．
def makeparams(char, path):
        group_len = len(char.groups())
        params = []
        target = os.path.join(path, char.group(1))
        for cnt in range(group_len - 1):
                params.append(char.group(cnt + 2))
        # 対象ファイル名には，絶対パスを付加する．
        return (target, params)

### コンパイル処理．コンパイル結果を，行ごとに配列にして返却．
def compile_process(src, exec, warn, cwd=None, display=False, first_time=False):
        if util.c_compiler() != None:
                cmd = [util.c_compiler()]
        else:
                cmd = ["gcc"]
        if warn != None:
                cmd.extend(["-W" + warn])
        if exec != None:
                cmd.extend(["-o", exec])
        if cwd != None:
                log.print("== source file " + os.path.join(cwd, src) + " start ==")
                log.print("".join(open_file(os.path.join(cwd, src))).rstrip())
                log.print("== end of file ==")
        cmd.extend([src])
        cmd_str = ''
        for str in cmd:
                cmd_str += str + ' '
        log.print("[Executed command] " + cmd_str)
        cp_compile = subprocess.run(cmd, capture_output=True, cwd=cwd)
        errmsg = cp_compile.stderr.decode("utf8")
        if display:
                if(first_time):
                        log.print(errmsg, end='', mode=Dest.ERR)
                else:
                        log.print("[Compile Error Messages]")
                        log.print(errmsg, end='')
        return errmsg

### コンパイル結果のメッセージを保存．保存したかどうかを返却．
def store_msgs(msg, tmpdir, fname):
        if (len(msg) == 0):
                # メッセージが無いときは保存しない
                return False
        with open(os.path.join(tmpdir, fname), 'w') as f:
                print(msg, file=f, end='') # 最後に余計な改行文字を付加しないようにしている
        return True

### コンパイル結果から，エラーを示す "XX.c:nn:(nn:)?" 形式で始まる行のみを抽出して返却
def get_errs(lines):
        messages = []
        for line in lines:
                if char := re.match("^(\\w+.c:\\d+:(\\d+:)? .+)", line):
                        messages.append(char.group(1))
        return messages

### エラーメッセージが "XX.c:nn:nn:" 形式ではなく，"XX.c:nn:" 形式（文字番号が無い）時に，内部処理用に文字番号0を追加する
def fix_msg(msg):
        if char := re.match("(\\w+.c:\\d+:)([^\\d]+)", msg):
                msg = char.group(1) + '0:' + char.group(2)
        return msg

### 指定されたエラーが解消したかどうかを判定
def isResolved(target_msg, orig_msgs, err_msgs):
        # 指定された元のエラーメッセージから，行番号と文字番号，メッセージを取り出す
        if not (char := re.match("\\w+.c:(\\d+):(\\d+): (.+)", fix_msg(target_msg))):
                return False
        line_no = int(char.group(1))
        column_no = int(char.group(2))
        msg_body = char.group(3)

        ## 指定されたエラーが解消されたかの判定
        # 指定されたエラーに該当するメッセージのエラーメッセージ数を取得
        cnt_pre_msgs = len([msg for msg in orig_msgs if msg_body in msg])
        cnt_aft_msgs = len([msg for msg in err_msgs if msg_body in msg])
        # 修正前後で減らなかった場合は，指定されたエラーメッセージを解消できていない
        if cnt_aft_msgs >= cnt_pre_msgs:
                return False

        ## エラー解消によって別のエラーが生じていないかどうかの判定
        # 修正後のエラーメッセージ各行についてループ
        for err in err_msgs:
                if char := re.match("\\w+.c:(\\d+):(\\d+): error: (.+)", fix_msg(err)):
                        # 修正対象のエラーが含まれる行に対して，修正後に修正対象のエラーより前の文字にエラーが発生したら，
                        # 修正が失敗したとみなす．
                        if line_no == int(char.group(1)) and column_no >= int(char.group(2)):
                                return False
        return True

### msg_grps と err_msgs を比較して，msg_grps のメッセージで解決したものを，このコンパイルに対するグループ番号 num でマークする
def markResolved(target_line, msg_grps, err_msgs, num):
        resolved = False

        # 判別対象のメッセージと，比較対象のメッセージの選択
        orig_msgs = [] 
        err_msgs = get_errs(err_msgs) # 修正後に発生したエラーメッセージ（比較対象）
        for msg in  msg_grps.keys() : # 元のエラーメッセージから判別対象を選択するためのループ
                if re.sub('^\\w+.c:', '', msg) ==  re.sub('^\\w+.c:', '', target_line.rstrip()):
                       # 修正対象のエラーメッセージについては，判別対象には後で加える．また比較対象からも外さないので，スキップ．
                       continue
                
                # 修正対象のエラーメッセージ以外についての処理
                if re.sub('^\\w+.c:', '', msg) not in [re.sub('^\\w+.c:', '', err) for err in err_msgs]:
                        # 元のメッセージが修正後に発生していない場合は，修正によって解決した可能性があるので判別対象に加える．
                        orig_msgs.append(msg)
                else:
                        # 元のメッセージが修正後にも発生している場合は，修正によって影響を受けない部分に対するエラーなので，判別対象に加えない．
                        # その場合は比較するとこの修正によって増えたとみなされるので比較対象からも外す．
                        err_msgs = [err_msg for err_msg in err_msgs if re.sub('^\\w+.c:', '', err_msg) != re.sub('^\\w+.c:', '', msg)]
        
        # まだ解決していないメッセージのみに判別対象を絞る．
        orig_msgs = [msg for msg in orig_msgs if msg_grps[msg] == 0]

        # 修正対象のエラーメッセージを判別対象メッセージの先頭に加える．
        target_in_grpkey = [err_msg for err_msg in msg_grps.keys() if re.sub('^\\w+.c:', '', err_msg) == re.sub('^\\w+.c:', '', target_line.rstrip())] # 修正対象のメッセージに対応する判別対象のメッセージを取得
        if target_in_grpkey != []:
                orig_msgs.insert(0, target_in_grpkey[0])
        
        # 判別対象の各メッセージについて，解決したかどうかを判別する
        for orig_msg in orig_msgs:
                # msg_grps から取得したメッセージについて，解決したかどうかを判定
                if isResolved(orig_msg, orig_msgs, err_msgs):
                        resolved = True
                        if orig_msg in msg_grps.keys():
                                msg_grps[orig_msg] = num
                else:
                        if re.sub('^\\w+.c:', '', target_line.rstrip()) == re.sub('^\\w+.c:', '', orig_msg):
                                # 修正対象のエラーが解決しない場合は，他のエラーはチェックせずに False を返す．
                                resolved = False
                                break
        log.print("[Grouping Status]")
        log.print(msg_grps)
        return (resolved, msg_grps)

### list_errmsg から指定されたグループのメッセージを表示．
def display_group(g_no, msg_grps, list_errmsg):
        # list_errmsg のうち，g_no に対応するメッセージ（対応は msg_grps に記述）を，すべて表示する．
        
        # g_no に対応するメッセージを抽出
        g_msg_list = []
        for k, v in msg_grps.items():
                if v == g_no:
                        g_msg_list.append(k)
        
        if g_msg_list != []:
                # 表示すべきメッセージがあるとき
                if g_no == 0:
                        # g_no == 0 は，分類不能なメッセージ
                        log.print("--- Uncategorized Message ---", mode=Dest.RESULT)
                else:
                        log.print("--- Error Group #" + str(g_no) + " ---", mode=Dest.RESULT)

                the_func = None
                src_fname = None
                for [msg, func_name] in list_errmsg:
                        if char := re.match("(\\w+.c):(\\d+):(\\d+): ", fix_msg(msg)):
                                # "XX.c:nn:nn:" 形式で始まる行だった時は，次の "XX.c:nn:nn:" の行までが一つのメッセージのかたまり
                                if msg in g_msg_list:
                                        # 表示すべきメッセージに含まれる場合：ソースファイル名を取得．
                                        src_fname = char.group(1)
                                else:
                                        # 表示すべきメッセージに含まれない場合：ソースファイル名をクリア．
                                        src_fname = None
                        if src_fname != None:
                                if the_func != func_name:
                                       the_func = func_name
                                       log.print(src_fname + ": In function " + the_func + ":", mode=Dest.RESULT)
                                log.print(msg, mode=Dest.RESULT)

        # 表示しなかったメッセージ（g_no 以外のメッセージ）を返却                
        return {k: v for k, v in msg_grps.items() if v != g_no}

### プログラムの終了時の処理
def cleanup_exit(tmpdir):
        # テンポラリディレクトリとファイルを削除
        shutil.rmtree(tmpdir)
        #exit(0)

def main():
        ### ルールの読込み
        json_open = open(util.rule_json(), 'r')
        rule_json = json.load(json_open)

        tmpdir = tempfile.mkdtemp()

        ### ソースファイル名，出力記録用ファイル名の作成
        # ファイル名は，0 からのシーケンス番号で生成される．
        # 最初のソースファイル名（元ファイル）については，エラーメッセージの都合で 0.c ではなく元のファイル名を利用．
        fnames = Fname()
        (src_fname, out_fname) = fnames.names()

        ### 元のソースファイルのコンパイル
        if store_msgs(compile_process(src, exec, warn, display=disp, first_time=True), tmpdir, out_fname) == False:
                # 元のファイルに対してのコンパイルが成功 → 後処理をして終了する
                cleanup_exit(tmpdir)

        ### 各エラーメッセージに対するグループを記録するための辞書型配列を作成
        # "XX.c:nn:nn: ..." 形式で始まる行は，一度のコンパイルに一行しか現れないことを仮定
        msg_grps = {}
        for msg in get_errs(open_file(os.path.join(tmpdir, out_fname))):
                msg_grps = {**msg_grps, msg: 0} # 0 means unresolved
        log.print(str(len(msg_grps)), end='', mode=Dest.ERR_NUM)

        ### ソースファイルを，テンポラリディレクトリにコピー（エラーメッセージからの参照に利用）
        shutil.copyfile(src, (os.path.join(tmpdir, src))) 

        # print("Temporary Directory is : " + tmpdir + "\n")

        log.print("==== Matching process start ====")

        ### コンパイルエラーの分類処理
        while True: # コンパイルエラーが残り続けている間ループ
                status = Status.NONE
                # コンパイルエラーを行単位で読込み
                log.print("<<loading err messages in " + out_fname + " ...>>")
                err_lines = open_file(os.path.join(tmpdir, out_fname))

                # コンパイルエラーの各行を，行単位でルールと比較
                for cnt, line in enumerate(err_lines):
                        for rule in rule_json:
                                # 各ルールと，if 部を比較
                                if char := re.match("(\\w+.c):" + rule_json[rule]['if'], line):
                                        log.print("Matched: { rule: " + rule + " }, { line: " + line.rstrip() + " }")
                                        # ルールにマッチした文字列を指定された抜き出す．
                                        (target, params) = makeparams(char, tmpdir)
                                        # ソースコードを読込み
                                        lines = open_file(target)
                                        # then 部に記載されたメソッドに対する呼出し文を生成．
                                        cmd = rule_json[rule]['then'] + "(lines, params)"
                                        log.print("cmd = " + cmd + " target = " + target + " params = " + str(params))
                                        # ファイル名用のシーケンス番号をインクリメント
                                        (src_fname, out_fname) = fnames.next()
                                        # then 部の修正処理を実施して，ソースファイルを保存
                                        with open(os.path.join(tmpdir, src_fname), 'w') as f:
                                                # 修正後ソースファイルを保存
                                                try:
                                                        lines_orig = lines
                                                        lines = eval(cmd)
                                                except:
                                                        # プラグイン実行でエラーがあった場合には，修正せずに続行する．
                                                        print("\033[31m[Message]\033[0m When the plugin module '" + rule_json[rule]['then']  + "' is executed the exception has occured by plugin execution, but continuing to processing.")
                                                        print("\tRule: " + rule)
                                                        print("\tMatched error message: " + line.rstrip())
                                                        print("\tParameters for plugin execution: " + str(params))
                                                        print("The occurred exception is follows: ")
                                                        import traceback
                                                        print("--- exception start --- ")
                                                        traceback.print_exc()
                                                        print("--- exception end --- ")
                                                        lines = lines_orig
                                                f.writelines(lines)
                                        
                                        # 修正後ソースファイルをコンパイル
                                        if store_msgs(compile_process(src_fname, exec, warn, tmpdir, display=disp), tmpdir, out_fname) == True:
                                                # 修正後ソースファイルにエラーが残存
                                                (resolved, msg_grps) = markResolved(line, msg_grps, open_file(os.path.join(tmpdir, out_fname)), fnames.seq())
                                                if resolved: # エラーが1つ以上解決された
                                                        # 修正したファイルのコンパイル結果を基にする必要がある．
                                                        log.print(rule, end=" ", mode=Dest.RULES)
                                                        status = Status.PARTIALLY_SOLVED
                                                else: #エラーが無くならなかったか，別のエラーが生じた（修正失敗）
                                                        # 修正を破棄して，次のエラー行を検査する
                                                        os.remove(os.path.join(tmpdir, src_fname))
                                                        os.remove(os.path.join(tmpdir, out_fname))
                                                        (src_fname, out_fname) = fnames.prev()
                                        else: 
                                                #エラーが全部なくなった
                                                (resolved, msg_grps) = markResolved(line, msg_grps, "", fnames.seq()) # エラーメッセージは発生していないので空文字
                                                log.print(rule, end=" ", mode=Dest.RULES)
                                                status = Status.ALL_SOLVED
                                        log.print(str(status))
                                if status != Status.NONE: # ルールが適用できなかったか，適用しても解決しなかったら，次のルールを試す．そうでない場合は break
                                        break
                        if status == Status.PARTIALLY_SOLVED or status == Status.ALL_SOLVED:
                                # なにかのルールで解決された場合は，修正したファイルのエラーメッセージに対して処理を実施する（再度読み直す）．
                                break
                        if cnt == len(err_lines) - 1:
                                # Status.None で for ループが最後の行だったら，すべてチェック済
                                break
                if status == Status.ALL_SOLVED or status == Status.NONE:
                        # すべて解決したか，全てのエラー行に対してどのルールを使っても解決できなかった場合
                        break

        log.print("==== Matching process end ====\n")

        ### 結果の表示
        # 元のエラーメッセージの各行を list_errmsg 配列に読込み，各行の所属する関数名と対応付けて保存
        list_errmsg = []
        func_name = None

        for msg in open_file(os.path.join(tmpdir, fnames.get_orig_err_fname())):
                if char := re.match("\\w+.c: In function (\S+):", msg):
                        func_name = char.group(1)
                        continue
                list_errmsg.append([msg.rstrip('\r\n'), func_name])

        # グループ番号 1 から順に結果を表示
        g_no = 1
        while True:
                remain_msgs = display_group(g_no, msg_grps, list_errmsg)
                if msg_grps == remain_msgs: # 表示対象のメッセージが無かったので何も表示していない場合
                        break
                msg_grps = remain_msgs
                g_no += 1
                log.print("", mode=Dest.RESULT) # グループごとの区切りのために改行
        log.print(str(g_no - 1), end='', mode=Dest.GRP_NUM)

        # 分類できなかったメッセージを表示
        if len(msg_grps) > 0:
                # 分類できなかったメッセージ（グループ番号 0）がある．
                display_group(0, msg_grps, list_errmsg)
                log.print("", mode=Dest.RESULT) # グループごとの区切りのために改行

        # 後処理をして終了
        cleanup_exit(tmpdir)

if __name__ == "__main__":
        src = "temp.c"

        ### コマンドライン引数の解析
        parser = argparse.ArgumentParser(description="C Compiler with Error message Grouping (for evaluation)")
        parser.add_argument('file', help="csv file to evaluate")
        parser.add_argument("-s", metavar='N',help="error number to start")
        parser.add_argument("-t", metavar='N',help="number of error reports to evaluate")


        args = parser.parse_args()
        csv = args.file

        warn = "all"
        exec = None
        disp = True

        if args.s == None:
               start = 0
        else:
               start = int(args.s)

        if args.t == None:
               num_eval = 0
        else:
               num_eval = int(args.t)

        df = pd.read_csv(csv, names=('name', 'fname', 'list', 'errors', 'times', 'datetime'))
        df2 = pd.DataFrame(columns=df.columns)

        df2 = None
        for i, record in enumerate(df.itertuples()):
                if i + 1 < start:
                       continue
                print("processing " + str(i + 1) +"th error message....")
                log = Logger(True)
                with open(os.path.join(".", src), 'w') as f:
                        print(record.list, file=f, end='') # 最後に余計な改行文字を付加しないようにしている

                main()
                if df2 is None:
                        df2 = log.save(df.loc[i])
                else:
                        df2 = pd.concat([df2, log.save(df.loc[i])], ignore_index=True, axis=0)
                if num_eval - 1 == i:
                        break
        df2.to_csv("eval.csv")


