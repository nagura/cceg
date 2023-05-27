from plugin.utils import *

def add(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: warning: control reaches end of non-void function"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))
        
        if lines[int(params[0]) - 1][cols - 1] == '}':
                # lack of return statement
                modified_lines = replace_comments_and_str(lines)
                def_str = get_func_def_str(substring(modified_lines, int(params[0]) - 1, cols))[-1]
                ret_type = re.findall('(\w+)\s+\w+\s*\([^\)]*\)', def_str)
                if ret_type != []:
                        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                                        + 'return (' + make_an_argument(ret_type[0]) + ');\n'\
                                        + lines[int(params[0]) - 1][cols - 1:]
                
        return lines
