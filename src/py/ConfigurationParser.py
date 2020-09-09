# Author: William Clark
# Python version: 3.8+
# TLDR: An object that loads your configuration JSON or Environment variables as a Python Dictionary
# Why Should I use this? 
#       You can write consistent Configuration files that can be shared cross project.
#       You will also have validation available for DB2 and Database DSNs
#       You will have, after creating the object and parsing, a python dictionary will all your credentials.
# Changelog
#       * 9/1/20 - Created. 
# Frantic Scribbling on the Wall
# The magical issue of 'I want a logger, but to get a logger I need to use the parser to get the log_path'
#       I fixed that bitch with a backlog and dynamic log method BOOM
# TODO: Shift "PrePath Logging" into a stand alone, implement in logger. Basically a wrapper around a real logger?

import os
import json
# from py_base import py_base_log as logging
# import py_base_log as logging
import logging
import re

class ConfigParser(dict):
    
    def __init__(self, clean=True):
        """ An extension of the python dictionary class with methods to load and validate data loaded 
        from different sources. This is the base class for each different data source, called ConfigParser. 
        
        The clean parameter controls if the keys/values are cleaned via the _clean_inputs function found in this class
        before the parser inserts them into the ConfigParser internal dictionary. See the function for more detail on
        what cleaning is done.
        
        self.logger and backlog are used for logging, ConfigParser uses a methodology that logs to the console up until
        it reads a `configparserlogpath` value into itself. The path provided in that variable is where a proper
        log is created. Logging can either use the base logging configuration, or py_base's custom logger. Which is
        imported is detected when the log file is created. All things logged before the logpath is loaded and therefore,
        the log file can be created, are logged when the log file is made. Additionally, console logging will take place
        before a log file is created for debugging purposes. 
        
        elseget is used by the validation functions; it represents the value to place into the dsn's if the value is not found.
        """
        self.clean = clean
        self.logger = None
        self.backlog = []
        self.elseget = ''
        
    def parse(self):
        """ Primary method to be defined in Implementations. Loads the data from a data source into this object.
        """
        pass
    
    def parse_flask(self, *args, **kwargs):
        self.parse(*args, **kwargs)
        
        return self
    
    def parse_db2(self, *args, **kwargs):
        """
        Neat little trick that calls the parse method of the implementing class with whatever 
        arguments are given to this function. This method is a shortcut to parse then immediately
        validate the parsed values via the validate_db2 function. 
        """
        self.parse(*args, **kwargs)
        self.validate_db2()
        
        return self
    
    def parse_database(self, *args, **kwargs):
        """
        Neat little trick that calls the parse method of the implementing class with whatever 
        arguments are given to this function. This method is a shortcut to parse then immediately
        validate the parsed values via the validate_database function. 
        """
        self.parse(*args, **kwargs)
        self.validate_database()
        
        return self
    
    def validate_db2(self):
        """
        Method that validates the values contained with in this object will allow for the creation
        of a valid DSN for a DB2 connection. Expects particular names in the source data, so 
        one should fill in the blanks in one of the sample_credentials files in the instance folder
        rather than create their own config. A DSN can be formed without this, but this standardizes
        the configuration file as well as the code. 
        """
        required = set(["database", "host", "username", "password", "port"])
        optional = set(["dialect", "driver", "protocol", "security", "sslcertificate", "sslclientkeystore", "sslclientstash"])
        
        keys = set(self.keys())
        # Check if all the required keys are found in the loaded parse. 
        # (Uses subset notation, required is subset of self.keys())
        # Also viable, required - set is empty
        if not required <= keys:
            self.log(f"Required keys {required - keys} not found, will not be able to connect to DB2.", "error")
            raise Exception(f"Required keys {required - keys} not found, will not be able to connect to DB2.")
        if not optional <= keys:
            self.log(f"Optional keys {optional - keys} not found.", "warn")
        
        dsn = f"Driver={self.get('driver', self.elseget)if self.get('driver') else '{IBM DB2 ODBC Driver}'}"
        dsn += f";DATABASE={self.get('database', self.elseget)}"
        dsn += f";HOSTNAME={self.get('host', self.elseget)}"
        dsn += f";PORT={self.get('port', self.elseget)}"
        dsn += f";UID={self.get('username', self.elseget)}"
        dsn += f";PWD={self.get('password', self.elseget)}"
        if self.get('protocol'):
            dsn += f";PROTOCOL={self.get('protocol', self.elseget)}"
        if self.get('security'):
            dsn += f";SECURITY={self.get('security', self.elseget)}" 
        if self.get('sslcertificate'):
            dsn += f";SSLSERVERCERTIFICATE={self.get('sslcertificate', self.elseget)}" 
        if self.get('sslclientkeystore'):
            dsn += f";SSLCLIENTKEYSTOREDB={self.get('sslclientkeystore', self.elseget)}" 
        if self.get('sslclientstash'):
            dsn += f";SSLCLIENTKEYSTASH={self.get('sslclientstash', self.elseget)}"
        
        self['db2dsn'] = dsn

        return self
    
    def validate_database(self):
        """
        Method that validates the values contained with in this object will allow for the creation
        of a valid DSN for a Database connection. Expects particular names in the source data, so 
        one should fill in the blanks in one of the sample_credentials files in the instance folder
        rather than create their own config. A DSN can be formed without this, but this standardizes
        the configuration file as well as the code. 
        """
        required = set(["dialect", "database", "host", "username", "password", "port"])
        optional = set(["driver", "protocol", "security", "sslcertificate", "sslclientkeystore", "sslclientstash"])
        
        keys = set(self.keys())
        # Check if all the required keys are found in the loaded parse. 
        # (Uses subset notation, required is subset of self.keys())
        # Also viable, required - set is empty
        if not required <= keys:
            self.log(f"Required keys {required - keys} not found, will not be able to connect to DB2.", "error")
            raise Exception(f"Required keys {required - keys} not found, will not be able to connect to DB2.")
        if not optional <= keys:
            self.log(f"Optional keys {optional - keys} not found.", "debug")
        
        dsn = f"{self.get('dialect', self.elseget) if self.get('dialect') else 'db2'}"
        dsn += f"{self.get('driver', self.elseget)}"
        dsn += f"://{self.get('username', self.elseget)}"
        dsn += f":{self.get('password', self.elseget)}"
        dsn += f"@{self.get('host', self.elseget)}"
        dsn += f":{self.get('port', self.elseget)}"
        dsn += f"/{self.get('database', self.elseget)}"
        if self.get('protocol'):
            dsn += f";PROTOCOL={self.get('protocol', self.elseget)}"
        if self.get('security'):
            dsn += f";SECURITY={self.get('security', self.elseget)}" 
        if self.get('sslcertificate'):
            dsn += f";SSLSERVERCERTIFICATE={self.get('sslcertificate', self.elseget)}" 
        if self.get('sslclientkeystore'):
            dsn += f";SSLCLIENTKEYSTOREDB={self.get('sslclientkeystore', self.elseget)}" 
        if self.get('sslclientstash'):
            dsn += f";SSLCLIENTKEYSTASH={self.get('sslclientstash', self.elseget)}"
        
        self['dsn'] = dsn

        return self
    
    def _clean_inputs(self, key, value):
        """
        Cleans the key and value pairs before inserting them into the ConfigParser dictionary.
        Current does the following steps:
        * lower case both key and value
        * strip both key and value
        * log a warning whenever an empty string/None is found as a value
        """
        key = key.lower().strip()
        if value == '' or value == None:
            self.log(f"Key {key} has an empty value.", "warning")
        elif type(value) == str:
            value = value.lower().strip()
        
        return key, value
    
    def log(self, message, level='warn'):
        """
        Function to facilitate logging before an actual log file location has been created. 
        If a log file has already been made (self.logger), logging is straight forward a la the logging 
        module. Only exceptions, info, error, and warning levels are logged at this time. 
        
        If a log file has yet to have been created, the parser checks if the logging path has been loaded
        into itself yet. This path MUST be called the `configparserlogpath`. This path is then used to 
        create either a standard python logger or a logging object customized via py_base. Whichever package
        is imported as logging will determine which is used. 
        
        Once a log file has been created all messages stored in the backlog (next section) are logged, then
        the message that was passed into this call of the log function is logged. 
        
        If no log file exists and the path is not in this object, logging is done via print statements. The
        prints are prepended with the level of log. The message and log level are also stored in the backlog,
        which once a log file has been created, will be logged into the log file proper. 
        """
        if self.logger: # Log was already created. 
            if level == 'exception':
                # Message would have to be a tuple; exception logs demand a exc_info keyword value.
                # Use Error unless you actually want an exception trace. 
                self.logger.exception(message[0], exc_info=message[1])
            elif level == 'info': 
                self.logger.info(message)
            elif level == 'error':
                self.logger.error(message)
            elif level == 'warn' or level == 'warning':
                self.logger.warning(message)
        else: # Logging hasn't been created yet. 
            if 'configparserlogpath' in self: # if you have a path to use
                
                os.makedirs(self['configparserlogpath'], exist_ok=True)
                if 'py_base' in logging.__file__: # Custom Logging
                    self.logger = logging.createLog('ConfigParser', self['configparserlogpath'])
                else: # Default Logging Package
                    logging.basicConfig(filename=os.path.join(self['configparserlogpath'], 'ConfigParser.basic.log'), level=logging.NOTSET)
                    self.logger = logging
                
                # Run all printed messages through the logger
                # TODO: Get this to not print the already printed messages (via print). Might be hard. 
                for x in self.backlog:
                    self.log(x[0], x[1])
                
                self.log(message, level)
            else: # No path, no log, you get prints. 
                self.backlog.append((message, level))
                if level == 'exception':
                    print('EXCEPTION: '+message)
                elif level == 'info': 
                    print('INFO: '+message)
                elif level == 'error':
                    print('ERROR: '+message)
                elif level == 'warn' or level == 'warning':
                    print('WARNING: '+message)

