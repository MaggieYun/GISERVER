/**
 * @author 刘荣涛
 * 2013.6.16
 * 修改：许照云 2013.10.9
 */
OpenLayers.Layer.ExDyLayer2 = OpenLayers.Class(OpenLayers.Layer.Grid,{
    
    singleTile: true,
    ratio: 1,
    wrapDateLine: true,
    
    url:null,
    queryURL:null,
    where:null,//是否有where条件用于export
    
    features:[],
    
    initialize: function(name, url, options) {
        OpenLayers.Layer.Grid.prototype.initialize.apply(this, [
            name || this.name, url || this.url, {}, options
        ]); 
        
        this.where = options['where']||'1=2';
        this.outfields = options['outfields']||'*';
        this.format = options['format']||'GEOJSON';
        this.spatialRel = options['spatialRel']||'contains';

        this.buffer = options['buffer']||0; //新增该参数，待验证

        this.geometry = options['geometry']||0;
        
        this.exp = {
            where: this.where,
            outfields: this.outfields,
            format:this.format,
            spatialRel:this.spatialRel,
            buffer:this.buffer, //新增该参数，待验证
            geometry:this.geometry
        };
        this.features = [];
    },
    
    destroy: function(){
        OpenLayers.Layer.Grid.prototype.destroy.apply(this, arguments); 
        this.exp = null;
        this.features = null;
    },
    
    getURL: function (value) {
        if(!this.sr){
            this.exp['inSR']  = this.map.projection.split(':')[1];
            this.exp['outSR'] = this.exp['inSR'];
        }
        
        var bounds = this.adjustBounds(value);
        var geometry = bounds.left + "," + bounds.bottom + "," + bounds.right + "," + bounds.top;

        var size = this.getImageSize();
        
        this.exp['geometry'] = this.geometry || geometry;

        this.exp['extent'] = geometry; //即为bbox
        
        this.exp['size'] = size.w + "," + size.h;
       
        var url = this.url + "export?" + this.gen_get_param(this.exp);

        this.query();
        
        return url;
    },
    
    gen_get_param: function(data){
        var r = [];
        for(var key in data){
            var val = data[key];
            if(typeof val !== 'function' && typeof val !== 'object'){
                r.push(key + '=' + val);
            }
        }
        return r.join('&');
    },

    // get_query_url:function(){
    //     return this.url + "query?" + this.gen_get_param(this.exp);
    // },
    
    query:function(){
        if(this.jsonLoading){
            return;
        }
        
        this.jsonLoading = true;
        
        this.features = [];
        
        var url = this.url + "query?" + this.gen_get_param(this.exp);

        this.queryURL = this.url + "query?where=" + this.where
                        +"&outfields="+this.outfields
                        // +"&buffer="+this.buffer
                        // +"&geometry="+this.geometry
                        +"&inSR="+this.exp['inSR']
                        +"&outSR="+this.exp['outSR'];

        $.ajax({
            url: url,
            dataType:'JSONP',
            context: this,
            success: function(data){
                this.jsonLoading = false;
                var geojson = new OpenLayers.Format.GeoJSON();
                this.features = geojson.read(data);
                this.events.triggerEvent('featurtesloaded', {features: this.features});
            }
        });
    },
    
    setWhere: function(val){
        this.where = val;
        this.exp['where'] = val;
        this.redraw();
    },

    /**
    *针对徐州项目，态势监控页面，获取表单数据，定制的方法
    *只做query请求，不export请求，不绘图
    */
    getFeatures: function(options){

        var where = options['where']||'1=1';
        var outfields = options['outfields']||'*';
        var format = options['format']||'GEOJSON';
        var spatialRel = options['spatialRel']||'contains';

        // var geometry = options['geometry']||'116,33,119,35'; //暂且只考虑该坐标

        var geometry = options['geometry']||'global';//请求所有坐标数据，特殊情况
        var buffer = options['buffer']||0;

        var url = this.url + 'query';

        var params = {
            where: where,
            geometry: geometry,
            buffer:buffer,
            spatialRel: spatialRel,
            outfields: outfields,
            inSR: this.exp['inSR'],
            outSR: this.exp['outSR']
        };

        $.ajax({
            url: url,
            dataType:'jsonp',
            method: 'POST',
            data: params,
            context: this,
            success: function(data){
                // console.log(data.features);
                this.events.triggerEvent('getFeaturesDown', {features: data.features});
            },
            error: function(){
                console.log(arguments);
            }
        });




    },


    
    CLASS_NAME: "OpenLayers.Layer.ExDyLayer2"
});
