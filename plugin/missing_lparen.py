from plugin.utils import *

def insert(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN:  error: expected ‘;’ before string constant"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                                + "(" \
                                + lines[int(params[0]) - 1][cols - 1:] 
        return lines
