#coding=utf-8
#author 许照云
import os,sys
from sqlalchemy import create_engine


class Validation():

    #普通数据库验证语句（oracle）
    VIEW_SQL = "select * from user_views where view_name = upper('%s')"
    TABLE_SQL = "select * from user_tables where table_name = upper('%s')"
    PRIMARY_SQL = "select column_name from user_cons_columns where table_name = upper('%s') and position is not null"
    COLUMN_SQL = "select column_name from cols  WHERE TABLE_name=upper('%s')"

    #空间数据库验证语句（postgresql）
    TABLE_VIEW_SQL_SPATIAL = "select * from %s"  #查询表或视图不用区分
    PRIMARY_SQL_SPATIAL = "select pg_constraint.conname as pk_name from pg_constraint  inner join pg_class on pg_constraint.conrelid = pg_class.oid where pg_class.relname = '%s' and pg_constraint.contype='p'" 
    #表
    TABLE_COLUMN_SQL_SPATIAL = "select column_name from information_schema.columns WHERE table_name = '%s'"  #以后表名全部大写
    #视图 该语句有待验证
    VIEW_COLUMN_SQL_SPATIAL = "select column_name from information_schema.columns WHERE view_name = '%s'"  #以后表名全部大写




    '''
    依赖于http://www.sqlalchemy.org/
    '''
    def __init__(self,ini):
        self.ini = ini
        self.database = ini.database

        self.db = self.database.dbname+'://'+self.database.user+':'+str(self.database.psw)+'@'+str(self.database.host)+':'+str(self.database.port)+'/'+self.database.name
        # print self.db
        self.engine = create_engine(self.db)

        
        self.errors = self.validate()
        print self.errors

    
    # def connect():
    #     self.conn = self.engine.connect() #self.engine验证通过

    # def get_table_names():
    #     pass

    # def get_view_names():
    #     pass

    # def get_cloumns_names(table_name):
    #     pass 



    def validate(self):
        '''
        errors一次性统计尽量多的错误用于显示
        '''
        errors = []  #存放所有错误信息
        print "start validate---------------"
        try:
            self.conn = self.engine.connect() #self.engine验证通过
            errors=self.assist_validate(errors) 
            self.conn.close()#关闭数据库连接
        except:
            raise
            s = "can't create_engine:%s"%self.db 
            errors.append(s)
        return errors  



        

    def assist_validate(self,errors):
        '''
        辅助判断
        '''
        if (self.database.host == 'oracle'): #普通数据库 有待修改
            sql_view = Validation.VIEW_SQL %self.ini.scheme_name   #查询视图是否存在
            sql_table = Validation.TABLE_SQL %self.ini.scheme_name   #查询表是否存在
            sql_p = Validation.PRIMARY_SQL %self.ini.scheme_name #查询主键字段名
            sql_col = Validation.COLUMN_SQL %self.ini.scheme_name   #查看字段名（与数据类型）是否存在
            
            if self.ini.scheme_type == 0:  #视图
                results = self.conn.execute(sql_view)
            elif self.ini.scheme_type == 1:  #表   
                results = self.conn.execute(sql_table)
            val = results.fetchone()

            if val is not None:   #self.scheme_name验证通过
                print "scheme_name pass"
                p_results = self.conn.execute(sql_p)  
                p_val = p_results.fetchone()
                xy_results = self.conn.execute(sql_col)  
                xy_val = map(str,reduce(lambda x,y:x+y,map(list,xy_results.fetchall())))
                if p_val is None:
                    s = "p_field is wrong,%s has no primary key"%self.ini.scheme_name
                    errors.append(s)
                else:    
                    if (p_val[0] == self.ini.p_field):  #self.p_field通过验证
                        print "p_field pass"
                    else:
                        s = "'p_field' is wrong"  
                        errors.append(s)

                    if self.ini.g_field in xy_val:
                        print "g_field pass"
                        return errors

                    if self.ini.x_field in xy_val:  #self.x_field通过验证
                        # self.geometryType = "point"
                        print "x_field pass"
                    else:
                        s =  "x_field is wrong"  
                        errors.append(s)   

                    if self.ini.y_field in xy_val: #self.y_field通过验证
                        print "y_field pass"
                    else:
                        s = "y_field is wrong"  
                        errors.append(s)           
            else:
                s = "'scheme_name' is wrong"    
                errors.append(s) 


        elif (self.database.host == 'postgresql'):  #空间数据库
            sql_table_view = Validation.TABLE_VIEW_SQL_SPATIAL %self.ini.scheme_name   #查询视图是否存在
            sql_p = Validation.PRIMARY_SQL_SPATIAL %self.ini.scheme_name #查询主键字段名
            sql_col_table = Validation.TABLE_COLUMN_SQL_SPATIAL %self.ini.scheme_name   
            sql_col_view = Validation.VIEW_COLUMN_SQL_SPATIAL %self.ini.scheme_name   

            results = self.conn.execute(sql_table_view) #表或视图语句相同

            val = results.fetchone()

            if val is not None:   #self.scheme_name验证通过
                print "scheme_name pass"
                p_results = self.conn.execute(sql_p)  
                p_val = p_results.fetchone()

                if self.ini.scheme_type == 0:  #视图
                    column_results = self.conn.execute(sql_col_view)
                elif self.ini.scheme_type == 1:  #表   
                    column_results = self.conn.execute(sql_col_table)

                column_val = map(str,reduce(lambda x,y:x+y,map(list,column_results.fetchall())))

                if p_val is None:
                    s = "p_field is wrong,%s has no primary key"%self.ini.scheme_name
                    errors.append(s)
                else:  
                    if (str(p_val[0]) == self.ini.p_field):  #self.p_field通过验证
                        print "p_field pass"
                    else: 
                        s = "'p_field' is wrong" 
                        errors.append(s)

                    if self.ini.g_field in column_val:
                        print "g_field pass"
                        return errors

                    if self.ini.x_field in column_val:  #self.x_field通过验证
                        # self.geometryType = "point"
                        print "x_field pass"
                    else:
                        s =  "x_field is wrong"  
                        errors.append(s)   

                    if self.ini.y_field in column_val: #self.y_field通过验证
                        print "y_field pass"
                    else:
                        s = "y_field is wrong"  
                        errors.append(s)           
            else:
                s = "'scheme_name' is wrong"    
                errors.append(s) 


        return errors                 




