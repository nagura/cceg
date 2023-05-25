from plugin.utils import *

import re

def insert_for_array_def(lines, params):
        # extract longuest match word with 'name' string
        def longuest_match(name, list):
                # make list of words (of 'list') which are contained in 'name' string
                matched_list = [str for str in list if re.findall('^' + str, name) != []]
                # count the characters of strings which are contained in generated list
                matched_characters = {len(str) : str for str in matched_list}

                # return longuest matched word
                return None if matched_characters == {} else matched_characters[max(matched_characters.keys())]

        # MESSAGE EXAMPLE: "NN:NN: error: expected ‘=’, ‘,’, ‘;’, ‘asm’ or ‘__attribute__’ before ‘]’ token"
        # Note: for missing left square bracket [ at array definition

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        # extract incorrect array name from program list
        incorrect_name = re.sub('^.*\s+', '', lines[int(params[0]) - 1][:cols - 1])

        # extract all variables from program lines except the line related to the compile error
        var_list = extract_variables(lines[:int(params[0]) - 1] + lines[int(params[0]) - 1 + 1:])
        # match incorrect array name with name from variable list
        correct_name = longuest_match(incorrect_name, var_list)
        # extract array size from incorrect array name string
        # for example, correct array name string for definition is a[10] and incorrect is a10], the difference between the correct name string 'a' and the incorrect name string 'a10' will be array size
        index = re.sub('^' + correct_name, '', incorrect_name)

        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1 - len(incorrect_name)] \
                        + correct_name + '[' + index +']'\
                        + lines[int(params[0]) - 1][cols:] 

        return lines
