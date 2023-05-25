from plugin.utils import *

def add(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: note: include ‘<stdio.h>’ or provide a declaration of ‘printf’"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                                + "#include" + params[2] + "\n"\
                                + lines[int(params[0]) - 1][cols - 1:] 
        return lines
