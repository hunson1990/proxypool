'''
获取器，拿到代理
并把代理存储到redis

'''

import threading
import random,time
from instances.spiders import Spider
from utils.setting import *


#---采集器的核心-- 用于调度(下载/解析/存储)---
class Getter(object):

    def __init__(self):
        self.spider = Spider()

    def run(self,q_savethread,q_downthread):
        self.spider.put_url()

        #-------多线程进行下载任务（ 本来打算使用线程池，后来对那个类threadpool有疑惑 ）
        for i in range(DOWNLOAD_THREADCOUNT):
            t = threading.Thread(target=self.spider.download,args=(q_downthread,), name='下载线程%s号'%str(i))
            self.spider.downThread.append(t) #把下载线程放到spider属性里面
            t.setDaemon(True)
            t.start()
            #time.sleep(random.randint(1,3)+random.random()) #每个线程开启时间间隔随机,可是如果设置了，那么就阻塞了，所以还是不设置了
        for thread in self.spider.downThread:
            pass
            #thread.join(),不等待子线程了，不然主线程阻塞。 主线程自行阻塞，用条件判断是否结束

        #------单线程存储---------
        savethread = threading.Thread(target=self.spider.save,args=(q_savethread,), name='存储线程')
        self.spider.saveThread = savethread #把存储线程保存到spider属性里面，方便以后监控
        #print(self.spider.saveThread)
        #q_downThread.put(self)
        savethread.setDaemon(True)
        savethread.start()


        #线程数量（主线程+子线程），若大于1说明有子线程在工作  threading.activeCount() > 1
        while threading.activeCount() > 1:
            # 存储线程的,工作状态/线程名字/工作内容 保存到Queue，以提供给其他进程； 元组的数据格式
            if hasattr(self.spider.saveThread, 'job'):
                savethreadMsg = (self.spider.saveThread.is_alive(), self.spider.saveThread.name, self.spider.saveThread.job)
            else:
                savethreadMsg = (self.spider.saveThread.is_alive(), self.spider.saveThread.name, None)
            q_savethread.put(savethreadMsg)

            # 下载线程的,工作状态/线程名字/工作内容 保存到Queue，以提供给其他进程； 列表+元组的数据格式
            downthreadMsg = []
            for downthread in self.spider.downThread:
                if hasattr(downthread, 'job'):
                    downthreadMsg.append((downthread.is_alive(),downthread.name,downthread.job))
                else:
                    downthreadMsg.append((downthread.is_alive(), downthread.name, None))
            q_downthread.put(downthreadMsg)




        print('一共采集了%s个代理'%self.spider.ip.__len__())
        print('Getter is endding...')


if __name__ == "__main__":
    get=Getter()
    get.run()
