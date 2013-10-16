#coding=utf-8
#author 许照云
import os,sys
from validation import *
from layer import *
from layerfactory import *

#以下代码逻辑有待调整，layerFactory作用未发挥

import tornado.web
#获取缓冲区域的请求是否应该独立？？


dirpath = os.path.dirname(__file__)   

class queryHandler(tornado.web.RequestHandler):

    def get(self,layersPath,layerPath):
        print u"query获取参数"

        layersPath = os.path.join(dirpath,layersPath)
        layerPath = layerPath+'.ini'

        layerFactory = LayerFactory(layersPath) #单例
        layer1 = layerFactory.createLayer(layerPath)

        queryParameter = QueryParameter.create(self)


        format = self.get_argument('format','GEOJSON')
        result = layer1.query(queryParameter,format)


        callback = self.get_argument('callback',None)
        if callback is None:
            self.write(result)
        else:
            self.write('%s(%s)'%(callback,result))
        # self.write(result)


    post = get  


class exportHandler(tornado.web.RequestHandler):

    def get(self,layersPath,layerPath):
        print u"export获取参数"

        layersPath = os.path.join(dirpath,layersPath)
        layerPath = layerPath+'.ini'

        layerFactory = LayerFactory(layersPath)
        layer1 = layerFactory.createLayer(layerPath)


        size = map(lambda x:int(x),self.get_argument("size").split(","))
        queryParameter = QueryParameter.create(self)

        layerFactory = LayerFactory(layersPath)
        layer1 = layerFactory.createLayer(layerPath)
        im=layer1.export(queryParameter,size)

        imstr = im.tostring("png")
        self.set_header("Content-Type", "image/png")
        self.write(imstr)

    post = get  


















