from plugin.utils import *

def insert(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: error: expected ‘)’ before ‘;’ token"

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        # when the character pointed by index is a kind of parentheses, it means a confusing is occured to use parentheses,
        # replace the parentheses character 
        latter = lines[int(params[0]) - 1][cols:] if lines[int(params[0]) - 1][cols - 1] in "({[]})" \
                else lines[int(params[0]) - 1][cols - 1:]


        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                                + params[2] \
                                + latter
        return lines

def insert_unspecified_char(lines, params):
        # insert the character not specified in err message
        # MESSAGE EXAMPLE: "NN:NN: error: expected expression before ‘)’ token -> case 1
        # MESSAGE EXAMPLE: "NN:NN: error: expected expression before ‘%’ token -> case 2

        done = False
        if params[2] == ')': # case 1
                # correct column number which includes Zenkaku characters
                cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))
                if (matched := re.match('\s+for\s*\(', lines[int(params[0]) - 1][:cols - 1])) != None:
                        # insert ';' character in for loop
                        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                                                + ';' \
                                                + lines[int(params[0]) - 1][cols - 1:]
                        done = True

        if not done: # case 2
                # insert '"" character
                params[2] = "\""
                lines = insert(lines, params)
        return lines
