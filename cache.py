#coding=utf-8
#author 许照云
from extent import *
import copy

from validation import *

class TableCache(object):
    '''
    Database Table(or view) Cache Class
    '''

    SQL = "SELECT %s from %s where %s"

    BASEGEOSQL = "SELECT ST_AsGeoJSON(%s) as geom,%s FROM %s WHERE %s(ST_GeomFromText(%s),geom) AND %s"

    GETBUFFER = "SELECT ST_AsText(ST_Buffer(ST_GeomFromText(%s),%f))"


    def __init__(self,ini,layer):
        '''
        isTable=True可根据ini中的信息来判断
        '''
        self.validation = Validation(ini)

        self.engine = self.validation.engine

        self.name = ini.scheme_name     #数据库中表名，也做此表layer的名字
        self.ini = ini   #该TableCache实例是哪个layer的缓存
        self.layer = layer

        self.scheme_type = ini.scheme_type
        self.bufferArea = 0

    def query(self,queryParameter):
        '''
        以下逻辑主要目的是将geojson转换为json
        '''
        #以下三要素相当于selector的主要内容，可改造成selector
        self.bufferArea = 0
        
        extent = Extent(queryParameter.geometry)      #bbox
        where = queryParameter.where             #where 
        outfields = map(lambda x:str(x),queryParameter.outfields)    #outfields    (尚未考虑insr,outsr)
        insr = queryParameter.insr
        # distance = queryParameter.distance

        #获取aliases,fields
        aliases_dict = self.ini.aliases          #aliases_dict>outfields
        aliases_dict_keys = aliases_dict.keys()
        
        # tableCache = TableCache(self.engine,self.name)
        aliases=["SHAPE"]            #顺序按照outfields的顺序,使用列表是为了保证顺序
        if self.ini.x_field:  #普通数据库
            # features = copy.deepcopy(self.layer.FEATURES)


            # if len(features) == 0:    #如果尚无缓存则从数据库取出数据
            results = copy.deepcopy(self.sync(queryParameter))["features"]  #为何同步实例化时传了两个参数？？
            if (len(results)==0):
                return
            #用户url中传来的参数outfields中不必（也不能）包含x，y字段，会自动查询并显示。
            features = []  
            fields = map(lambda x:str(x),outfields[:])
            fields.insert(0,'SHAPE')
            isgot_fields = True    #布尔型，True表示尚未获得aliases和fields信息
            if outfields[0] is not "*":             #暂且默认queryResult里必然包含x,y字段（即geometry属性）
                for result in results:                  #注意保持取出字段的排列顺序
                    one_result =[]                      #一个graphic的attributes中应取出的outfields字段
                    one_result.append(result['geometry']['coordinates'])   #首先将location字段添加
                    for outfield in outfields:             #按道理outfields必然是self.fileds的子集
                        #获取fields、aliases数据
                        if isgot_fields:          #目的是提高效率，效果不大。
                            if outfield in aliases_dict_keys:
                                aliases.append(str(aliases_dict.get(outfield)))
                            else:
                                aliases.append(outfield)

                        # 获取features要素的所有信息    
                        one = result['properties'].get(outfield)
                        if one:                             #验证一下attributes中是否包含该字段。
                            one_result.append(one)
                        else:
                            one_result.append("null")
                    
                    #提取fields、aliases信息只需遍历一遍outfields
                    isgot_fields = False  


                    features.append(one_result)             #二维数组 
            else:    
                
                features= reduce(lambda x,y:x+y,
                                map(lambda x:[x['properties'].values()],
                                            results))   #去除键，重新组织键值 
                n = len(features)
                for i in range(n) :
                    features[i].insert(0,results[i]['geometry']['coordinates'])
                
                fields = map(lambda x:str(x),results[0]['properties'].keys())
                fields.insert(0,"SHAPE")
                aliases = []
                for field in fields:
                    aliase = str(aliases_dict.get(field))
                    if aliase:
                        aliases.append(aliase)
                    else:
                        aliases.append(field)

        elif self.ini.g_field:   #空间数据库直接进行空间查询，再结合aliases重新组织下数据（不用实现sync）
            isgot_fields = True 
            results = self.sync(queryParameter)
            features = []
            outfields = map(lambda x:x.upper(),outfields)
            fields = outfields[:]
            fields.insert(0,'SHAPE')

            if (len(results['features'])==0):
                return
            for result in results['features']:
                one_result =[]                     
                one_result.append(result['geometry']['coordinates']) 
                
                
                for outfield in outfields:             #按道理outfields必然是self.fileds的子集
                    #获取fields、aliases数据
                    if isgot_fields:          #目的是提高效率，效果不大。
                        if outfield in aliases_dict_keys:
                            aliases.append(str(aliases_dict.get(outfield)))
                        else:
                            aliases.append(outfield)
                    # 获取features要素的所有信息    
                    one = result['properties'].get(outfield)
                    if one:                             #验证一下attributes中是否包含该字段。
                        one_result.append(one)
                    else:
                        one_result.append("null")
                #提取fields、aliases信息只需遍历一遍outfields
                isgot_fields = False 

                features.append(one_result)             #二维数组 

        
        return aliases,fields,features


    def sync(self,queryParameter):
        '''
        同步数据库,从数据库中获取最新的记录;可以指定同步字段,默认同步所有字段信息;
        ?是否需要在第一次调用时,强制同步所有字段信息.
            Y:  之后的查询可以支持任何字段值的返回,但不保证数据的实时性;
            N:  会加载不必要的数据,占用过多系统资源;
            
        @param {list<str>} fields 更新字段列表
        '''


        conn = self.engine.connect()
        
        where = queryParameter.where             #where    
        outfields = queryParameter.outfields     #outfields    (尚未考虑insr,outsr)
        insr = queryParameter.insr
        distance = queryParameter.distance 
        spatialRel = queryParameter.spatialRel

        if(type(queryParameter.geometry)==list):
            extent = Extent(queryParameter.geometry)      #bbox
            extentText = extent.toText()
        else:
            extentText = "'%s'"%queryParameter.geometry

        outfields = ",".join(outfields)
        


        if self.ini.x_field:
            fields = outfields #全部取出,默认情况下全部范围全部数据全部取出
            results = conn.execute(self.SQL%(fields,self.name,where))
        elif self.ini.g_field:           
            if(distance):
                buffer_sql = self.GETBUFFER%(extentText,distance)
                self.bufferArea = str(conn.execute(buffer_sql).fetchall()[0][0])
                extentText = "'%s'"%self.bufferArea
            #以下这句代码，需重新考虑和验证outfields="*"的情况
            
            postgisRelationships = {
                "contains":"ST_Contains",
                "intersects":"ST_Intersects",
                "crosses":"ST_Crosses",
                "touches":"ST_Touches",
                "within":"ST_Within",
                "overlaps":"ST_Overlaps"
            }

            relation = postgisRelationships.get(spatialRel)

            spatial_query_sql = self.BASEGEOSQL%(
                                self.ini.g_field,
                                outfields,
                                self.ini.scheme_name,
                                relation,
                                extentText,
                                where)

            results = conn.execute(spatial_query_sql)
        records = results.fetchall()#获取数据所有记录
        conn.close()#关闭数据库连接,将connection放回连接池

        keys = map(lambda key:str(key.upper()),results.keys())

        self.fields = keys   #包含的所有字段
        results = map(lambda vals:dict(zip(keys,map(encodeAttr,vals))),records)
        features = []
        
        if (self.ini.x_field):
            gtype = "point"
            import shapely
            from shapely.wkt import dumps, loads
            from shapely.geometry import Point,Polygon
            
            if(type(queryParameter.geometry)==list):
                polygon = loads(extent.toWKT()) #extentText多了一对引号
            else:
                polygon = loads(queryParameter.geometry)
                if(distance): #则表示polygon可能不是多边形
                    polygon = polygon.buffer(distance)
                    self.bufferArea = dumps(polygon)

            shapelyRelationships = {
                    "contains":"polygon.contains(point)",
                    "crosses":"polygon.crosses(point)",
                    "intersects":"polygon.intersects(point)",
                    "touches":"polygon.touches(point)",
                    "within":"polygon.within(point)"

                }
            functionStr = shapelyRelationships.get(spatialRel)
            
            for item in results:  
                # print item                             
                x = item.get(self.ini.x_field,0)
                y = item.get(self.ini.y_field,0)

                #一、多边形与每个点做运算
                #二、将点变成点集 multipoint??
                point = Point(x, y)

                if(eval(functionStr)):
                    shape=[x,y]     #x,y对应经纬度
                    # print shape
                    item.pop(self.ini.x_field)         
                    item.pop(self.ini.y_field)
                    feature = {"geometry":{'type':gtype,'coordinates':shape},
                                'properties':item}
                    # print feature
                    features.append(feature)

        elif (self.ini.g_field):
            # print results[0]
            for result in results:  
                feature = {"geometry":eval(result['%s'%self.ini.g_field])}
                result.pop('%s'%self.ini.g_field)
                feature.update({"properties":result})   
                features.append(feature)  #将每次实例化得到的graphic实例添加到layer的缓存中  
        

        self.layer.add_features(features)
        self.layer.get_type()
        # print features[0]
        return self.layer.FEATURES


class Engine:
    cache = {}

    @classmethod
    def create(cls,dsn):
        '''
        create databse engine
        @param {str} dsn database connection string
        '''
        engine = cls.cache.get(dsn)
        if engine is None:
            from sqlalchemy import create_engine
            engine = create_engine(dsn)
            cls.cache[dsn] = engine
        return engine



def encodeAttr(val):
    import datetime
    from decimal import Decimal
    if val is None:
        return ""
    elif isinstance(val,datetime.datetime):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(val,datetime.date):
        return val.strftime("%Y-%m-%d")
    elif isinstance(val,Decimal):
        return float(str(val))
    elif isinstance(val,unicode):
        try:
            return str(val)
        except:  #中文字符
            return val.encode('gbk') 
    else:
        return val  