class JsonConfigParser(ConfigParser):
    
    """
    Implements loading a JSON configuration file. All functions other than Parser are inherited from
    the super class ConfigParser above. An example of the configuration file used to develop this
    class can be found in ../../tests/sample_credentials.json. 
    """
        
    def parse(self, json_file, sub_keys=[]):
        """
        Loads a json file, throwing errors if the json file is not found or it was not able to be 
        parsed as json via the json module, and imports the selected values into this object.
        
        Json_file should be a path to the json you wish to load. 
        
        sub_keys is a list of keys to traverse down the JSON's 'tree' before loading in all values. 
        in the case of an object like below, one can specify sub_keys=['bar'] to load the dictionary
        under the bar key into the object (ignoring the top level foo=bar), or sub_keys=['bar', 'baz']
        to load only the dictionary under 'baz'. 
            "foo":"bar",
            "bar": 
            {
                "foo": "baz",
                "baz":
                {
                    "foo": "foo"
                }
            }  
        Examples of this can be seen in the "Json Parse Test" of the unit tests.
        
        Key value pairs are only cleaned before insertion if the class variable `clean` is set to true.
        """
        if not os.path.isfile(json_file):
            self.log(f"Path {json_file} not found", "error")
            raise Exception(f"Path {json_file} not found")
        try:
            json_data = json.loads(open(json_file).read())
        except:
            self.log(f"File at {json_file} was unable to be read as JSON.", "error")
            raise Exception(f"File at {json_file} was unable to be read as JSON.")
        
        if sub_keys: # Navigate down the JSON 'tree' to a specific key. Can go multiple layers down. 
            if type(sub_keys) is str: sub_keys = [sub_keys]
            for k in sub_keys:
                if k not in json_data.keys():
                    self.log(f"Sub key {k} not found from sub key list f{sub_keys}", "error")
                    raise Exception(f"Sub key {k} not found from sub key list {sub_keys}")
                json_data = json_data[k]
        
        # Add all data from the JSON to this object.
        for x, y in json_data.items():
            if self.clean:
                x_clean, y_clean = self._clean_inputs(x,y)
                self[x_clean] = y_clean
            else:
                self[x] = y
            
        return self
        
