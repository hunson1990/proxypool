# -*- coding: UTF-8 -*-

#__author__ = 'mr.guo'

'''
主要功能：对数据库进行封装
redis数据存储在内存中，因而速度是相当快。 缺点：无法长时间保存，所以将redis作为代理队列，test合格的代理将存储到mysql当中。

因为2个原因，redis里面选择的数据结构为'集合'(非有序)：
1. 检测redis，无论代理是否合格，都会被删除，所以对排序无要求
2. 代理有重复的可能
'''

import re,random
import redis,pymysql
from utils.setting import DATABASES_REDIS,DATABASES_MYSQL  # (REDIS_SET_KEY 为 ：set集合名)
from utils.utils_func import get_hash



class RedisClient(object):
    def __init__(self,redisKey,host=DATABASES_REDIS['REDIS_HOST'],port=DATABASES_REDIS['REDIS_PORT'],password=DATABASES_REDIS['REDIS_PASSWORD']):
        '''初始化redis数据库'''

        #加上decode_responses=True，写入的键值对中的value为str类型，不加这个参数写入的则为字节类型。
        self.pool = redis.ConnectionPool(host=host, port=port, decode_responses=True) #redis连接池
        self.db = redis.StrictRedis(connection_pool=self.pool)
        self.redis_set_key = redisKey
    #---增
    def add(self,proxy):
        '''添加代理'''
        #检测数据是否为ip

        if not re.match('\d+\.\d+\.\d+\.\d+\:\d+', proxy):
            print('代理不符合规范', proxy, '丢弃')
            return
        #判断是否存在这个代理ip
        if not self.db.sismember(self.redis_set_key,proxy):
            #如果不存在就插入
            return self.db.sadd(self.redis_set_key,proxy)


    #---删
    def delete(self,proxy):
        '''删除指定代理'''
        return self.db.srem(self.redis_set_key,proxy)

    #---查
    def getRandom_andDele(self,count):
        '''随机获取代理,并且删除这些代理,count是返回代理的数量;'''
        proxies = self.db.srandmember(self.redis_set_key,count)
        for proxy in proxies:
            self.delete(proxy)
        return proxies



    def getRandom(self, count):
        '''随机获取代理,但不删除这些代理,count是返回代理的数量;'''
        return self.db.srandmember(self.redis_set_key,count)


    def getCount(self):
        '''获取目前所有代理的数量'''
        return self.db.scard(self.redis_set_key)

    def getAll(self):
        '''获取所有的代理成员'''
        return self.db.sscan(self.redis_set_key)


class MysqlClient(object):
    def __init__(self,table):
        self.table = table

    def getConn(self):
        '''封装数据库连接，每次操作都是新增一个conn，不能公用一个conn'''
        conn = pymysql.connect(host=DATABASES_MYSQL['HOST'], user=DATABASES_MYSQL['USER'], password=DATABASES_MYSQL['PASSWORD'], db=DATABASES_MYSQL['NAME'],
                               port=DATABASES_MYSQL['PORT']
                               , charset='utf8', autocommit=True)
        cursor = conn.cursor()
        mysql=[conn,cursor]
        return mysql


    # --------------添加
    def add(self,proxy):
        mysql = self.getConn()
        proxyHash = get_hash(proxy)
        try:
            sql="INSERT INTO %s (proxyId,proxy) VALUES ('%s','%s')"%(self.table,proxyHash,proxy)
            mysql[1].execute(sql)
        except pymysql.err.IntegrityError:
            return 'The proxy: %s is already exists!'%proxy
        except:
            return 'Add proxy unkwon Error!'
        else:
            return '代理 %s: 插入MYSQL成功！'%proxy
        finally:
            mysql[0].close()


    # --------------删除
    def delete(self,proxy):
        mysql = self.getConn()
        proxyHash = get_hash(proxy)
        try:
            sql="DELETE FROM %s WHERE proxyId = '%s' "%(self.table,proxyHash)
            mysql[1].execute(sql)
        except:
            #print('Unkwon Error!')
            return 'Unkwon Error!'
        else:
            #print('%s: delete success'%proxy)
            return '%s: delete success'%proxy
        finally:
            mysql[0].close()


    #--------------查询
    def getProxies(self,count):
        mysql = self.getConn()
        '''获取代理,count是返回代理的数量;'''
        try:
            sql="SELECT * FROM %s"%self.table
            mysql[1].execute(sql)
            proxies = mysql[1].fetchmany(count)
        except:
            print('Unkwon Error!')
        else:
            return proxies
        finally:
            mysql[0].close()



    def getRandom(self):
        '''随机获取一个代理;'''
        mysql = self.getConn()
        count = self.getCount()
        index = random.randint(0,count-1)
        try:
            sql="SELECT * FROM %s limit %s,1"%(self.table,index)
            mysql[1].execute(sql)
            proxy = mysql[1].fetchone()
        except:
            print('Unkwon Error!')
        else:
            return proxy
        finally:
            mysql[0].close()




    def getAll(self):
        '''获取所有的代理成员'''
        mysql = self.getConn()
        try:
            sql="SELECT * FROM %s"%self.table
            mysql[1].execute(sql)
            proxies = mysql[1].fetchall()
        except:
            print('Unkwon Error!')
        else:
            return proxies
        finally:
            mysql[0].close()



    def getCount(self):
        '''获取目前所有代理的数量'''
        mysql = self.getConn()
        try:
            sql="SELECT COUNT(*) FROM %s"%self.table
            mysql[1].execute(sql)
            count = mysql[1].fetchone()[0]
        except:
            print('Unkwon Error!')
        else:
            return count
        finally:
            mysql[0].close()


if __name__ == '__main__':

    redis=RedisClient(DATABASES_REDIS['REDIS_SET_KEY'])


    mysql = MysqlClient('proxy')
    #mysql.add('1.3.214.2:800')
    #mysql.add('124.263.24.2:800')
    #conn.delete('124.23.214.2:800')
    #print(mysql.getAll())
    while True:
        print(redis.getCount())







