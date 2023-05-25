from plugin.utils import *

import re

def replace_varname(lines, params):
        # MESSAGE EXAMPLE: "NN:NN: error: two or more data types in declaration specifiers" (case of variable name)
        # MESSAGE EXAMPLE: "NN:NN: error: expected identifier or ‘(’ before ‘void’" (case of pointer name)

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        # extract incorrect variable/function name
        incorrect_name = re.findall('\w+', lines[int(params[0]) - 1][cols - 1:])[0]

        if is_c89_keyword(incorrect_name): # check whether the name is included in keywords or not
                vars = extract_variables(lines)

                if (get_func_def_str(lines, incorrect_name) == None): # variable name
                        # generate unused variable name
                        num = 0
                        while incorrect_name + str(num) in vars:
                                num += 1
                else: # function name
                        # generate unused function name
                        num = 0
                        while get_func_def_str(lines, incorrect_name + str(num)) != None:
                                num += 1

                lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                                + incorrect_name + str(num)\
                                + lines[int(params[0]) - 1][cols - 1 + len(incorrect_name):-1] + "\n" 
                
        return lines
