#-*- encoding: utf-8 -*-
import json

from sqlitedb import KakouDB


class sqliteTest(object):
    def __init__(self):
        self.s = KakouDB()
        
    def add_info(self):
        print self.s.add_idflag(123, 456)

    def get_info(self):
        print self.s.get_idflag(limit=1)

    def del_info(self):
        self.s.del_idflag(14)

if __name__ == "__main__":
    st = sqliteTest()
    st.add_info()
    st.get_info()
    st.del_info()
