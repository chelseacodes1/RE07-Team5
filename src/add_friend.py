from sql import SQLDatabase
sql_db = SQLDatabase("database.db")

# Assume dahao and test exist
sql_db.add_friend("dahao", "chelsea")
sql_db.add_friend("chelsea", "friend")

sql_db.commit()
sql_db.cur.close()