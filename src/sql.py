from re import I, S, U
import sqlite3

class SQLDatabase():

    # Get the database running
    def __init__(self, database_arg=":memory:"):
        self.con = sqlite3.connect(database_arg)
        self.cur = self.con.cursor()
    
    def execute(self, query):
        self.cur.execute(query)

    def commit(self):
        self.con.commit()

    def close(self):
        self.cur.close()

    #-----------------------------------------------------------------------------
    
    # Sets up the database
    # Default admin password
    def database_setup(self):

        # Clear the database if needed
        self.cur.execute("DROP TABLE IF EXISTS Users")
        self.cur.execute("DROP TABLE IF EXISTS Messages")
        self.commit()

        # Create the users table
        self.cur.execute("""CREATE TABLE Users(
            username TEXT,
            password TEXT,
            salt TEXT,
            public_key TEXT,
            state INTEGET DEFAULT 0,
            friends TEXT,
            admin INTEGER DEFAULT 0
        )""")

        # iv is needed for symmetric encryption; it alse works as the id of a message
        # the chance that two messages have the same sender, recevier and iv is very small
        self.cur.execute("""CREATE TABLE Messages(
            sender TEXT,
            receiver TEXT,
            encrypted_sk TEXT,
            encrypted_message TEXT,
            iv TEXT,
            signature TEXT
        )""")

        self.commit()
        return

    #-----------------------------------------------------------------------------
    # User handling
    #-----------------------------------------------------------------------------

    # Add a user to the database
    def add_user(self, username, password, salt, public_key, state=0, admin=0):
        sql_cmd = """
                INSERT INTO Users
                VALUES('{username}', '{password}', '{salt}', '{public_key}', {state}, "", {admin})
            """
        sql_cmd = sql_cmd.format(username=username, password=password, salt=salt, public_key=public_key, state=state, admin=admin)

        self.cur.execute(sql_cmd)
        self.commit()
        return True

    #-----------------------------------------------------------------------------
    
    def check_exist(self, username):
        sql_query = """
                SELECT 1
                FROM Users
                WHERE username = '{username}'
            """
        sql_query = sql_query.format(username=username)

        self.cur.execute(sql_query)

        if self.cur.fetchone():
            return True
        else: 
            return False

    #-----------------------------------------------------------------------------

    # Check login credentials
    def check_credentials(self, username, password):
        sql_query = """
                SELECT 1 
                FROM Users
                WHERE username = '{username}' AND password = '{password}'
            """

        sql_query = sql_query.format(username=username, password=password)
        self.cur.execute(sql_query)

        # If our query returns
        if self.cur.fetchone():
            return True
        else:
            return False

    #-----------------------------------------------------------------------------
    
    def check_online(self, username):
        sql_query = """
                SELECT 1
                FROM Users
                WHERE username = '{username}' AND state = 1
            """
        sql_query = sql_query.format(username=username)
        self.cur.execute(sql_query)
        if self.cur.fetchone():
            return True
        else:
            return False
    
    def give_salt(self, username):
        sql_query = """
                SELECT salt
                FROM Users
                WHERE username = '{username}'
            """
        sql_query = sql_query.format(username=username)
        self.cur.execute(sql_query)
        salt = self.cur.fetchone()

        if salt:
            return salt
        else:
            return None
     
    def set_online(self, username):
        sql_query = """
                UPDATE  Users
                SET state = 1
                WHERE username = '{username}'
            """
        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        self.commit()
        return
   
    def set_offline(self, username):
        sql_query = """
                UPDATE  Users
                SET state = 0
                WHERE username = '{username}'
            """
        sql_query = sql_query.format(username=username)
        self.execute(sql_query)
        self.commit()
        return

    def all_set_offline(self):
        sql_query = """
                UPDATE  Users
                SET state = 0
            """
        self.execute(sql_query)
        self.commit()
        return
    
    def add_friend(self, username, friendname):
        # Get friends list
        friends = friendname

        # Add to friend list
        sql_query = """
                UPDATE Users
                SET friends = '{friends}'
                WHERE username = '{username}'
            """
        sql_query = sql_query.format(friends=friends, username=username)
        self.cur.execute(sql_query)
        self.commit()
        return
    
    def give_friends(self, username):
        sql_query = """
                SELECT friends FROM Users
                WHERE username = '{username}'
            """
        sql_query = sql_query.format(username=username)
        self.cur.execute(sql_query)
        friends = self.cur.fetchone()
        if friends:
            return friends
        else:
            return None
    
#-----------------------------------------------------------------------------
# Message
#-----------------------------------------------------------------------------

    def add_message(self, sender, receiver, sk, msg, iv, sig):
        sql_cmd = """
                INSERT INTO Messages
                VALUES('{sender}', '{receiver}', '{sk}', '{msg}', '{iv}', '{sig}')
            """
        sql_cmd = sql_cmd.format(sender=sender, receiver=receiver, sk=sk, msg=msg, iv=iv, sig=sig)
        self.cur.execute(sql_cmd)
        self.commit()
        return
    
    # Return one message with the same sender and receiver when called every time
    def get_message(self, sender, receiver):
        sql_query = """
                SELECT * FROM Messages
                WHERE sender = '{sender}' and receiver = '{receiver}'
            """
        sql_query = sql_query.format(sender=sender, receiver=receiver)
        self.cur.execute(sql_query)
        self.con.row_factory = sqlite3.Row
        message = self.cur.fetchone()
        return message
    
    def delete_message(self, sender, receiver, iv):
        sql_query = """
                DELETE FROM Messages
                WHERE sender = '{sender}' and receiver = '{receiver}' and iv = '{iv}'
            """
        sql_query = sql_query.format(sender=sender, receiver=receiver, iv=iv)
        self.cur.execute(sql_query)
        self.commit()
        return

    def give_public_key(self, username):
        sql_query = """
                SELECT public_key
                FROM Users
                WHERE username = '{username}'
            """
        sql_query = sql_query.format(username=username)
        self.cur.execute(sql_query)
        pk = self.cur.fetchone()

        if pk:
            return pk
        else:
            return None