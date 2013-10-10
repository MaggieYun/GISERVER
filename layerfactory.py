#coding=utf-8
#author 许照云
import os
from validation import *
from layer import *

class Singleton(type):
    def __init__(cls,name,bases,dic):
        super(Singleton, cls).__init__(name,bases,dic)
        cls.instance = None

    def __call__(cls,*args,**kwargs):
        if cls.instance is None:
            cls.instance = super(Singleton,cls).__call__(*args,**kwargs)
        return cls.instance
        
class LayerFactory:
    '''单例'''
    LAYER_CACHE = {}   #缓存
    __metaclass__ = Singleton

    def __init__(self,dirpath):
        self.dirpath = dirpath  #多个配置文件所在的根目录？

        # self.ini = dict4ini.DictIni(pathname)

        
    def createLayer(self,filepath):
        layer = self.LAYER_CACHE.get(filepath)  #从缓存中判断该实例是否已创建
        if layer is None:
            print "layer from create"
            pathname = os.path.join(self.dirpath,filepath)
            #这里需要格外注意：
            #1、ini是否需要单例类？为何？
            #2、ini不能随便获取不存在的对象后调用save方法，否则会轻易修改了配置文件内容
            #3、查找ini对象时最好使用get()方法，而非点操作
            # ini = dict4ini.DictIni(pathname)
            layer = Layer(pathname) 
            self.LAYER_CACHE[filepath] = layer    
            print self.LAYER_CACHE
        return layer

    def removeLayer(self,layer_name):
        self.LAYER_CACHE.pop(layer_name)
        pass





