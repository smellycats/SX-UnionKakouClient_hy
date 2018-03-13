import sqlite3


class KakouDB(object):
    def __init__(self, path='kakou.db'):
        self.conn = sqlite3.connect(path)
        print("Opened database successfully")

    def __del__(self):
        self.conn.close()

    def add_idflag(self, start_id, end_id):
        self.conn.execute("INSERT INTO IDFLAG (START_ID,END_ID) \
              VALUES ({0}, {1})".format(start_id, end_id));
        r = self.conn.execute("SELECT last_insert_rowid()")
        self.conn.commit()
        return r.fetchone()[0]

    def set_idflag(self, _id, banned=1):
        sql = "UPDATE IDFLAG SET banned={0} WHERE id={1}".format(
            banned, _id)
        self.conn.execute(sql)
        self.conn.commit()

    def get_idflag_by_id(self, _id):
        sql = "SELECT * FROM IDFLAG WHERE id={0}".format(_id)
        r = self.conn.execute(sql)
        return r.fetchone()

    def get_idflag(self, banned=0, limit=20, offset=0):
        sql = "SELECT * FROM IDFLAG WHERE banned={0} ORDER BY id DESC LIMIT {1} OFFSET {2}".format(banned, limit, offset)
        r = self.conn.execute(sql)
        return r.fetchall()

    def del_idflag(self, _id):
        sql = "DELETE FROM IDFLAG WHERE id={0}".format(_id)
        self.conn.execute(sql)
        self.conn.commit()

