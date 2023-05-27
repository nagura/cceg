import sys
import re

# correct column number when the given line includes Multi-byte characters
def correct_cols(line, orig_cols):
        corr_cols = 0
        for c in line:
                if orig_cols <= 0:
                     break
                # subtract the number of character under considering Multi-byte character
                orig_cols -= len(c.encode(sys.getdefaultencoding()))
                corr_cols += 1
        return corr_cols

# mask the strings and the comments in the program code with the given character
# Note: the number of lines will be kept, and when given character is single character, the number of columns also will be kept.
def replace_comments_and_str(lines, ch=' '):
        def replace_str(str, target, ch, esc): ### replace the string
                # search the string "target" from the given string "str", then replace the first matched substring with the given character 'ch'.
                # in this replacing procedure, the given character "esc" will be kept.
                # Note: specify '\n' for the character "esc", to keep the line break. specify the '"" for the character "esc", to keep the double-quotes indicates the beginning/end of string.
                return str.replace(target, "".join([esc if c == esc else ch for c in target]), 1)

        # concatinate lines to simplify the string processing
        concatinated_line =  "".join([line for line in lines])

        # mask the double-quoted string literal
        pattern = '\"[^(\"\n)]*\"' # the pattern for string literal
        while matched := re.search(pattern, concatinated_line): # extract the string literal (XXX: string literal is not over multi-line is supposed)
                concatinated_line = replace_str(concatinated_line, matched.group(), ch, None)

        # mask the inline comment
        pattern = '//(.*)\n' # the pattern for inline comment
        while matched := re.search(pattern, concatinated_line): # extract the inline comment (keep the '\n' character at tail of line)
                concatinated_line = replace_str(concatinated_line, matched.group(), ch, '\n')

        # mask the block comment
        pattern = '/\*([^*]|\*[^\/])*\*\/' # the pattern for block comment
        while matched := re.search(pattern, concatinated_line): # extract the block comment
                # when the block comment includes line break, output same number of them to keep line number
                concatinated_line = replace_str(concatinated_line, matched.group(), ch, '\n')
        
        # return lines as array structure
        return [line + '\n' for line in concatinated_line.splitlines()]

# extract type list of parameters from parameter string
def parse_params(params_str):
        # whether parameter string is exist or not
        params = []
        if params_str != None and params_str.strip() != '':
                # split parameter string when which contains multiple parameter
                params = [s.strip() for s in params_str.split(',')]
                # remove variable name string from each parameter
                params = [re.findall('^\w+\s*\*?\s*', param)[0].strip() for param in params]
                # add space character when type string and '*' character are close without any space
                params = [re.sub('(\w+)(\*)', '\\1 \\2', param) for param in params]
        return params


## extract function definition string of func_name function from source code list
def get_func_def_str(lines, func_name='\w+'):
        # remove characters inside double-quoted strings and comments to enable retrieving position even the string or the comment includes retrieval targeted characters.
        modified_lines = replace_comments_and_str(lines)

        # concatinate lines to simplify the string processing
        concatinated_line =  "".join([line for line in modified_lines])

        # extract function definition string
        matched = re.findall('(\w*)\s+\*?(' + func_name + ')\s*\(([^\)]*)\)\s*\{', concatinated_line)

        func_defs = []
        for func in matched:
                if is_c89_keyword(func[1]):
                        continue
                
                ret_type = func[0] # return type string
                params_str = func[2] # parameter string

                # extract parameter type lists
                params = parse_params(params_str)
                # create array with the string pair of function name and normalized function definition string
                func_defs.append([func[1],  (func[0] + ' ' + func[1] + '(' + ', '.join(params) + ')').strip()])
        
        if func_name != '\w+':
                # return function definition string specified by func_name
                matched_funcs = [def_str[1] for def_str in func_defs if def_str[0] == func_name]
                return None if matched_funcs == [] else matched_funcs[0]
        else:
                # return all function definition string list ordered by appearance
                return [def_str[1] for def_str in func_defs]

# make an argument from type string
def make_an_argument(typestr):
        str = ""
        if typestr in ['char *']:
                str = "\"XX\""
        elif typestr in ['int *', 'short *', 'long *']:
                str = '(' + typestr +')' + "0"
        elif typestr in ['double * ', 'float *']:
                str = '(' + typestr +')' + "0.0"
        elif '*' in typestr:
                # could not make parameters with other pointers
                str = "NULL"
        elif typestr in ['int', 'short', 'long']:
                str = "0"
        elif typestr in ['double', 'float']:
                str = "0.0"
        elif typestr in ['char']:
                str = "'X'"
        return str

