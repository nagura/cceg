from plugin.utils import *

import re

def remove(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: error: expected identifier or ‘(’ before ‘{’ token"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        # concatinate lines to simplify the string processing
        concatinated_line =  "".join([line for line in lines])

        # recalcurate index in the concatinated string
        cnt = 0
        for l, line in enumerate(lines):
                if l == int(params[0]) - 1:
                        break
                cnt += len(line)
        cnt += (cols - 1) # decrement character length of '{' 

        # extract incorrect string
        strs = re.search('\w+\s+\w+\([^\)]*\)(\s*\S+\s*)$', concatinated_line[:cnt])
        if strs != None:
                incorrect_str = strs.group(1)
                # remove incorrect string
                concatinated_line = concatinated_line[:cnt - len(incorrect_str)] + ''.join(re.findall('\n', incorrect_str)) + concatinated_line[cnt:]

        # translate to the line array
        return [line + '\n' for line in concatinated_line.splitlines()]
