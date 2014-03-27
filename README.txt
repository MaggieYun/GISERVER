2013.10.16
使用注意事项：
1、在configs文件夹中创建对应map(或layer)的.ini配置文件，配置文件一定要.ini格式。假设文件为A.ini。
2、在configs文件夹中创建于.ini文件同名的文件夹（A），在该文件夹中创建.xml文件（假设为B.xml），用于配置图层的样式。
3、配置文件的书写格式和配置项可参考现有配置文件。
4、启动服务后，服务地址即为：'http://机器ip地址:6666/giserver2013/configs/A/'。
5、配置文件中在[styles]的配置项中指向对应的xml文件。即：
[styles]
style = B.xml






5、在前段js文件中加载地图时的配置有：
必选参数：url：'http://机器ip地址:6666/giserver2013/configs/A/'
可选参数：
>  where：任意的合法的SQL语句，可包含中文。eg："roadname='东大街'"
>  outfields：可以为'*',表示全选；可以是任意数据库中字段的组合；一定要是数据库中已有的字段；大小写随意不受限制             ；字段中一定要包含xml文件中涉及到的字段；字段中是否包含空间字段或经纬度字段都可以。
>  format:可选值为'GEOJSON'、'JSON'。默认值为'GEOJSON'。
>  spatialRel:一般该处默认用contains。可选值有：intersects、contains、crosses、touches（overlaps和within不通用		）

6、用户在进行空间查询，拼接url参数时，url参数中除了包含以上字段外，还有：
inSR
outSR
geometry： 即传统意义的bbox参数，是bbox的扩展。可以为bbox（4个参数，两对坐标组成的数组）；可以为wkt标准的		geometry对象。


！！！geometry特殊说明，因徐州项目，态势监控页面，表单数据利用地图服务query请求数据，为了取出数据库中任意合法或不合法的地理数据，给geometry参数增加了一个'global'合法参数值，该参数只在普通数据库中有效，空间数据库无效。

buffer 单位为米

7、export请求比query请求多2个参数：size和extent(bbox),如果请求时的geometry不为wkt，则extent参数与geometry参数相同。
