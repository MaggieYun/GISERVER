#coding=utf-8
#author 许照云
class Extent:
    def __init__(self,bbox):
        self.bbox = bbox
        self.xmin = bbox[0]
        self.ymin = bbox[1]
        self.xmax = bbox[2]
        self.ymax = bbox[3]        

    def contain(self,point):  
        "@point 2-list:[x,y]"
        if ((self.xmin<=point[0]<=self.xmax) and (self.ymin<=point[1]<=self.ymax)):
            return True
        else:
            return False

    def toText(self):  #查找方法将bbox对象直接转换为wkt要求的text
        temp = (self.xmin,self.ymin,
                self.xmax,self.ymin,
                self.xmax,self.ymax,
                self.xmin,self.ymax,
                self.xmin,self.ymin)
        return "'Polygon((%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f))'"%temp

    def toWKT(self):
        temp = (self.xmin,self.ymin,
                self.xmax,self.ymin,
                self.xmax,self.ymax,
                self.xmin,self.ymax,
                self.xmin,self.ymin)
        return "Polygon((%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f))"%temp

