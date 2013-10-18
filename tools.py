#coding=utf-8
#author 许照云
from functools import partial
import pyproj

toMerctor = partial(
        pyproj.transform,
        pyproj.Proj("+init=epsg:4326"),
        pyproj.Proj("+init=epsg:3857"))

toLonLat = partial(
        pyproj.transform,
        pyproj.Proj("+init=epsg:3857"),
        pyproj.Proj("+init=epsg:4326"))


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
        return val.encode('utf-8')
    else:
        return val  
