#coding=utf-8
#author 许照云
from cache import *
import mapnik
import dict4ini
import os
import json


class Layer:
    FEATURES = {}

    def __init__(self,pathname):
        """
        @ini:DictIni对象，有save等方法
        """
        ini = dict4ini.DictIni(pathname)
        self.path = pathname
        self.ini = ini

        self.ini.layer = self #这样操作存在一个小的隐患：save时会修改配置文件的内容，但何时会出现调save方法的情况？

        self.cache = TableCache(ini,self)

        self.geometryType = None
        self.bufferArea = "null"

    def get_type(self):
        '''
        获取layer的图层类型（点图层、线图层、面图层...）
        该逻辑是否放在此处有待考虑？？？
        '''
        try:
            self.geometryType = self.FEATURES['features'][0]['geometry']['type']
        except:
            self.geometryType = None



    @classmethod
    def add_features(cls,features):
        cls.FEATURES = { "type": "FeatureCollection","features":features}


    def reload(self):
        pass

    def queryTotal(self,where):
        totalnum = self.cache.queryTotal(where)
        return json.dumps(totalnum)

    def query(self,queryParameter,format):
        self.cache.sync(queryParameter)
        
        if(format == "JSON"):
            try:
                aliases,fields,features=self.cache.toJSON(queryParameter)
                queryResult = QueryResult(aliases,fields,features,self.geometryType,self.cache.bufferArea)
                result = queryResult.toString()
                return result
            except:   #没有查询出任何符合条件的数据，结果为0
                return 
        else:
            self.FEATURES.update({"bufferArea":self.cache.bufferArea})
            result = json.dumps(self.FEATURES)
            return result


    def export(self,queryParameter,size,extent):
        #1、第一次查询时，两次同步，效率低。缓存问题
        #2、export请求一般都在query请求之后

        #3、经徐州项目，export特殊请求，增加extent参数，extent可能等于geometry
        
        
        where = queryParameter.where

        geometry = queryParameter.geometry  #若geometry为wkt，不为四个数的list，则有问题

        m = mapnik.Map(size[0],size[1])
        styles = self.ini.styles
        keys = styles.keys()
        path = os.path.splitext(self.path)

        for key in keys:  #现修改配置项方式，所有layer都在一个xml中，所以keys的长度始终为1
            xmlpath = str(os.path.join(path[0],styles.get(key)))
            mapnik.load_map(m, xmlpath)

            from mapnik import Ogr, Layer, PostGIS
            if (self.ini.database.dbname != 'postgresql'):
                self.cache.sync(queryParameter) #同步数据
                datasource = Ogr(layer='OGRGeoJSON',string=json.dumps(self.FEATURES)) 
            else:
                #以下逻辑中未考虑到buffer问题，export出子图有问题
                sql = "(SELECT * FROM %s WHERE %s) as %s"%(self.ini.scheme_name,
                                                            where,
                                                            self.ini.scheme_name)
                subtable = '%s'%sql

                datasource = PostGIS(host=self.ini.database.host,
                                    port =self.ini.database.port,
                                    user=self.ini.database.user,
                                    password=self.ini.database.psw,
                                    dbname=self.ini.database.name,
                                    # table=self.ini.scheme_name,
                                    table=subtable,
                                    extent=geometry)  #是geometry or extent，尚未验证？？
                                       
            # print m.layers[0].name
            # print m.layers[0].styles[0]
            m.layers[0].datasource = datasource

            m_extent = mapnik.Box2d(extent[0],extent[1],extent[2],extent[3])

            m.zoom_to_box(m_extent) 

            im = mapnik.Image(m.width,m.height)
            mapnik.render(m, im)
            # mapnik.render_to_file(m,'test4.png', 'png')


        return im


class QueryParameter:
    def __init__(self,geometry,where,insr,outfields,outsr,distance,spatialRel,startRow,endRow):
        self.geometry = geometry
        self.where = where
        self.insr = insr
        self.outfields = outfields.split(",")
        self.outsr = outsr
        self.distance = distance
        self.spatialRel = spatialRel

        self.startRow = startRow
        self.endRow = endRow

    @classmethod
    def create(cls,requestHandler):
        # cls.layer = layer  #layer参数如何处理有待解决？？？
        
        where = requestHandler.get_argument("where",'1=1')
        insr = requestHandler.get_argument("inSR")
        outsr = requestHandler.get_argument("outSR")  
        outfields = requestHandler.get_argument("outfields","*")
        spatialRel = requestHandler.get_argument("spatialRel","contains")

        startRow = requestHandler.get_argument("startRow",0)
        endRow = requestHandler.get_argument("endRow",0)


        try:  #export请求时有的参数
            #bbox是以逗号分隔的四个数值  
            bbox = map(lambda x:float(x),requestHandler.get_argument("geometry").split(","))
            # print "bbox____________"
            queryParameter = QueryParameter(bbox,where,insr,outfields,outsr,0,spatialRel,startRow,endRow) 
        except:  #query请求时参数
            #geometry是wkt字符串对象  
            geometry = requestHandler.get_argument("geometry")
            # print "geometry____________"
            distance = float(requestHandler.get_argument('buffer',0))  #缓冲距离
            # print "distance_________", distance
            #默认全部取出？？还是缓存的？？
            queryParameter = QueryParameter(geometry,where,insr,outfields,outsr,distance,spatialRel,startRow,endRow)
        
        return queryParameter


    def toString(self):
        pass    


class QueryResult:
    def __init__(self,aliases,fields,features,layer_type,bufferArea):
        self.aliases = aliases
        self.fields = fields
        self.features = features
        self.type = layer_type 
        self.bufferArea = bufferArea or "null"

    def toString(self):
        result = {"aliases":self.aliases,
                 "fields":self.fields,
                 "features":self.features,
                 "type":self.type,
                 "bufferArea":self.bufferArea}  
        return json.dumps(result)