# make fulfilled arguments of function call from parameters string of parentheses block
def make_arguments_str(str):
        # remove parentheses
        str = re.findall('\(\s*(.*)\s*\)', str)
        # pick the parameters' type
        params = [s.strip() for s in str[0].split(',')]

        # make string of parentheses block
        param_str = "("
        for i, param in enumerate(params):
                param_str += make_an_argument(param)
                if i + 1 < len(params):
                        param_str += ","
        param_str += ")"
        return param_str

# cut out the substring of lines by index
def substring(lines, l_idx, c_idx):
        # concatinate lines to simplify the string processing
        concatinated_line =  "".join([line for line in lines])

        # count index value in the concatenated string
        cnt = 0
        for l, line in enumerate(lines):
                if l == l_idx:
                        break
                cnt += len(line)
        cnt += c_idx

        return [line + '\n' for line in concatinated_line[:cnt].splitlines()]



# check whether the word is one of C language keyword or not
def is_c89_keyword(word):
        keywords = {'auto', 'break', 'case', 'char', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto', 'if', 'int', 'long', 'register', 'return', 'short', 'signed', 'sizeof', 'static', 'struct', 'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 'while'}
        return True if word in keywords else False

# extract all variables from program lines
def extract_variables(lines):
        # split space separated string list to each word
        def split_spaces(list):
                words = []
                for str in list:
                        splited = str.split(' ')
                        for s in splited:
                                words.append(s)
                return words


        # remove comments and strings
        lines = replace_comments_and_str(lines, ch='')

        # concatinate lines to simplify the string processing
        concatinated_line =  "".join([line for line in lines])

        # extract statements in functions
        matched = re.findall('\s*(.*)\s*;\s*\n', concatinated_line)
        # extract statements in parentheses of conditions/loops
        matched += re.findall('\s*(.*)\s*{\s*\n', concatinated_line)
        
        # remove function name and parentheses and keyword for conditions/loops/types
        flag = True
        while flag:
                flag = False
                for cnt, str in enumerate(matched):
                        pattern = '\w*\s*\w+\s*\((.*)\)' # regex pattern to remove function name and parentheses and keyword for conditions/loops/types
                        if re.findall(pattern, str) == []:
                                pass
                        else:
                                # remove except matched pattern
                                matched[cnt] = re.sub(pattern, '\\1', str)
                                flag = True

        # replace ',' character which separates between arguments to whitespace
        matched = [str.replace(',', ' ').strip() for str in matched]

        # replace operators and contiguous whitespaces to a space
        matched = [re.sub('[\s\&\=\+\*/-]+', ' ', str) for str in matched]
        # remove cast operators
        matched = [re.sub('\([\w\s]*\)', '', str).strip() for str in matched]

        # split space separated string to each word
        matched = split_spaces(matched)
        # remove index (number and squares) of array
        matched = [re.sub('\[\d*\]', '', str).strip() for str in matched]
        # remove characters that variable name should not contain (e.g. '(' ')' )
        matched = [re.sub('[^\w]', '', str).strip() for str in matched]
        # remove duplicate element to unique elements
        matched = set(matched)
        # remove elements consist of only numbers
        matched = [str for str in matched if re.sub('\d*', '', str).strip() != '']

        # remove elements which are C89 keywords
        matched = [str for str in matched if not is_c89_keyword(str)]

        return matched

# insert quote character 'ch' to forward place (the next direction) from index
def insert_quote_forward(line, cols, ch):
        idx = cols + 1 # search the place from next character of index
        while not (line[idx] in "),;\n" or idx == len(line)): # loop until delimiter character of terms
                idx += 1
        while line[idx - 1] in "\t\n " : # rewind the index when the index points white space not to include them to quoted string.
                idx -= 1
        return line[:idx] + ch + line[idx:] # insert quote to just before of delimiter character.

# insert quote character 'ch' to backward place (the previous direction) from index
def insert_quote_backward(line, cols, ch):
        idx = cols - 1 # search the place from previous character of index
        while not (line[idx] in "(,;=" or idx == -1): # loop until delimiter character of terms (or beginning of the line)
                idx -= 1
        while line[idx + 1] in "\t\n " : # skip the index when the index points white space not to include them to quoted string.
                idx += 1
        return line[:idx + 1] + ch + line[idx + 1:] # insert quote to just after of delimiter character.

