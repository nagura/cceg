from plugin.utils import *

import re

def __insert_lcurly(lines, params, pattern):
        # concatinate lines to simplify the string processing
        concatinated_line =  "".join([line for line in lines])
        
        # extract position of string without '{' character
        matched = re.search(pattern, concatinated_line)

        if matched != None:
                # insert '{' character before matched.start() + len(matched.group(1))
                concatinated_line = concatinated_line[: matched.start() + len(matched.group(1))] \
                                        + '{' \
                                        + concatinated_line[matched.start() + len(matched.group(1)):]
        
        # divide concatenated line to lines array
        return [line + '\n' for line in concatinated_line.splitlines()]

def insert(lines, params):
        # MESSAGE EXAMPLE: "NN:NN: error: expected expression before ‘}’ token"
        # Note: for missing left curly brackets {
        # XXX: Couldn't handle the missing left curly for structure declaration

        # the pattern means that is the missing left curly for non-function definition
        ## the parentheses for capture group ('(' and ')') are set that "matched.start() + len(matched.group(1))" enables to point the position to be inserted 
        return __insert_lcurly(lines, params, '([{};]\s*\n\s+\w+\s*\([^\)]*\))\s*[^(\{\s;)]+')

def insert_for_function_def(lines, params):
        # MESSAGE EXAMPLE: "NN: error: expected ‘{’ at end of input"
        # Note: for missing left curly brackets {
        # XXX: Couldn't handle the missing left curly for structure declaration

        # the pattern means that is the missing left curly for function definition
        ## the parentheses for capture group ('(' and ')') are set that "matched.start() + len(matched.group(1))" enables to point the position to be inserted 
        return __insert_lcurly(lines, params, '(\w*\s+\w+\s*\([^\)]*\))\s*[^(\{\s;)]+')