class EnvConfigParser(ConfigParser):
        
    """
    Implements loading from the os environment variables. All functions other than Parser are inherited from
    the super class ConfigParser above. An example of the source file of variables used to develop this
    class can be found in ../../tests/sample_credentials.sh. 
    
    The environment variables are filtered through using a prefix or straight regex. 
    """
        
    def parse(self, env_prefix, regex=False, trim=False):
        """
        The parse function operates differently based on if regex is True or False. When False, 
        the env_prefix is a prefix value that must be matched by an environment variable for it to
        be added to this object's internal dictionary. For example, with a prefix of 'foo', 'foobar'
        would be added to the dictionary and barfoo would not. When True, the env_prefix is used as
        a complete regex (using re.match) against each environment variable. 
        
        Cleaning is preformed via the _clean method on matches only if the clean class variable is True.
        
        The trim flag is used to REMOVE all parts of the KEY that aren't part of a single capture group
        in the regex. When the regex flag is False, this means that the prefix will be dropped when the
        key is inserted. Example, 'foo' as the prefix would match 'foobar', but the dictionary will 
        contain 'bar' instead of 'foobar'. 
        
        When regex is true and using trim, you'll need a specific NAMED REGEX GROUP in your pattern, 
        `(?P<var>...)`. The triple dots can be replaced with however you want to match the variable name, 
        but it must be referred to in this manner for trim to work. 
        
        Trim functionality is set to False when parsing by default. It is recommended to be used when
        using the parse_db2 or parse_database expansions on the parse method, as `username` and `database` are
        fairly amigious names compared to `prod_db2_ny_database`. 
        
        Finally, parse will produce an error BUT NOT CRASH when no matches were found for the provided pattern. 
        """
        
        
        envs = os.environ
        pattern = f'{env_prefix}(?P<var>.*)' if not regex else env_prefix

        if trim and not re.search('\(?P<var>.*?\)', pattern):
            self.log(f"regex `(?P<var>...)` not found in your pattern `{pattern}`, will not be able to trim.", "error")
            raise Exception(f"regex `(?P<var>...)` not found in your pattern `{pattern}`, will not be able to trim.")
        
        matches = 0
        for x, y in envs.items():
            match = re.match(pattern, x)
            if match:
                if self.clean:
                    if trim:
                        x = match.group('var')
                    x_clean, y_clean = self._clean_inputs(x,y)
                    self[x_clean] = y_clean
                else:
                    self[x] = y
                matches+=1
        if matches == 0:
            self.log(f"There were no matches found for pattern '{pattern}'", "error")
        return self
        

