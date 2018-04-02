'''
整个代理池的核心调度器，负责 采集/测试代理 的调度工作
----------------------------------------------

本代理池涉及到知识点：
多进程，多线程，协程（异步网络请求aiohttp）
flask制作api

代理池：采集器，测试器，API，三个部分

[采集器]
采集器：下载器，解析器，存储器
下载器采用多线程下载网页，下载结束由下载器直接交给解析器去解析，由domain（域名）去判断哪个解析器进行解析
存储器单线程

[测试器]
测试器采用协程，异步网络请求（aiohttp）进行检测

'''

import time,os
from multiprocessing import Process,Queue
from core.Api import run
from core.Getter import Getter
from core.Tester import Tester
from utils.setting import *


class Scheduler():
    def __init__(self):
        self.tester = Tester()
        self.getter = Getter()
        self.apirun = run


    def schedule_tester(self, cycle=TESTER_CYCLE):
        """
        定时测试代理
        """
        while True:
            print('测试器开始运行')
            self.tester.run()
            if cycle:
                print('%s秒后再次进行测试...'%str(cycle))
                time.sleep(cycle)

    def schedule_getter(self,q_savethread, q_downthread, cycle=GETTER_CYCLE):
        """
        定时获取代理
        """
        while True:
            print('开始抓取代理')
            self.getter.run(q_savethread , q_downthread)
            if cycle:
                print('%s秒后再次进行采集...' % str(cycle))
                time.sleep(cycle)

    def schedule_api(self,q_savethread,q_downthread):
        """
        开启API
        """
        self.apirun(q_savethread,q_downthread)


    def run(self):
        print('代理池开始运行')
        # settings 里面，TESTER_ENABLED，如果真，就让调度器执行 test（检查） 功能
        q_savethread = Queue() #传递存储线程信息
        q_downthread = Queue() #传递下载线程信息

        if TESTER_ENABLED:
            tester_process = Process(target=self.schedule_tester, name='检测进程')
            tester_process.daemon = True
            tester_process.start()

        if GETTER_ENABLED:
            getter_process = Process(target=self.schedule_getter,args=(q_savethread,q_downthread,), name='采集进程')
            getter_process.daemon = True
            getter_process.start()

        if API_ENABLED:
            api_process = Process(target=self.schedule_api,args=(q_savethread,q_downthread,), name='API进程')
            api_process.daemon = True
            api_process.start()

        while True:
            pass
            #print('q_downThread :', q_downThread.get())



if __name__ == "__main__":

    scheduler=Scheduler()
    scheduler.run()
