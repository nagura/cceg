from plugin.utils import *

import re

def remove_from_functioncall(lines, params):
        # MESSAGE EXAMPLE: "NN:NN: error: expected expression before ‘int’"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        if is_c89_keyword(params[2]):
                # remove typename string
                lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                                + re.sub('^' + params[2], '', lines[int(params[0]) - 1][cols - 1:])
                
        return lines