def unit_tests():
    """Unit testing. Comment out sections if you want to be able to follow along"""
    
    """Dictionary Feature Test"""
    p = ConfigParser()
    p['foo'] = 'bar'
    print('foo' in p)
    print(p['foo'])
    print(p.get('bar'))
    p.update({'foo':'baz', 'bar':'foo'})
    print(p.items())
    
    
    
    """JSON Parse Test"""
    try: 
        print(JsonConfigParser().parse('test2.json'))
    except Exception as e:
        print(e)
    try: 
        print(JsonConfigParser().parse('logger.py'))
    except Exception as e:
        print(e)
    print(JsonConfigParser().parse('../../tests/test.json'))
    print(JsonConfigParser().parse('../../tests/test.json', ['bar']))
    print(JsonConfigParser().parse('../../tests/test.json', ['bar', 'baz']))
    
    
    
    """Db2/Database DDL JSON Parse"""
    print(JsonConfigParser().parse_db2('../../tests/sample_credentials.json', ['db2'])['db2dsn'])
    print(JsonConfigParser().parse_database('../../tests/sample_credentials.json', ['database'])['dsn'])
    
    
    
    """Env Parse Test"""
    try:
        print(EnvConfigParser().parse('tdd_(dev|prod)_(.*)', regex=True, trim=True))
    except Exception as e:
        print(e)
    print(EnvConfigParser().parse('tdd_dev_'))
    print(EnvConfigParser().parse('tdd_(dev|prod)_(?P<var>.*)', regex=True)) 
    """ WONTFIX: without Trim, the above command's (?P<var>...) group isn't technically necessary. 
        Nothing from the match is used without Trim, so as long as the regex matches, it will trigger fine. 
        In fact, you don't even need the .* at all. As long as the pattern matches from the start of the var name (we use re.match), the whole environment variable name gets kicked back. Case in point below. 
    """
    print(EnvConfigParser().parse('tdd_(dev|prod)_', regex=True)) 
    print(EnvConfigParser().parse('tdd_(dev|prod)_(?P<var>.*)', regex=True, trim=True))
    
    
    
    """Db2/Database DDL Env Parse"""
    print(EnvConfigParser().parse_db2('tdd_dev_db_', trim=True)['db2dsn'])
    print(EnvConfigParser().parse_database('tdd_dev_db_', trim=True)['dsn'])
    

if __name__ == '__main__':
    unit_tests()
    
    # # Usecase Sample
    # db2config = JsonConfigParser()
    # db2config.parse_db2('path/to/config.json', sub_keys=['dev'])
    # print(db2config['db2dsn'])