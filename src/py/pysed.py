# Author: William Clark
# Python version: 3.8+
# TLDR: A regular expression runner you can can use from the command line
# Why Should I use this? 
"""
    * Sed is old and annoying syntax wise
    * Python is great
""" 
# Changelog
"""
    * Created 9/9/20
"""
# Frantic Scribbling on the Wall
"""
    The use case on this got kinda fuzzy. The idea was to have a utility to run half a dozen
    regex that need to be run against a file to clean it with a single VSC code command.
    That said, writing the task is potentially more effort than it's worth, and this is not
    too differnt from sed. 
"""
import re
import argparse
import os

class Pysed(object):

    def __init__(self, arguments):
        """
        Initializes off of command line arguments. The arguments are defined under the class, just before Main. 
        Argparse could make Pattern manditory by making it a positional arg, HOWEVER it's left as an actually
        manditory optional arg so that it's easier to write up clean arg blocks. It also reads better if 
        pattern comes before sub, which wouldn't be possible if the pattern was a positional. 
        
        Takes file input over command line input. Any argument passed that's not prefixed with a flag gets used
        as the input string to run the pattern over. 
        """
        self.parsed_args = {}
        
        if arguments.pattern:
            self.pattern = arguments.pattern
        else:
            raise Exception("FATAL: Regex cannot be performed without a regex pattern, use the -p flag.")
        
        if arguments.substitute:
            self.substitute = arguments.substitute

        self.line_numbers = arguments.linenumbers
            
        if arguments.file and arguments.text:
            print("WARN: Both -f and command line text provided, taking file by default.")
            if not os.path.isfile(arguments.file):
                raise Exception("FATAL: file argument not a valid path.")
            self.file = arguments.file
        elif arguments.text:
            self.text = ' '.join(arguments.text)
        elif arguments.file:
            if not os.path.isfile(arguments.file):
                raise Exception("FATAL: file argument not a valid path.")
            self.file = arguments.file
        else:
            raise Exception("FATAL: Need text to search through, use -f or -t")
            
        
    def infer(self):
        """
        Does the actual regex work. The usecases are as follows:
        * Pattern with No Group, No Subsitute
            Searches the input data for matches. This ONLY shows lines containing the pattern,
            it's a SEARCH operation that filters out non matching data.
            If line_numbers was set in the arguments, each line is prefixed with it's line number.
        * Pattern with Group, no Subsitute
            Searches the input data for matches. This ONLY shows THE GROUPS from lines containing 
            the pattern, it's a SEARCH operation that filters out non matching data. 
            If line_numbers was set in the arguments, each line is prefixed with it's line number.
        * Pattern with Group and Subsitute
            Returns ALL the lines from the input, including those WITHOUT MATCHES. Every Match
            is replaced with the subsitution provided. This is intended to be used for data cleaning,
            not searching.
        """
        return_lines = []
        if hasattr(self, 'text'):
            input_lines = [self.text]
            line_joiner = '\n'
        else:
            input_lines = open(self.file).readlines()
            line_joiner = '\n'
        
        for line, line_no in zip(input_lines, range(1, len(input_lines)+1)):
            if hasattr(self, 'substitute'):
                return_lines.append(re.sub(self.pattern, self.substitute, line.strip()))
                # IS running on all lines
                # should only run if sub works
                # fix later
            else:
                match = re.search(self.pattern, line)
                if match:
                    if match.groups():
                        return_lines.append(''.join(match.groups()))
                    else:
                        if self.line_numbers: return_lines.append(f'{line_no}: {line.strip()}')
                        else: return_lines.append(line.strip())
        if return_lines: 
            print(line_joiner.join(return_lines))
        return 0

def unit_tests():
    """Text Matches Unit Tests"""
    
    # # No match, nothing prints.
    argv =  [
                "--pattern", "c\w+",
                # "--substitute", "",
                "i like dogs",
                # "--file", ""
            ]
    args = parser.parse_args(argv)
    print(args)
    Pysed(args).infer()
    print('-------------------------')
    
    # # Match, no substitute or group, prints whole line with line number.
    argv =  [
                "--pattern", "c\w+",
                # "--substitute", "",
                "i like cats",
                # "--file", ""
                "--linenumbers",
            ]
    args = parser.parse_args(argv)
    Pysed(args).infer()
    print('-------------------------')

    # # Match, no substitute or group, prints whole line
    argv =  [
                "--pattern", "c\w+",
                # "--substitute", "",
                "i like cats",
                # "--file", ""
                # "--linenumbers",
            ]
    args = parser.parse_args(argv)
    Pysed(args).infer()
    print('-------------------------')
    
    # # Match, no substitute with group, returns group
    argv =  [
                "--pattern", "(\w+) (c\w+)",
                # "--substitute", "",
                "i like cats",
                # "--file", ""
            ]
    args = parser.parse_args(argv)
    Pysed(args).infer()
    print('-------------------------')
    
    # Match, substitute, returns replacement
    argv =  [
                "--pattern", "\w+ (c\w+)",
                "--substitute", "love \g<1> and Dogs",
                "i like cats",
                # "--file", ""
            ]    
    args = parser.parse_args(argv)
    Pysed(args).infer()
    print('-------------------------')
    
    """File Matches Unit Tests"""
    
    # # No match, nothing prints.
    argv =  [
                "--pattern", "^ERROR",
                # "--substitute", "",
                # "i like dogs",
                "--file", "../../tests/regexsample.log",
            ]
    args = parser.parse_args(argv)
    Pysed(args).infer()
    print('-------------------------')
    
    # Match, no substitute or group, prints whole line with line number.
    argv =  [
                "--pattern", "^WARNING",
                # "--substitute", "",
                # "i like cats",
                "--file", "../../tests/regexsample.log",
                "--linenumbers",
            ]
    args = parser.parse_args(argv)
    Pysed(args).infer()
    print('-------------------------')

    # Match, no substitute or group, prints whole line
    argv =  [
                "--pattern", "^WARNING",
                # "--substitute", "",
                # "i like cats",
                "--file", "../../tests/regexsample.log",
                # "--linenumbers",
            ]
    args = parser.parse_args(argv)
    Pysed(args).infer()
    print('-------------------------')
    
    # Match, no substitute with group, returns group
    argv =  [
                "--pattern", "^WARNING: (.*)",
                # "--substitute", "",
                # "i like cats",
                "--file", "../../tests/regexsample.log"
            ]
    args = parser.parse_args(argv)
    Pysed(args).infer()
    print('-------------------------')
    
    # Match, substitute, returns replacement
    argv =  [
                "--pattern", "^WARNING: (.*)",
                "--substitute", "THIS IS IMPORTANT: \g<1>",
                # "i like cats",
                "--file", "../../tests/regexsample.log"
            ]
    args = parser.parse_args(argv)
    Pysed(args).infer()
    print('-------------------------')

"""
Arguments for the Pysed class initialization. 
Pattern is REQUIRED, not optional
Anything provided on the command line that doesn't have a flag is treated as text input
Quotes are recommended around pretty much every input, given regex uses many special characters.
"""
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--pattern', help="Regex Pattern to search for")
parser.add_argument('-s', '--substitute', help="Matches will be replaced with this.")
parser.add_argument('text', nargs='*', help="text string to search in")
parser.add_argument('-f', '--file', help="file to be read as the text to search in")
parser.add_argument('-l', '--linenumbers', action='store_true', help='Prints line numbers when searching with no groups.')

# unit_tests()
args= parser.parse_args()
Pysed(args).infer()