from plugin.utils import *

import re

def replace_order(lines, params):
        # MESSAGE EXAMPLE: "NN:NN: error: expected expression before ‘>’ token"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        # find the '=' character that is confused
        matched = re.findall('.*\s*(=)\s*$', lines[int(params[0]) - 1][:cols - 1])

        if matched != None:
                lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 2] \
                                + params[2] + matched[0]\
                                + lines[int(params[0]) - 1][cols:]
                
        return lines
