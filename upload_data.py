# -*- coding: utf-8 -*-
import time
import json

import arrow

from helper_kakou_v2 import Kakou
#from union_kakou import UnionKakou
from helper_unionkk import UnionKakou
from sqlitedb import KakouDB
from my_yaml import MyYAML
from my_logger import *


debug_logging(u'/home/logs/error.log')
logger = logging.getLogger('root')


class UploadData(object):
    def __init__(self):
        # 配置文件
        self.ini = MyYAML('/home/my.yaml')
        self.flag_ini = MyYAML('/home/flag.yaml')
        self.my_ini = self.ini.get_ini()

        # request方法类
        self.kk = Kakou(**dict(self.my_ini['kakou']))
        self.uk = UnionKakou(**dict(self.my_ini['union']))
        self.sq = KakouDB('/home/kakou.db')
        
        self.kk.status = True
        self.uk.status = True

        self.city = self.my_ini['city']
        self.kkdd_id = self.my_ini['kkdd_id']
        self.id_flag = self.flag_ini.get_ini()['id']
        self.step = self.my_ini['id_step']
        # 有效的卡口地点
        if self.my_ini['usefulkkdd'] is None:
            self.useful_kkdd = set()
        else:
            self.useful_kkdd = set(self.my_ini['usefulkkdd'])

    def set_id(self, _id, msg=''):
        """设置ID"""
        self.id_flag = _id
        self.flag_ini.set_ini({'id': _id})
        logger.info('{0} {1}'.format(_id, msg))

    def post_data(self, start_id, end_id):
        """上传卡口数据"""
        info = self.kk.get_kakou(start_id, end_id, 1, self.step+1)
        # 如果查询数据为0则退出
        if info['total_count'] == 0:
            return

        data = []
        for i in info['items']:
            if i['kkbh'] is None:
                i['kkdd_id'] = self.kkdd_id
                i['kkbh'] = self.kkdd_id
            elif len(i['kkbh']) != 9:
                i['kkdd_id'] = self.kkdd_id
                i['kkbh'] = self.kkdd_id
            #if i['kkbh'] is None:
            #    continue
            #if len(i['kkbh']) != 9:
            #    continue
	    # 有效卡点为零时
            if len(self.useful_kkdd) == 0:
                pass
            elif i['kkbh'] not in self.useful_kkdd:
                continue
            data.append({'jgsj': i['jgsj'],          # 经过时间
                         'hphm': i['hphm'],          # 号牌号码
                         'kkdd_id': i['kkbh'],       # 卡口地点ID
                         'hpys_id': i['hpys_id'],    # 号牌颜色ID
                         'fxbh': i['fxbh_code'],     # 方向编号
                         'cdbh': i['cdbh'],          # 车道
			 'clsd': i['clsd'],          # 车速
			 'hpzl': i['hpzl'],          # 号牌种类
                         'img_path': i['imgurl']})   # 图片url地址
        if len(data) > 0:
            self.uk.post_kakou(data)                 # 上传数据

    def post_info_realtime(self):
        print('id_flag: {0}'.format(self.id_flag))
        """上传实时数据"""
        maxid = self.kk.get_maxid()
        # id间隔
        interval = maxid - self.id_flag
        #print('interval={0}'.format(interval))
        # 没有新数据则返回
        if interval <= 0:
            r = self.post_data_from_db()
            return r
        # id间隔大于阀值
        if interval > self.step * 60:
            for i in range(60):
                self.sq.add_idflag(self.id_flag+1, self.id_flag+self.step)
                self.set_id(self.id_flag+self.step, msg='sqlite')  # 设置最新ID
            return 0
        # id间隔小于步长
        if interval < self.step:
            self.post_data(self.id_flag+1, maxid)
            self.set_id(maxid)   # 设置最新ID
            return 0.5
        
        self.post_data(self.id_flag+1, self.id_flag+self.step)
        self.set_id(self.id_flag+self.step)
        return 0.25

    def post_data_from_db(self):
        """上传历史数据"""
        r = self.sq.get_idflag(banned=0, limit=1)
        if r == []:
            return 1
        self.post_data(r[0][1], r[0][2])
        # 删除历史ID
        self.sq.del_idflag(r[0][0])
        logger.info('{0} {1}'.format(r[0][2], 'from db'))
        return 0

    def main_loop(self):
        while 1:
            if self.kk.status and self.uk.status:
                try:
                    n = self.post_info_realtime()
                    time.sleep(n)
                except Exception as e:
                    logger.exception(e)
                    time.sleep(5)
            else:
                try:
                    print(self.kk.status)
                    print(self.uk.status)
                    if not self.kk.status:
                        self.kk.get_maxid()
                        self.kk.status = True
                    if not self.uk.status:
                        self.uk.get_root()
                        self.uk.status = True
                except Exception as e:
                    logger.exception(e)
                    time.sleep(1)

