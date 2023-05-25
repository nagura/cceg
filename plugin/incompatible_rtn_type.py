from plugin.utils import *

def adjust_rtn_type(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: warning: assignment to ‘int *’ from ‘int’ makes pointer from integer without a cast"
        #  MESSAGE EXAMPLE: "NN:NN: warning: assignment to ‘int’ from ‘int *’ makes integer from pointer without a cast"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))
        
        if lines[int(params[0]) - 1][cols - 1] == '=':
                # assignment incompatible type
                if re.match('\w* \*', params[2]) != None and re.match('\w* \*', params[3]) == None:
                        # when return value is non-pointer and assigned variable is pointer
                        match = re.search('\w+\s*$', lines[int(params[0]) - 1][:cols - 1])
                        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:match.start()] \
                                        + '*' \
                                        + lines[int(params[0]) - 1][match.start():]
                else:
                        # when return value is pointer and assigned variable is non-pointer
                        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols] \
                                        + ' *' \
                                        + lines[int(params[0]) - 1][cols:].lstrip()

        return lines
