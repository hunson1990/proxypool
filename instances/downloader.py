# -*- coding: UTF-8 -*-

'''
页面下载器 downloader
'''

import random,time
import requests
from requests.exceptions import ConnectionError
from utils.setting import *
from instances.db import MysqlClient

class Downloader(object):
    '''页面下载器'''
    def __init__(self,url,headers={}):
        self.base_headers = HEARDERS_DEFAULT
        self.url=url
        self.headers=dict(self.base_headers, **headers)


    def download(self):
        """
        下载器，只供职于spider
        """
        sleepTime = random.randint(DOWNLOAD_DELAY[0],DOWNLOAD_DELAY[1]) + random.random()
        time.sleep(sleepTime)
        #print('正在抓取', self.url)
        header_ua=random.choice(USER_AGENT_LIST) #随机UA
        mysql = MysqlClient('proxy')
        self.headers['User-Agent'] = header_ua
        proxy = mysql.getRandom()
        try:
            if IFPROXY:
                response = requests.get(self.url, headers=self.headers,proxies={'http':proxy[0]})
            else:
                response = requests.get(self.url, headers=self.headers)

        except requests.exceptions.ConnectionError:
            print('连接错误', self.url)
            return None
        except requests.exceptions.Timeout:
            print('请求超时')
            return None
        except:
            print('下载，未知错误！')
            return None
        else:
            if response.status_code == 200:
                #response编码问题： 先获取网页的编码，然后在把response强制设置为网页的原先编码
                #response.encoding = response.apparent_encoding
                print('success :', self.url, response.status_code)
                return response
            else:
                print('服务器返回码异常:', response.status_code, self.url)
                return None


if __name__ == "__main__":

    downloader=Downloader('http://www.baidu.com')
    downloader.download()