# -*- coding: UTF-8 -*-
import tornado.ioloop
import tornado.web
import time  # 引入time模块
import json
import random as rd
import tushare as ts
import datetime
import requests
def floatHandle(num,point):
    return ('%.{}f'.format(point))%num
def newPrice(code):
    data = {}
    url = "http://hq.sinajs.cn/list="+"sh"+code
    dt = requests.get(url).text
    data['price'] = dt.split(",")[3]
    jsondata = json.dumps(data)
    
    return jsondata

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        symbol =  self.get_argument("symbol")
        jdata = newPrice(symbol)
        self.write(str(jdata))
        
        
# 处理历史数据请求        
class HistoryHandler(tornado.web.RequestHandler):
    def get(self):
        symbol = self.get_argument("symbol")#股票代码
        period = self.get_argument("period")#时间周期,单位-分钟
        period_allow_list = ["5","15","30","60"]
        if period not in period_allow_list:
            return 
        data = ts.get_k_data(symbol,ktype=period)
        print "=========",symbol,":",period
        resultlist = []
        lens = len(data)
        for unit in data.iterrows():
            obj  = {}
            dates = unit[1]['date']
            d=datetime.datetime.strptime(dates,"%Y-%m-%d %H:%M")
            obj["date"]=int(time.mktime(d.timetuple()))
            obj["open"]=unit[1]['open']
            obj["close"]=unit[1]['close']
            obj["high"]=unit[1]['high']
            obj["low"]=unit[1]['low']
            obj["volume"]=unit[1]['volume']
            resultlist.append(obj)
        
        resultlist.sort(key=lambda obj:obj.get('date'), reverse=False) 
        
        s = json.dumps(resultlist)
        self.write(s)

class TestHandler(tornado.web.RequestHandler):
    def get(self):
        data = {}
        #         保留几位小数
        point = 5
        #        生成一个系统时间
        ostime = time.time()
        data['timestamp'] = int(ostime)
        seed = rd.uniform(10, 20);
        data['price'] = floatHandle(seed,point)    
        data['vol'] = rd.randint(500,10000);
        jsondata = json.dumps(data)
        self.write(str(jsondata))
# 设置
application = tornado.web.Application([
    (r"/", MainHandler), 
    (r"/history", HistoryHandler),
    (r"/test", TestHandler),
])

if __name__ == "__main__":
    ports = 9080
    application.listen(ports)
    print "service run at prot:",ports
    tornado.ioloop.IOLoop.instance().start()
    