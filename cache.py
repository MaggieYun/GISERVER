#coding=utf-8
#author 许照云
from extent import *
import copy

from validation import *
from tools import *


class TableCache(object):
    '''
    Database Table(or view) Cache Class
    '''

    SQL = "SELECT %s FROM %s WHERE %s"

    BASEGEOSQL = "SELECT ST_AsGeoJSON(%s),%s FROM %s WHERE %s(ST_GeomFromText(%s),%s) AND %s"
    TRANSGEOSQL = "SELECT ST_AsGeoJSON(ST_Transform(ST_SetSRID(%s,%s),%s)),%s FROM %s WHERE %s(ST_GeomFromText(%s),%s) AND %s"

    GETBUFFER = "SELECT ST_AsText(ST_Buffer(ST_GeomFromText(%s),%f))"

    SPATIAL_TRANSFORM = "SELECT ST_AsText(ST_Transform(ST_GeomFromText(%s,%s),%s))"

    #用于geometry为global的情况(空间数据库)
    BASEGEOSQL_G = "SELECT ST_AsGeoJSON(%s),%s FROM %s WHERE  %s"
    TRANSGEOSQL_G = "SELECT ST_AsGeoJSON(ST_Transform(ST_SetSRID(%s,%s),%s)),%s FROM %s WHERE %s"


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

        self.keys = []


    def sync(self,queryParameter):
        '''
        同步数据库
        '''

        conn = self.engine.connect()
        
        where = queryParameter.where             #where    
        outfields = queryParameter.outfields     #outfields    (尚未考虑insr,outsr)
        distance = queryParameter.distance 
        spatialRel = queryParameter.spatialRel
        geometry = queryParameter.geometry
        insr = queryParameter.insr
        outsr = queryParameter.outsr
        
        if(insr == '4326'):
            distance = distance*0.0000106 

        if self.ini.x_field:
            features = self.sync_xy(conn,where,outfields,distance,spatialRel,geometry,insr,outsr)
            
        elif self.ini.g_field:           
            features = self.sync_spatial(conn,where,outfields,distance,spatialRel,geometry,insr,outsr)

        self.layer.add_features(features)
        self.layer.get_type()

        return self.layer.FEATURES

    def sync_xy(self,conn,where,outfields,distance,spatialRel,geometry,insr,outsr):

        #outfields为'*'或者为任意字段的组合（经纬度字段可有可无）
        if(outfields[0] != '*'):
            if self.ini.x_field not in outfields:
                outfields.append(self.ini.x_field)
            if self.ini.y_field not in outfields:
                outfields.append(self.ini.y_field)

        outfields = ",".join(outfields)

        sql = self.SQL%(outfields,self.name,where)
        results = conn.execute(sql)
        records = results.fetchall()#获取数据所有记录
        conn.close()#关闭数据库连接,将connection放回连接池

        self.keys = map(lambda key:str(key.upper()),results.keys())
        results = map(lambda vals:dict(zip(self.keys,map(encodeAttr,vals))),records)
        features = []
        gtype = "point"
        import shapely
        from shapely.wkt import dumps, loads
        from shapely.geometry import Point,Polygon
        # from shapely.geometry import *

        if(geometry == 'global'):  #空间数据库尚且不允许该geometry参数
            polygon = geometry   #请求任意坐标数据(任意合法或不合法坐标数据)
        elif(type(geometry)==list):
            extent = Extent(geometry)      #bbox
            polygon = loads(extent.toWKT()) #extentText多了一对引号
        else:
            polygon = loads(geometry) #可以是任意geometry,并非一定是多边形
            if(distance): #则表示polygon可能不是多边形
                polygon = polygon.buffer(distance)  
                self.bufferArea = dumps(polygon)

        #转换db中点的坐标，若outsr与insr不同，总共需要把所有点转换两次
        
        #因为polygon对象可能是shapely.geometry中的任意对象，比如环线，线等，转换不方便

        #如果polygon不是Polygon对象，以下方法要增加判断
        # print type(polygon)
        # x = list(polygon.exterior.coords)
        # y = []
        # for ele in x:
        #     temp = toMerctor(ele[0],ele[1])
        #     y.append(temp)
        # polygon1 = Polygon(y)
        # print polygon1


        #所以：转换db中的点要素



        shapelyRelationships = {
                "contains":"polygon.contains(point)",
                "crosses":"polygon.crosses(point)",
                "intersects":"polygon.intersects(point)",
                "touches":"polygon.touches(point)",
                "within":"polygon.within(point)"

            }
        functionStr = shapelyRelationships.get(spatialRel)

        for item in results: 
 
            x = item.get(self.ini.x_field,0)
            y = item.get(self.ini.y_field,0)

            if(type(x) == str): #数据库中为空字符串
                x,y = 0,0

            if(self.ini.dbsr != int(insr)): #坐标转换
                if(insr == '4326'):
                    try:          #此处有问题，有待进一步解决
                        x,y = toLonLat(x,y)
                    except:
                        continue
                if(insr == '102113'):
                    x,y = toMerctor(x,y)

            point = Point(x, y)

            if(polygon == 'global' or (eval(functionStr))): #or左右的参数不能调换顺序
                if(insr != outsr):
                    if (outsr == '4326'):
                        x,y = toLonLat(x,y)
                    if (outsr == '102113'):
                        x,y = toMerctor(x,y)

                shape=[x,y]     #x,y对应经纬度
                item.pop(self.ini.x_field)         
                item.pop(self.ini.y_field)
                
                feature = {"geometry":{'type':gtype,'coordinates':shape},
                            'properties':item}
                features.append(feature)

        return features

    
    def sync_spatial(self,conn,where,outfields,distance,spatialRel,geometry,insr,outsr):
        if (self.ini.dbsr == 102113):
            dbsr = '3857'
        else:
            dbsr = self.ini.dbsr

        if(insr == '102113'):
            insr = '3857'
        if(outsr == '102113'):
            outsr = '3857'
        
        if(outfields[0] == '*'):
            if (self.ini.scheme_type == 0):
                columns = conn.execute(self.validation.TABLE_COLUMN_SQL_SPATIAL%self.ini.scheme_name)
            else:
                columns = conn.execute(self.validation.VIEW_COLUMN_SQL_SPATIAL%self.ini.scheme_name)
            outfields = map(lambda x:encodeAttr(x[0]),columns.fetchall())
            outfields.remove(self.ini.g_field)
        else:
            if self.ini.g_field in outfields:
                outfields.remove(self.ini.g_field)

        self.keys = outfields

        outfields = ",".join(outfields)

        if(geometry == 'global'): #请求所有地理范围内数据
            if(dbsr != outsr): #坐标转换
                spatial_query_sql = self.TRANSGEOSQL_G%(
                                            self.ini.g_field,
                                            dbsr,
                                            outsr,
                                            outfields,
                                            self.ini.scheme_name,
                                            where)
            else:
                spatial_query_sql = self.BASEGEOSQL_G%(
                                    self.ini.g_field,
                                    outfields,
                                    self.ini.scheme_name,
                                    where)
        else: #geometry非global的情况
            if(type(geometry)==list):
                extent = Extent(geometry)      #bbox
                extentText = extent.toText()
            else:
                extentText = "'%s'"%geometry

            if(distance):
                buffer_sql = self.GETBUFFER%(extentText,distance)
                self.bufferArea = str(conn.execute(buffer_sql).fetchall()[0][0])
                extentText = "'%s'"%self.bufferArea

            if(dbsr != insr): #坐标转换
                extentText = "'%s'"%conn.execute(self.SPATIAL_TRANSFORM%(extentText,insr,dbsr)).fetchall()[0][0]
            
            postgisRelationships = {
                "contains":"ST_Contains",
                "intersects":"ST_Intersects",
                "crosses":"ST_Crosses",
                "touches":"ST_Touches",
                "within":"ST_Within",
                "overlaps":"ST_Overlaps"
            }

            relation = postgisRelationships.get(spatialRel)

            if(dbsr != outsr): #坐标转换
                spatial_query_sql = self.TRANSGEOSQL%(
                                            self.ini.g_field,
                                            dbsr,
                                            outsr,
                                            outfields,
                                            self.ini.scheme_name,
                                            relation,
                                            extentText,
                                            self.ini.g_field,
                                            where)
            else:
                spatial_query_sql = self.BASEGEOSQL%(
                                    self.ini.g_field,
                                    outfields,
                                    self.ini.scheme_name,
                                    relation,
                                    extentText,
                                    self.ini.g_field,
                                    where)

        results = conn.execute(spatial_query_sql)
        records = results.fetchall()#获取数据所有记录
        conn.close()#关闭数据库连接,将connection放回连接池

        keys = map(lambda key:str(key.upper()),results.keys())
        results = map(lambda vals:dict(zip(keys,map(encodeAttr,vals))),records)
       
        features = []
        temp = 'ST_AsGeoJSON'.upper()    #硬编码
        for result in results:  
            feature = {"geometry":eval(result['%s'%temp])}
            result.pop('%s'%temp)
            feature.update({"properties":result})   
            features.append(feature)  #将每次实例化得到的graphic实例添加到layer的缓存中  

        return features



    def toJSON(self,queryParameter):
        '''
        以下逻辑主要目的是将geojson转换为json
        '''

        self.bufferArea = 0
        
        extent = Extent(queryParameter.geometry)      #bbox
        where = queryParameter.where             #where 
        # outfields = queryParameter.outfields
        outfields = self.keys  #避免'*'的麻烦,有bug待修正

        aliases_dict = self.ini.aliases          #aliases_dict>outfields
        aliases_dict_keys = aliases_dict.keys()

        aliases=["SHAPE"]            #顺序按照outfields的顺序,使用列表是为了保证顺序
        

        if(self.layer.FEATURES):
            results = self.layer.FEATURES
        else:
            results = self.sync(queryParameter)
            

        if self.ini.x_field:  #普通数据库
            outfields.remove(self.ini.x_field)
            outfields.remove(self.ini.y_field)

            results = results['features']
            if (len(results)==0):
                return
            #用户url中传来的参数outfields中不必（也不能）包含x，y字段，会自动查询并显示。
            features = []  
            fields = ['SHAPE'] + map(lambda x:str(x),outfields[:])
            # fields.insert(0,'SHAPE')
            isgot_fields = True    #布尔型，True表示尚未获得aliases和fields信息
            
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
            

        elif self.ini.g_field:   #空间数据库直接进行空间查询，再结合aliases重新组织下数据（不用实现sync）
            isgot_fields = True 
            features = []
            
            outfields = map(lambda x:x.upper(),outfields)
            fields = ['SHAPE'] + outfields[:]
            # fields.insert(0,'SHAPE')

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
