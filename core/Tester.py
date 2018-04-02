'''
检测ip代理器，代理从redis中取出；若合格将放入mysql数据库，不合格将清理。

这里我们不采用多线程了，采用协程工作。（asyncio是Python 3.4版本引入的标准库，直接内置了对异步IO的支持。）

代理 proxies={"http": "%s"%proxy}， 其中http是目标网站使用的协议
'''

import asyncio,aiohttp
import random,time

from instances.db import RedisClient,MysqlClient
from utils.setting import *


class saveMysql(object):
    pass


class Tester(object):

    def __init__(self):
        self.redis=RedisClient(DATABASES_REDIS['REDIS_SET_KEY'])
        self.mysql=MysqlClient('proxy')

    async def testProxy(self,proxy):
        print('The proxy %s is begin to test...' % proxy)
        header_ua=random.sample(USER_AGENT_LIST,1)[0] #随机选一个UA
        HEARDERS_DEFAULT['User-Agent'] = header_ua
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(TESTURL, headers=HEARDERS_DEFAULT, proxy='http://%s' % proxy,timeout=TIMEOUT) as resp:
                    if resp.status in VALID_STATUS_CODES:
                        #print('测试成功:',proxy,'装入mysql...')
                        print(self.mysql.add(proxy))
                    else:
                        print('The response code is unlawful...:', resp.status,'---', proxy)
            except:
                print('Test faild...', proxy)


    def run(self):

        if self.redis.getCount()==0:
            print('redis代理为空，测试器退出!')
            return
        loop = asyncio.get_event_loop()
        while self.redis.getCount()>0:
            proxies = self.redis.getRandom_andDele(TEST_SIZE)
            tasks = [self.testProxy(proxy) for proxy in proxies]
            loop.run_until_complete(asyncio.wait(tasks))
            time.sleep(TIMEOUT+1)
        #loop.close()
        print('Test endding...')




if __name__ == "__main__":
    test = Tester()
    test.run()
