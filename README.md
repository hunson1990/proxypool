# proxypool

本代理池涉及到知识点：
多进程(process)，多线程(threading)，协程（异步网络请求aiohttp）
flask制作api, 并通过web界面实时监控代理池的工作状态

代理池：采集器，测试器，API，三个部分

[采集器]
采集器：下载器，解析器，存储器
下载器采用多线程下载网页，下载结束由下载器直接交给解析器去解析，由domain（域名）去判断哪个解析器进行解析
存储器单线程

[测试器]
测试器采用协程，异步网络请求（aiohttp）进行检测

[API]
API 用flask做




core 主要是一些核心模块，采集/测试/API
instance 主要是一些封装，下载/数据库/爬虫模块
utils 是一些工具函数 包含setting 文件

