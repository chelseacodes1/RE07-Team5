#-----------------------------------------------------------------------------
# Import
#-----------------------------------------------------------------------------
import sys
from sql import SQLDatabase

# bottle related import
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

#-----------------------------------------------------------------------------
# Config macro
#-----------------------------------------------------------------------------
import config
host = config.host
port = config.port
debug = config.port
app = config.app # used in the gevent server, this will be called in controller as well

#-----------------------------------------------------------------------------
# You may eventually wish to put these in their own directories and then load 
# Each file separately

# For the template, we will keep them together

import model
import view
import controller

#-----------------------------------------------------------------------------
# Main Methods
#-----------------------------------------------------------------------------

def run_server():    
    sql_db = SQLDatabase("database.db")
    sql_db.all_set_offline()
    server = WSGIServer(
        ("localhost", 8081), 
        app, 
        certfile="../certs/info2222.test.crt", 
        keyfile="../certs/info2222.test.key",
        handler_class=WebSocketHandler 
        )
    server.serve_forever()

#-----------------------------------------------------------------------------

# What commands can be run with this python file
# Add your own here as you see fit

command_list = {
    'server' : run_server
}

# The default command if none other is given
default_command = 'server'

def run_commands(args):
    '''
        run_commands
        Parses arguments as commands and runs them if they match the command list

        :: args :: Command line arguments passed to this function
    '''
    commands = args[1:]

    # Default command
    if len(commands) == 0:
        commands = [default_command]

    for command in commands:
        if command in command_list:
            command_list[command]()
        else:
            print("Command '{command}' not found".format(command=command))

#-----------------------------------------------------------------------------
# Run
#-----------------------------------------------------------------------------

run_commands(sys.argv)