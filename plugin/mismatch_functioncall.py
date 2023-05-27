from plugin.utils import *

import re

def replace_ptr_in_args(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: warning: passing argument 3 of ‘keisan’ makes pointer from integer without a cast"
        #  MESSAGE EXAMPLE: "NN:NN: warning: passing argument 1 of ‘foo’ makes integer from pointer without a cast"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        # parameter number (not used)
        commas = int(params[2]) - 1

        pattern = '^\s*\*\s*' # means '*' started string (e.g. pointer)
        if re.match(pattern, lines[int(params[0]) - 1][cols - 1:]):
                # remove '*' character if exist
                lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                                + re.sub(pattern, '', lines[int(params[0]) - 1][cols - 1:]) 
        else:
                # extract function definition string of indicated function name
                def_str = get_func_def_str(lines, params[3])
                if def_str != None:
                        lines[int(params[0]) - 1] = re.sub('\s*\(\s*$', '', lines[int(params[0]) - 1][:cols - 1]) \
                                        + make_arguments_str(re.findall('\([^\)]*\)', def_str)[0]) \
                                        + re.sub('\s*[^\)]*\)', '', lines[int(params[0]) - 1][cols - 1:])
                
        return lines

def replace_ptr_in_return_args(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: returning ‘char *’ from a function with return type ‘int’ makes integer from pointer without a cast"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        line_former_half = lines[int(params[0]) - 1][:cols]
        if re.search('\($', line_former_half) != None:
                pattern = '\)\s*;'
        else:
                if re.search('\s$', line_former_half) == None:
                        line_former_half = re.sub('\s*\S+$', ' ', line_former_half) 

                pattern = '\s*;'

        # skip to end position of arguments of function call
        while cols < len(lines[int(params[0]) - 1]) and re.search(pattern, lines[int(params[0]) - 1][cols:]) != None:
                cols += 1

        # remove '*' character (make "return(0)" string)
        lines[int(params[0]) - 1] = line_former_half \
                                + "0" \
                                + lines[int(params[0]) - 1][cols - 1:] 
        return lines

def replace_args(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: error: too few arguments to function ‘wa’"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        # extract function definition string (params[2] is function name)
        def_str = get_func_def_str(lines, params[2])

        # extract line string before the function call

        if def_str != None:
                # replace argument string
                lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                                        + params[2] \
                                        + make_arguments_str(re.findall('\([^\)]*\)', def_str)[0]) \
                                        + re.sub(params[2] + '\s*\([^\)]*\)', '', lines[int(params[0]) - 1][cols - 1:])
        return lines
