from plugin.utils import *

def replace(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: error: unknown type name ‘inr’; did you mean ‘int’?"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                                + params[3] \
                                + lines[int(params[0]) - 1][cols - 1 + len(params[2]):] 
        
        return lines
