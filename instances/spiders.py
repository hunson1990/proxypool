# -*- coding: UTF-8 -*-

#__author__ = 'mr.guo'

'''
爬虫们
涉及到各网站的抓取工作，其中： domain页面/解析方法 不同。
代理格式：0.0.0.0:80，str字符串

如果要增加网站，先要在put_url里面把url压进去，然后增加解析函数
解析函数命名规则： parse_域名(self)
'''

# 队列
from queue import Queue
import threading
from instances.db import RedisClient
from instances.downloader import Downloader
from utils.utils_func import responseTodom, getDomain, match_ip
from utils.setting import DATABASES_REDIS

class Spider(object):

    def __init__(self):
        self.urlQueue = Queue()
        self.proxyQueue = Queue()
        self.downThread = [] # 用于存储下载线程
        self.saveThread = None # 用于存储：saver线程
        self.ip=[] # 存储采集到的代理，；这里可以不用这个列表，因为会比较耗内存，可以读取resids里面的量就是采集的代理

    def download(self,q_downthread):
        '''下载页面，并根据url的域名，选择合适的解析函数'''
        #print('%s:开始下载'% threading.current_thread().name)
        while not self.urlQueue.empty():
            url=self.urlQueue.get(False)
            threading.current_thread().job = url #把当前线程的工作内容，保存到线程属性里面
            domain = getDomain(url)# 获取域名，方便后面根据域名 选择解析函数
            func_name= domain.replace('.','_')

            downloader = Downloader(url)
            response = downloader.download()
            if response:
                eval('self.parse_{}({})'.format(func_name,'response'))
            else:
                #print('下载失败...')
                #如果下载失败，应该把url继续put进去
                self.urlQueue.put(url)

        #print('%s:下载结束'%threading.current_thread().name)


    def downThreadStatus(self):
        '''判断下载任务的状态'''
        downloadStatus = None
        for thread in self.downThread:
            if thread.isAlive():
                downloadStatus = True
                break
            else:
                downloadStatus = False
        return downloadStatus

    def save(self,q_savethread):
        #print('存储工作开始...')
        self.ip.clear()
        redis=RedisClient(DATABASES_REDIS['REDIS_SET_KEY'])
        saveEnable = True
        while saveEnable:
            downloadStatus = self.downThreadStatus()
            try:
                proxy = self.proxyQueue.get(False)
                self.saveThread.job=proxy #工作内容保存到线程对象的属性里面
                self.ip.append(proxy)
                print('Get proxy :',proxy)
                redis.add(proxy)
            except:
                pass
                #print('proxy队列为空，退出存储')
            if downloadStatus==False and self.proxyQueue.empty():
                saveEnable = False

        print('The save work is endding...')




    def parse_xicidaili_com(self,response=None):
        res_dom = responseTodom(response)

        try:
            node_list=res_dom.xpath("//table[@id='ip_list']//tr")
        except:
            print('xpath 页面解析错误')
            print(response.text)
        else:
            for node in node_list:
                try:
                    ip=node.xpath("./td[2]/text()")[0]
                    port=node.xpath("./td[3]/text()")[0]
                except:
                    print('xpath，ip解析错误')
                else:
                    proxy=':'.join([ip, port])
                    if match_ip(proxy):
                        self.proxyQueue.put(proxy)

    def parse_ip3366_net(self,response=None):
        res_dom = responseTodom(response)
        try:
            node_list=res_dom.xpath("//table//tr")
        except:
            print('xpath 页面解析错误')
            print(response.text)
        else:
            for node in node_list:
                try:
                    ip=node.xpath("./td[1]/text()")[0]
                    port=node.xpath("./td[2]/text()")[0]
                except:
                    print('xpath，ip解析错误')
                else:
                    proxy=':'.join([ip, port])
                    if match_ip(proxy):
                        self.proxyQueue.put(proxy)


    def parse_66ip_cn(self,response=None):
        #print('解析中。。。')
        res_dom = responseTodom(response)
        try:
            node_list=res_dom.xpath("//div[@class='containerbox boxindex']//tr")
        except:
            print('xpath 页面解析错误')
            print(response.text)
        else:
            for node in node_list:
                try:
                    ip=node.xpath("./td[1]/text()")[0]
                    port=node.xpath("./td[2]/text()")[0]
                except:
                    print('xpath，ip解析错误')
                else:
                    proxy=':'.join([ip, port])
                    if match_ip(proxy):
                        self.proxyQueue.put(proxy)


        #print('解析结束。。。')


    def put_url(self):
        '''向urlQueue里面塞url'''

        #---66ip.cn
        url="http://www.66ip.cn/{}.html"
        for pageNum in range(1,1200):
            self.urlQueue.put(url.format(pageNum))

        #---xicidaili.com---
        url="http://www.xicidaili.com/wt/{}"
        for pageNum in range(1,1690):
            self.urlQueue.put(url.format(pageNum))

        #---ip3366.net---
        url ="http://www.ip3366.net/?stype=1&page={}"
        for pageNum in range(1,11):
            self.urlQueue.put(url.format(pageNum))





