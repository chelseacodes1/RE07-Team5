'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from email import message
from re import S, U
from string import ascii_letters
from bottle import route, get, post, error, request, static_file, Bottle, abort
from django.dispatch import receiver
from geventwebsocket import WebSocketError
import config
from sql import SQLDatabase
app = config.app
import model

#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@app.route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow CSS
@app.route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')

#-----------------------------------------------------------------------------

# Allow javascript
@app.route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to login
@app.get('/')
@app.get('/home')
def get_index():
    return model.index()

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

# Display the login page
@app.get('/login')
def get_login_controller():
    return model.login_form()

#-----------------------------------------------------------------------------

# Attempt the login
@app.route('/login/websocket')
def login_handle_websocket():
    ws = request.environ.get("wsgi.websocket")
    if not ws:
        abort(400, 'Expected WebSocket request.')
    
    # Helper var
    user_exist = False

    # var to pass
    username = ""
    password = ""
    salt = ""

    message = ""
    while True:
        try:
            message = ws.receive()

            message_list = message.split(",")

            if message_list[0] == "username":
                username = message_list[1]
                if model.login_check_exist(username):
                    ws.send("1,user exists")
                else:
                    ws.send("0,User doesn't exists.")
                    username = ""
                    password = ""
                    salt = ""

            if message_list[0] == "?":
                if message_list[1] == "salt":
                    ws.send("1,username is %r" % username)
                    salt = model.login_give_salt(username) 
                    if salt:
                        salt_message = "1,salt," + salt[0]
                        ws.send(str(salt_message))
                    else:
                        ws.send("0,Error occurs when retriving salt.")
                        username = ""
                        password = ""
                        salt = ""

            if message_list[0] == "password":
                password = message_list[1]
                if model.login_check_credentials(username, password):
                    model.login_set_online(username)
                    ws.send("1,valid password")
                else:
                    ws.send("0,Wrong password.")
                    username = ""
                    password = ""
                    salt = ""
        except WebSocketError:
            break
    
    return


#-----------------------------------------------------------------------------
# Register
#-----------------------------------------------------------------------------

@app.route('/register/websocket')
def register_handle_websocket():
    ws = request.environ.get('wsgi.websocket')
    if not ws:
        abort(400, 'Expected WebSocket request.')
    
    # Helper var
    info_counter = 0
    public_key_send = False
    
    # var to pass
    username = ""
    password_1 = ""
    password_2 = ""
    salt = ""
    public_key = ""

    # Receive
    message = "" 
    while True:
        try:
            message = ws.receive()
            # ws.send("The message you sent was: %r" % message)

            # Process message received
            message_list = message.split(",")
            if (message_list[0] == "username"):
                username = message_list[1]
            elif (message_list[0] == "password_1"):
                password_1 = message_list[1]
            elif (message_list[0] == "password_2"):
                password_2 = message_list[1]
            elif (message_list[0] == "salt"):
                salt = message_list[1]
            elif (message_list[0] == "public_key"):
                public_key = message_list[1]
            
            # Logic
            if (username != "") and (password_1 != "") and (password_2 != "") and (salt != ""):
                # Check usrename
                user_exsit = model.register_check_if_exist(username)
                if user_exsit:
                    ws.send("User already exists. Please try another username.")
                    username = ""
                    password_1 = ""
                    password_2 = ""
                    salt = ""
                    public_key = ""

                # Check password
                if (password_1 != "") and (password_2 != "") and (username != ""):
                    if (password_1 != password_2):
                        ws.send(f"The passwords entered are different. Please re-enter.")
                        username = ""
                        password_1 = ""
                        password_2 = ""
                        salt = ""
                        public_key = ""
                    else:
                        if (public_key_send == False):
                            ws.send("Positive")
                            public_key_send = True
            else:
                info_counter += 1
                if (info_counter > 3):
                    ws.send("Please finish implementing information!")
                    info_counter = 0

            # Check public key, add user to database
            if (public_key != ""):
                model.register_add_user(username, password_1, salt, public_key)
                ws.send("Registeration successful!")
                username = ""
                password_1 = ""
                password_2 = ""
                salt = ""
                public_key = ""

        except WebSocketError:
            break

#-----------------------------------------------------------------------------

@app.get('/register')
def get_register_controller():
    return model.register_form()


#-----------------------------------------------------------------------------
# Chat
#-----------------------------------------------------------------------------

@app.get('/chat/<username:re:.+>')
def get_login_controller(username):
    if_online = model.check_if_online(username)
    if if_online:
        return model.chat_form()
    else:
        return model.chat_form_invalid() 

# @app.route('/chat/<username:re:.+>/websocket')
@app.route('/chat/websocket')
def chat_handle_websocket():
    ws = request.environ.get('wsgi.websocket')
    if not ws:
        abort(400, 'Expected WebSocket request.')
    
    # To receive
    send_sym = ""
    send_msg = ""
    send_iv = ""
    send_sig = ""

    # Receive
    while True:
        try:
            message = ws.receive()
            # ws.send("0,Server message received!")
            message_list = message.split(",")

            username = message_list[0]

            if message_list[1] == "?":
                if message_list[2] == "pk":
                    send_to = message_list[3]
                    pk = model.give_public_key(send_to)
                    if pk:
                        message_to_send = "1,target_info," + pk[0]
                        ws.send(message_to_send)

            if message_list[1] == "receive":
                sender = message_list[2]
                message_received = model.get_message(sender, username)
                if message_received:
                    message_received_header = "2," + sender + ","
                    recv_sym = message_received[2]
                    recv_msg = message_received[3]
                    recv_iv = message_received[4]
                    recv_sig = message_received[5]
                    ws.send(message_received_header + "sym," + recv_sym)
                    ws.send(message_received_header + "msg," + recv_msg)
                    ws.send(message_received_header + "iv," + recv_iv)
                    ws.send(message_received_header + "sig," + recv_sig)
            
            if message_list[1] == "message received":
                sender = message_list[2]
                ws.send("1,message deleted")
                model.delete_message(sender, username)

            if message_list[1] == "send":
                receiver = message_list[2]
                order = message_list[3]

                # In case "," in message
                value = ""
                for i in message_list[4:]:
                    value += i

                if order == "sym_key":
                    send_sym = value
                elif order == "msg":
                    send_msg = value
                elif order == "iv":
                    send_iv = value
                elif order == "sig":
                    send_sig = value
                
                if (send_sym != "") and (send_msg != "") and (send_iv != "") and (send_sig != ""):
                    model.add_message(username, receiver, send_sym, send_msg, send_iv, send_sig)
                    send_sym = ""
                    send_msg = ""
                    send_iv = ""
                    send_sig = ""
                

        except WebSocketError:
            break 


#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------


#-----------------------------------------------------------------------------
# Others
#-----------------------------------------------------------------------------

@app.get('/about')
def get_about():
    '''
        get_about
        
        Serves the about page
    '''
    return model.about()
#-----------------------------------------------------------------------------

# Help with debugging
@app.post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@app.error(404)
def error(error): 
    return model.handle_errors(error)
