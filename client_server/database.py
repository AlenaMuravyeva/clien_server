""" The database, in which stored users logins and passwords"""
import sys
import sqlite3
import client_server.log


class DataBase(object):
    """Initializes database."""
    def __init__(self, name_database):
        """Initializes database."""
        self.database = name_database
        self.created_db()

    def created_db(self):
        """Created database, if she did'n create"""
        client_server.log.logger.info("Initialization SQL %s", self.database)
        try:
            self.connection_db = sqlite3.connect(
                self.database, check_same_thread=False
            )
            self.cur = self.connection_db.cursor()
            self.cur.execute(
                "CREATE TABLE IF NOT EXISTS users (login VARCHAR, password VARCHAR)"
            )
            client_server.log.logger.info(
                "Initialization SQL: DB is initialized OK..."
            )

        except sqlite3.DatabaseError as err:
            print("Initialization SQL: DB creation FAIL: %s", err)
            client_server.log.logger.info(
                "Initialization SQL: DB creation FAIL: %s", err
            )
            sys.exit(1)

    def check_duplicate(self, login):
        """Check availability login in database"""
        data = False
        get_login = "SELECT login FROM users WHERE login = '{}'".format(login)
        self.cur.execute(get_login)
        data = self.cur.fetchone()
        if data is None:
            return data
        else:
            data = True
            return data

    def get_password(self, login):
        """Get entry "password" from database for this login"""
        password = None
        get_password = "SELECT  password FROM users WHERE login = '{}'".format(login)
        self.cur.execute(get_password)
        password = self.cur.fetchone()
        return password

    def add_new_user(self, login, password):
        """Add new user to database"""
        login_password = (login, password)
        new_entry = ("INSERT INTO users VALUES(?,?)")
        self.cur.execute(new_entry, login_password)
        self.connection_db.commit()
