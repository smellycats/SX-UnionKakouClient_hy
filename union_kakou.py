# -*- coding: utf-8 -*-
import json

import requests


class UnionKakou(object):

    def __init__(self, **kwargs):
        self.host = kwargs['host']
        self.port = kwargs['port']

        self.headers = {'content-type': 'application/json'}
        self.status = False

    def __del__(self):
        pass
        
    def post_kakou(self, data):
        url = 'http://{0}:{1}/kakou'.format(self.host, self.port)
        try:
            r = requests.post(url, headers=self.headers, data=json.dumps(data))
            if r.status_code == 201:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise

    def connect_test(self):
        url = 'http://{0}:{1}'.format(self.host, self.port)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return json.loads(r.text)
            else:
                self.status = False
                raise Exception('url: {url}, status: {code}, {text}'.format(
                    url=url, code=r.status_code, text=r.text))
        except Exception as e:
            self.status = False
            raise
