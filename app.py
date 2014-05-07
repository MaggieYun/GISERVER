#coding=utf-8
#author 许照云
import tornado.ioloop
import tornado.web
from main import queryHandler,exportHandler,totalHandler

def startup(port):
    application = tornado.web.Application([
        (r"/giserver2013/(\w*)/(\w*)/export",exportHandler), 
        (r"/giserver2013/(\w*)/(\w*)/query",queryHandler),
        (r"/giserver2013/(\w*)/(\w*)/total",totalHandler),
    
        # (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.dirname(__file__)+ os.sep + "sample"}),
    ])
      
    application.listen(port)
    print u"程序已经启动"
    tornado.ioloop.IOLoop.instance().start()


    

if __name__ == '__main__':
    import os
    os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8' 

    startup(6666)
