from plugin.utils import *

def __fix_line(line, cols):
        # MESSAGE EXAMPLE: nn:nn: warning: missing terminating ' character
        if(line[:cols - 1].rstrip() == ""): # when all of characters before index are whitespace
                # Note: in this situation, it seems that only "'" character is written incorrectly.
                # this case is not missing "'" character so that this rule can not resolve this compilation error.
                pass
        elif (line[:cols - 1].rstrip()[-1] in "(,;="): # when the character just before index is delimiter character of terms
                # Note: this condition compares the last character of the string stripped whitespaces, that the string is produced by slicing until one letter before specified character.
                # this means that it is missing the single-quote character in the after part from specified character.
                line = insert_quote_forward(line, cols, '\'')
        else: # when the character just before index is not delimiter character of terms, the character just before index is a part of string literal
                # this means that it is missing the single-quote character in the former part from specified character.
                line = insert_quote_backward(line, cols, '\'')
        return line

def insert(lines, params):
        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        # complement the string literal by inserting the "'" character to appropriate position near the index received in parameter
        lines[int(params[0]) - 1] = __fix_line(lines[int(params[0]) - 1], cols)
        return lines

