from plugin.utils import *

import re

def replace(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: warning: format ‘%d’ expects argument of type ‘int’, but argument 2 has type ‘double’

        def __skip_pos_to_insert(lines, params, cols):
                # skip index to the double-quote character (points end of string)
                while lines[int(params[0]) - 1][cols] != '"':
                        cols += 1
                commas = int(params[4]) - 1

                # skip to adequate argument of function call
                for i in range(commas):
                        cols += 1
                        while lines[int(params[0]) - 1][cols] != ',':
                                cols += 1
                return cols

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        if re.search('\(\*\)\([\w,\s,\*]*\)', params[5]):
                # maybe a mistake in argument parameter (the parameter maybe function name)

                if params[3] in ['char *']:
                        param_str = "\"XX\""
                elif '*' in params[3]:
                        # could not make parameters with pointers
                        param_str = "NULL"
                elif params[3] in ['int', 'short', 'long']:
                        param_str = "0"
                elif params[3] in ['double', 'float']:
                        param_str = "0.0"
                elif params[3] in ['char']:
                        param_str = "'X'"

                # retrieve the position to insert                
                cols = __skip_pos_to_insert(lines, params, cols)
                
                # a character located at cols maybe comma, so increment the cols variable
                cols += 1
                str_start = cols

                # retrieve end position of the function argument
                while lines[int(params[0]) - 1][cols] != ',' and lines[int(params[0]) - 1][cols] != ')':
                        cols += 1

                # add string for parameter
                lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:str_start] \
                                        + param_str \
                                        + lines[int(params[0]) - 1][cols:]

        elif (('*' in params[3]) and ('*' in params[5])) or not (('*' in params[3]) or ('*' in params[5])):
                # maybe a mistake in conversion identifier 
                conv = ""

                if params[5] in ['double', 'float']:
                        conv = "%f"
                elif params[5] in ['double *', 'float *']:
                        conv = "%lf"
                elif params[5] in ['int', 'short', 'int *', 'short *']:
                        conv = "%d"
                elif params[5] in ['char']:
                        conv = "%c"
                elif params[5] in ['char *']:
                        conv = "%s"

                lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - len(params[2])] \
                                        + conv \
                                        + lines[int(params[0]) - 1][cols:]
        else:
                # maybe a mistake in argument parameter (the parameter maybe with mismatch type)
                
                # retrieve the position to insert                
                cols = __skip_pos_to_insert(lines, params, cols)
                
                if re.search('^\s*\&', lines[int(params[0]) - 1][cols + 1:]) != None:
                        # already '&' character is existed -> remove '&' character
                        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols + 1] \
                                                + re.sub('^\s*\&', '', lines[int(params[0]) - 1][cols + 1:]) 
                else:
                        # add '&' character (means address) for parameter
                        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols + 1] \
                                                + "&" \
                                                + lines[int(params[0]) - 1][cols + 1:]
        return lines

def add_args(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: warning: format ‘%d’ expects a matching ‘int’ argument

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        ## add lack of a parameter

        # skip index to the double-quote character (points end of string)
        while lines[int(params[0]) - 1][cols] != '"':
                cols += 1
        
        # skip to end position of arguments of function call
        while cols < len(lines[int(params[0]) - 1]) and re.search('\)\s*;', lines[int(params[0]) - 1][cols:]) != None:
                cols += 1

        # parameters to add        
        if params[3] in ['double', 'float']:
                val = "0.0"
        elif params[3] in ['int', 'short']:
                val = "0"
        elif params[3] in ['char']:
                val = "'X'"
        elif params[3] in ['char *']:
                val = "\"XX\""

        # add a parameter
        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cols - 1] \
                                + "," + val \
                                + lines[int(params[0]) - 1][cols - 1:]
        
        return lines

def remove_args(lines, params):
        #  MESSAGE EXAMPLE: "NN:NN: warning: format ‘%d’ expects a matching ‘int’ argument

        # correct column number which includes Zenkaku characters
        cols = correct_cols(lines[int(params[0]) - 1], int(params[1]))

        ## remove too many arguments

        str_start = cols
        # skip index to the double-quote character (points end of string)
        while lines[int(params[0]) - 1][cols] != '"':
                cols += 1
        
        # count number of args from double-quoted string
        num_args = len(re.findall('%[^%]+', lines[int(params[0]) - 1][str_start:cols]))

        # skip to start posiotion of unnecessary argument
        for i in range(num_args + 1):
                cols += 1
                while lines[int(params[0]) - 1][cols] != ',':
                        cols += 1

        # start position to cut
        cut_start = cols
        
        # skip to end position of arguments of function call
        while cols < len(lines[int(params[0]) - 1]) and re.search('\)\s*;', lines[int(params[0]) - 1][cols:]) != None:
                cols += 1

        # add a parameter
        lines[int(params[0]) - 1] = lines[int(params[0]) - 1][:cut_start] \
                                + lines[int(params[0]) - 1][cols - 1:]
        return lines
