from plugin.utils import *

import re

def insert(lines, params):
        # MESSAGE EXAMPLE: "NN:NN: error: expected declaration or statement at end of input"
        # Note: for missing right curly brackets } 
        # XXX: Couldn't handle the missing right curly for structure declaration

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        # the method rewinds the index one letter before
        def move_prev(lines, l_idx, c_idx):
                if c_idx == 0: # when the index points the character at the beginning of the line
                        if l_idx == 0: # returns error that means it could not rewinds index one letter before.
                                raise LookupError
                        l_idx -= 1 # rewinds the index to previous line.
                        c_idx = len(lines[l_idx]) # change index to after the last character of rewinded line.
                c_idx -= 1 # rewinds the index to one letter before in the line.
                return (l_idx, c_idx)

        # the method detecting the index of correspondent (given) starting character (e.g. lcurly).
        # this method regards the character pointed by given index as the terminating character.
        def search_correspondent_symbol_backward(lines, l_idx, c_idx, l_sym):
                lv = 0 # nested level
                r_sym = lines[l_idx][c_idx] # the index of terminating character (given index)

                while True: # checks character by one character at the before part of given index
                        if lines[l_idx][c_idx] == r_sym: # when the character is terminating character
                                lv += 1 # increment the nested level
                        elif lines[l_idx][c_idx] == l_sym: # when the character is starting character
                                lv -= 1 # decrement the nested level
                        if lv == 0: # when the nested lebel become 0, it means the index points the corresponding symbol.
                                break
                        (l_idx, c_idx) = move_prev(lines, l_idx, c_idx)  # rewinds the index to previous letter.
                return (l_idx, c_idx)

        # the method judges whether the just before part pointed by the index is the string of function definition
        def is_function_definition(lines, l_idx, c_idx):
                # cut out the substring of lines by index
                lines = substring(lines, l_idx, c_idx)
                
                # judge whether the string until before the index is function definition "xxx xxxx(xxx)" 
                if re.search('\w+\s+\w+\s*\([^\)]*\)\s*$', "".join([line for line in lines])) == None:
                        # not function definition
                        return False
                return True

        ### detects the rcurly (}) character from the latter part of string/line from specified index
        # if the rcurly (}) character is detected, detects the corresponded lcurly ({) character from before part of the index.
        # if the rcurly (}) character is not detected, detects the semi-colon as terminating character of statement from after part of the index, then add the rcurly (}) character at the next of the semi-colon.

        # the index pointed in the compilation error message
        l_idx = int(params[0]) - 1
        c_idx = cols - 1

        if lines[l_idx][c_idx:].find('}') != -1:
                # the rcurly (}) character is detected at the latter part of string/line from specified index
                # -> detects the corresponded lcurly ({) character from before part of the index, then insert the rcurly (}) character at the previous of the lcurly ({) character
                c_idx += lines[l_idx][c_idx:].find('}') # move the index to the previous character of detected rcurly (}) character.

                # store index to later use
                last_l = l_idx
                last_c = c_idx

                # mask the strings and the comments in the program code to prevent miss detection when the strings include the rcurly (}) character.
                modified_lines = replace_comments_and_str(lines)

                try: 
                        # detects the lcurly ({) character corresponded to the rcurly (}) character located just after the index written in compilation error message
                        (l_idx, c_idx) = search_correspondent_symbol_backward(modified_lines, l_idx, c_idx, '{')
                except LookupError: # could not detect the corresponded lcurly ({) character. (Note: this situation is occured when grammatical error is included. however according to the definition of compiliation error, so this situation will not be occured.)
                        return lines # returns lines received in the parameter without any change


                if is_function_definition(modified_lines, l_idx, c_idx):
                        # when the just before part from index is function definition, the part of strings between the rcurly (}) character located just after the index from error message and detected corresponded lcurly ({) character is the function definition. so the part does not include the missing of the rcurly (}) character.

                        # insert the rcurly (}) character just after to the semi-colon (;) character appeared before thecorresponded lcurly ({) character
                        # Note: When the semi-colon (;) character was missing which it is located just before line of the rcurly (}) character, the missing may be already fixed by using other error message. 
                        # So that in this step, it simply detects semi-colon character only.
                        while True:
                                if lines[l_idx][c_idx] == ";": # detects the location of semi-colon ";" character
                                        break
                                try: 
                                        (l_idx, c_idx) = move_prev(lines, l_idx, c_idx) # rewinds the index to previous letter
                                except LookupError: # could not detect the corresponded semi-colon (;) character. (Note: this situation is occured when grammatical error is included. however the missing may be already fixed, so this situation will not be occured.)
                                        return lines # returns lines received in the parameter without any change
                        
                        # XXX: Essentially, it should be done same procedure (detecting the rcurly (}) and the lcurly ({) characters) for more before part.
                        # Under the circumstances, based an implicit assumption that the missing of the rcurly (}) character is included in the function just before last function.
                        
                else:
                        # when the just before part from index is not function definition, the missing is contained in the area (from last '}' to detected '{'). so the rcurly (}) will be added after the last character of thae area.
                        l_idx = last_l
                        c_idx = last_c

        else:
                # the rcurly (}) character is not detected at the latter part of string/line from specified index (the rcurly (}) character is missed which should exist after specified index )
                # -> detects the semi-colon (;) character, then insert the rcurly (}) character at the after the semi-colon character
                # Note: When the semi-colon (;) character was missing which it is located just before line of the rcurly (}) character, the missing may be already fixed by using other error message. 
                # So that in this step, it simply detects semi-colon character only.
                while lines[l_idx][c_idx] != ";":
                        c_idx += 1
        
        # insert/add "}" character after the character pointed by the index
        lines[l_idx] = lines[l_idx][:c_idx + 1] \
                                + "}" \
                                + lines[l_idx][c_idx + 1:] 
        return lines

def replace(lines, params):
        # MESSAGE EXAMPLE: "NN:NN: error: expected statement before ‘)’ token
        # Note: to replace confusing right curly brackets } and ) or ] parentheses

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                        + "}" \
                        + lines[int(params[0]) - 1][cols:] 
        return lines

