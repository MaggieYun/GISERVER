#coding=utf-8
#author 许照云
from extent import *
import copy
class GiserverStore:
    '''
    用于处理数据库操作及取出数据的处理
    '''
    QEURY_SQL = "select * from %s" 
    
    @classmethod
    def set_engine(cls,engine):
        '''
        设置engine
        '''
        cls.engine = engine

    # @classmethod
    # def get_data_from_database(cls,sql):
    #     '''
    #     从数据库中取出数据，并组成字典的形式
    #     '''
    #     conn = cls.engine.connect()#从连接池获取连接
    #     results = conn.execute(sql)#执行查询
    #     records = results.fetchall()#获取数据所有记录
    #     conn.close()#关闭数据库连接,将connection放回连接池
    #     keys = map(lambda key:key.upper(),results.keys())
    #     results = map(lambda vals:dict(zip(keys,map(encodeAttr,vals))),records)
    #     return results,keys

    # @classmethod
    # def filter_data(cls,layer,queryParameter):
    #     extent =Extent(queryParameter.bbox)      #bbox
    #     where = queryParameter.where             #where    直接在查询数据库的时候给出where过滤条件，不用filter函数，影响缓存内容，即每次query都需重新查询数据库。
    #     outfields = queryParameter.outfields     #outfields    (尚未考虑insr,outsr)
 
    #     features = []
    #     for item in results:                               
    #         x = item.get(layer.definition.x_field,0)
    #         y = item.get(layer.definition.y_field,0)
    #         shape=[x,y]
    #         print shape
    #         item.pop(layer.definition.x_field)         #感觉此方法不好，可能影响后续很多操作和查询
    #         item.pop(layer.definition.y_field)
    #         item.update({"shape":shape})               #将x,y放在一个列表里
    #         if extent.contain([x,y]):                  #过滤bbox
    #             features.append(item)       

    #     import re                                          #过滤where条件
    #     p=re.compile(r'\[(\w+)\]')
    #     para = p.findall(where)
    #     n=len(str(para))
    #     filter_where = eval("lambda record:record.get('%s')%s"%(para[0],where[n-2:]))
    #     features=filter(filter_where,features)


    #     if outfields[0] is not "*":
    #         map(lambda x:keys_copy.remove(x),outfields)  #剩下要删除的键
    #         for i in xrange(len(features)):
    #             for key in keys_copy:
    #                 features[i].pop(key)    #删除对应的键值

    #     last_features=reduce(lambda x,y:x+y,map(lambda x:[x.values()],features))   #去除键，重新组织键值 

    #     aliases_dict = layer.definition.aliases
    #     aliases_dict_keys = aliases_dict.keys()
    #     for key in keys_copy:
    #         if key in aliases_dict_keys:
    #             aliases_dict.pop(key)   #删除对应的别名键值

    #     return aliases_dict,last_features



      