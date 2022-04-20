'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
from calendar import firstweekday
from cgitb import reset
import re
from sqlite3 import SQLITE_DROP_TABLE, sqlite_version
import view
import random
from sql import SQLDatabase

# Initialise our views, all arguments are defaults for the template
page_view = view.View()

#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def index():
    '''
        index
        Returns the view for the index
    '''
    return page_view("index")

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view("login")

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    # By default assume good creds
    login = True
    
    if username != "admin": # Wrong Username
        err_str = "Incorrect Username"
        login = False
    
    if password != "password": # Wrong password
        err_str = "Incorrect Password"
        login = False
        
    if login: 
        return page_view("valid", name=username)
    else:
        return page_view("invalid", reason=err_str)

#-----------------------------------------------------------------------------

def login_give_salt(username):
    sql_db = SQLDatabase("database.db")
    result = sql_db.give_salt(username)
    sql_db.close()
    return result

def login_check_exist(username):
    sql_db = SQLDatabase("database.db")
    result = sql_db.check_exist(username)
    sql_db.close()
    return result

def login_check_credentials(username, password):
    sql_db = SQLDatabase("database.db")
    result = sql_db.check_credentials(username, password)
    sql_db.close()
    return result

def login_set_online(username):
    sql_db = SQLDatabase("database.db")
    sql_db.set_online(username)
    sql_db.close()
    return


#-----------------------------------------------------------------------------
# Register
#-----------------------------------------------------------------------------
def register_form():
    return page_view("register")

#-----------------------------------------------------------------------------

def register_check_if_exist(username):
    sql_db = SQLDatabase("database.db")
    result = sql_db.check_exist(username)
    sql_db.close()
    return result

#-----------------------------------------------------------------------------

def register_add_user(username, password, salt, public_key):
    sql_db = SQLDatabase("database.db")
    sql_db.add_user(username, password, salt, public_key, 0, 0)
    sql_db.close()
    return

#-----------------------------------------------------------------------------
# Chat
#-----------------------------------------------------------------------------
def chat_form():
    return page_view("chat")

def chat_form_invalid():
    return page_view("chat_invalid")

def check_if_online(username):
    sql_db = SQLDatabase("database.db")
    result = sql_db.check_online(username)
    sql_db.close()
    if result:
        return True
    else:
        return False

def give_friends(username):
    sql_db = SQLDatabase("database.db")
    friends = sql_db.give_friends(username)
    sql_db.close()
    return friends

def add_message(sender, receiver, pk, msg, iv, sig):
    sql_db = SQLDatabase("database.db")
    sql_db.add_message(sender, receiver, pk, msg, iv, sig)
    sql_db.close()
    return

def get_message(sender, receiver):
    sql_db = SQLDatabase("database.db")
    message = sql_db.get_message(sender, receiver)
    sql_db.close()
    return message

def delete_message(sender, receiver):
    sql_db = SQLDatabase("database.db")
    sql_db.delete_message(sender, receiver)
    sql_db.close()
    return

def give_public_key(username):
    sql_db = SQLDatabase("database.db")
    result = sql_db.give_public_key(username)
    sql_db.close()
    return result
#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("about", garble=about_garble())



# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.", 
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)