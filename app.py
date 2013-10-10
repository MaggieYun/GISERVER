#coding=utf-8
#author 许照云
import tornado.ioloop
import tornado.web
from main import queryHandler,exportHandler

def startup(port):
    application = tornado.web.Application([
        (r"/giserver2013/(\w*)/(\w*)/export",exportHandler), 
        (r"/giserver2013/(\w*)/(\w*)/query",queryHandler),
    
        # (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": os.path.dirname(__file__)+ os.sep + "sample"}),
    ])
      
    application.listen(port)
    print u"程序已经启动"
    tornado.ioloop.IOLoop.instance().start()


    

if __name__ == '__main__':
    startup(6666)
















    
    # layerFactory = LayerFactory(path)
    # layer1=layerFactory.createLayer('1.ini')

    # print "errors:",layer1.cache.validation.errors  #validation应该何时验证？？放在哪里？

    # bbox = (120.513513,31.28561972,120.98838306,31.36400551)
    # where = "[TASK_POINT_ID]<30"  #有待改进,
    
    # outfields = '*'
    
    # outfields = "TASK_POINT_ID,TASK_POINT_PASS_TIME"



    # bbox = (120.357,31.1675,120.972,31.5392)
    # where = "gid>10"  #暂时与普通数据库where设计不一致
    # outfields = "gid,id,roadname,roadid,roadtype,shape_len,updatetime,source"


    # insr = 4326
    # outsr = 4326

    # queryParameter = QueryParameter(bbox,where,insr,outfields,outsr)
    

    # queryResult = layer1.query(queryParameter)



#绘图
    # size=(500,500)
    # img=layer1.export(queryParameter,size)
    # img.save(r"")
    # img.show()
    
    # print "aliases:",queryResult.aliases
    # print "fields:",queryResult.fields
    # print "features:",queryResult.features[0]
    # print "type:",queryResult.type

    