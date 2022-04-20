from sql import SQLDatabase
sql_db = SQLDatabase("database.db")
sql_db.database_setup()
sql_db.commit()
sql_db.cur.close()