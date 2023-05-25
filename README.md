# cceg
C compiler with error message grouping

## Getting started
### Prerequisites
The cceg is executed on the Python 3.8.10 or later. It uses C compiler like CC or GCC. The execution was checked using GCC 9.4.0.

### How to run
To use this on the Linux, please execute following command:

```
% ./cceg target.c
```
or

```
% ./cceg.py target.c
```
or

```
% python3 cceg.py target.c
```
Note that the cceg above mentioned is the symlink for cceg.py.

### Sample usage
The sample file included (sample.c) is tiny example of incorrect program file. This sample file contains 5 grammatically errors as follows.  
- (Line:5) for [int i = 1; i <= 12; i++){ *[confusing parenthesis with square bracket]*
- (Line:8) printf("\n")  *[missing semi-colon]*
- (Line:10) *[missing return statement for non-void function]*
- (Line:14)  print_tt; *[missing empty parentheses for void argument]*
- (Line:15) ] *[confusing curly bracket with square bracket]*

Compiling this program using gcc with "-Wall" option, you can see the 12 error/warning messages caused by these 5  grammatically errors.  
If you use cceg with "-Wall" option instead of gcc (as follows), you will see the 12 messages in 5 error groups. The groups are each corresponded to the 5 grammatically errors.

```
% ./cceg -Wall sample.c
```


### Options
The options are listed to the console when "-h"/"--help" option is specified.

```
% ./cceg -h
usage: cceg [-h] [-o <file>] [-DEBUG] [-d] [-Wwarn...] file

C Compiler with Error message Grouping

positional arguments:
  file       Source file to compile

optional arguments:
  -h, --help   show this help message and exit
  -o <file>  Place the output into <file>.
  -DEBUG     Display debug messages
  -d         Display compile error messages (when -DEBUG is enabled)
  -Wwarn...  Warning options for compiler
```

#### -o \<file\>
File name of the output file of compilation.

#### -Wwarn
Warning options for compiler

The -o option and -W option are through to the compiler directly.

#### -DEBUG
Displays detailed messages to console.

#### -d
Displays each compile error message. This option is valid when the -DEBUG is enabled

### Configuration file
The configuration file is "opt/config.json".
Using this file, the user can configure the behaviour of cceg. Default configurations are follows:

```
{
  "rule_json"   : "opt/rule.json",
  "c_compiler"  : "gcc",
  "debug_mode"  : "False",
  "display_err" : "False"
}
```

The ***rule_json*** is the file name and path name for json file which contains if-then rules.  
The ***c_compiler*** is the command name for compilation (it sould be gcc or cc).  
The ***debug_mode*** is the flag. When this flag is True, the cceg prints processing details verbosely. If the **-DEBUG** command line option is set, the  *debug_mode* flag will be overwritten.  
The ***display_err*** is the flag. When this flag is True, the cceg prints compilation errors on each compilation time. This flag is only valid when *debug_mode* is True. If the **-d** command line option is set, the  *display_err* flag will be overwritten.  

## If-then rules
The default if-then rules to avoid compilation error is included in *opt/rule.json* (the name configured in *config.json*) file. The if-then rules uses specific logics to eliminate the errors, each logic is described as python program. The programs specified in then statement of the rules are located in *plugin* directory. The programs in *plugin* directory include the method which has specified name. The parameters of the method must be two variables as follows:

1. string array represents lines of targeted program list
2. array each element corresponds to the group in the regex pattern of if condition

Return value of the method must be string array of modified lines whose error represented by if condition is eliminated.

## Author
* **Masataka NAGURA** - *Initial work* - [nagura](https://github.com/nagura)

## Acknowledgements
* **Ryota KONDO** supported initial work in his school days.