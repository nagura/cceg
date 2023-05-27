from plugin.utils import *

import re

def insert_in_methodarg(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: error: invalid operands to binary * (have ‘int (*)(int)’ and ‘int (*)(int)’)"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        # extract substring which is before lacked parentheses
        substr = lines[int(params[0]) - 1][:cols - 1]
        # add parentheses substring for first operand
        substr += make_arguments_str(params[4])
        # add operator to substring
        substr += lines[int(params[0]) - 1][cols - 1:cols]
        # extract second operand name from source code
        operand = re.findall('(\s*\w+)', lines[int(params[0]) - 1][cols:])
        # add second operand to substring
        substr += operand[0]
        cols += len(operand[0])
        # add parentheses substring for second operand
        substr += make_arguments_str(params[6])
        # add remaining string in the line
        substr += lines[int(params[0]) - 1][cols:]
        # replace corresponding line
        lines[int(params[0]) - 1] = substr

        return lines

def insert(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: warning: statement with no effect [-Wunused-value]"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        # remove characters inside double-quoted strings and comments to enable retrieving position even the string or the comment includes retrieval targeted characters.
        modified_lines = replace_comments_and_str(lines)

        # extract substring which is before lacked parentheses
        substr = modified_lines[int(params[0]) - 1][cols - 1:]

        # extract function name
        func_name = re.sub('\s*;\s*', '', substr)

        # extract function definition string
        def_str = get_func_def_str(modified_lines, func_name)
        if def_str != None:
                # replace argument string
                lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1 + len(func_name)] \
                                        + make_arguments_str(re.findall('\([^\)]*\)', def_str)[0]) \
                                        + lines[int(params[0]) - 1][cols - 1 + len(func_name):]

        return lines
