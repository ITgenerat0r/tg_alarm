import Config
from includes import *
import pymysql
from uuid import uuid4
from datetime import datetime
from shutil import copy



class Database:
    "Base class for Database"
    host = "localhost"
    user = "root"

    def __init__(self, host, user, password, db_name):
        self.host = host
        self.__port = 3306
        self.user = user
        self.password = password
        self.db_name = db_name
        self.__status = 1
        self.__logs = True
        self.__stop_errors = False


    def set_time_out(self, tm=28800):
        self._commit(f"SET GLOBAL connect_timeout={tm}")
        self._commit(f"SET GLOBAL interactive_timeout={tm}")
        self._commit(f"SET GLOBAL wait_timeout={tm}")

    def __del__(self):
        self.close_connect()

    def set_logs(self, log=True):
        self.__logs = log

    def set_stop_errors(self, stop_err=False):
        self.__stop_errors = stop_err

    def connect(self):
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.__port,
                user=self.user,
                password=self.password,
                database=self.db_name,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.__status = 1
            if self.__logs:
                print(f"success {self.db_name}")
        except Exception as ex:
            if self.__logs:
                print(f"Connection refused {self.db_name}")
                print(ex)
                if self.__stop_errors:
                    input("Press enter to continue...")


    def _checkSlash(self, line):
        return line.replace('\\', '\\\\')

    def _checkQuote(self, line):
        # return line.replace("'", '"')
        return line.replace('"', "'")

    def _commit(self, cmd, err="commit error"):
        with self.connection.cursor() as cursor:
            try:
                if self.__logs:
                    print(f"_commit({cmd})")
                cursor.execute(cmd)
                self.connection.commit()
                return True
            except Exception as ex:
                if self.__logs:
                    print(cmd)
                    print(red_text("Error:"), err)
                    print(ex)
                    if self.__stop_errors:
                        input("Press enter to continue...")
                self.__status = 0
                self.heal()
                return False
            return False

    def _fetchall(self, cmd, err="fetch error"):
         with self.connection.cursor() as cursor:
            try:
                if self.__logs:
                    print(f"_fetchall({cmd})")
                cursor.execute(cmd)
                return cursor.fetchall()
            except Exception as ex:
                if self.__logs:
                    print(red_text("Error:"), err)
                    print(cmd)
                    print(ex)
                    if self.__stop_errors:
                        input("Press enter to continue...")
                self.__status = 0
                self.heal()
                return {}
            return {}

    def heal(self):
        if self.__status != 1:
            self.connect()
        return self.__status == 1

    def close_connect(self):
        self.connection.close()


    def get_current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]








class Alarm_database(Database):

    

    def add_user(self, login, password, name):
        if login:
            columns = "u_login"
            values = f"'{login}'"

            columns += ", u_passhash"
            values += f", '{password}'"

            columns += ", u_name"
            values += f", '{name}'"

            self._commit(f"insert into users({columns}) values ({values})")


    def set_user_name(self, id, name):
        if name:
            self._commit(f"update users set u_name = '{name}' where id = {id}")

    def set_user_login(self, id, login):
        if name:
            self._commit(f"update users set u_login = '{login}' where id = {id}")

    def set_user_password(self, id, phash):
        if name:
            self._commit(f"update users set u_passhash = '{phash}' where id = {id}")


    def delete_user(self, id):
        if id:
            self._commit(f"delete from users where id = {id}")

    def get_user(self, login):
        r = self._fetchall(f"select * from users where u_login = '{login}'")
        if r:
            return r[0]
        return {}

    def get_user_by_id(self, id):
        r = self._fetchall(f"select * from users where id = {id}")
        if r:
            return r[0]
        return {}






   

    def login(self, login, password):
        user = self.get_user(login)
        if user:
            if user['u_passhash'] == password:
                return True
        return False







    def new_session(self, iv="", aes_key=""):
        cols = "date_last_conn"
        vals = f"'{self.get_current_time()}'"
        if iv:
            cols += ", aes_iv"
            vals += f", '{iv}'"
        if aes_key:
            cols += ", aes_key"
            vals += f", '{aes_key}'"
        self._commit(f"insert into sessions ({cols}) value ({vals})")
        r = self._fetchall(f"SELECT * FROM sessions ORDER BY ID DESC LIMIT 1")
        if r:
            return r[0]['id']
        return 0


    def delete_session(self, session_id):
        self._commit(f"delete from sessions where id = {session_id}")

    def delete_old_sessions(self):
        time = self.get_current_time()
        time = time[:10]
        dt = self._fetchall(f"select * from sessions where date_last_conn < '{time}';")
        for i in dt:
            self._commit(f"delete from sessions where id = {i['id']}")
        

    def get_session(self, session_id):
        dt = self._fetchall(f"select * from sessions where id = {session_id}")
        if dt:
            return dt[0]
        return {}

    def set_iv(self, session_id, iv):
        self._commit(f"update sessions set aes_iv = '{iv}' where id = {session_id}")

    def get_iv(self, session_id):
        ss = self.get_session(session_id)
        if ss:
            return ss['aes_iv']

    def set_aes_key(self, session_id, aes_key):
        self._commit(f"update sessions set aes_key = '{aes_key}' where id = {session_id}")


    def set_login(self, session_id, login):