OpenLayers.Control.DyLayerSelect = OpenLayers.Class(
    OpenLayers.Control.Button, 
    {
        type: OpenLayers.Control.TYPE_TOOL,
        
        _t: null,
        
        initialize: function (layer, options) {
            OpenLayers.Util.extend(this, options);
            
            OpenLayers.Control.prototype.initialize.apply(this,[options]);
            
            this.layer = layer;
            
            if(!this.targets){
                this.targets = [];
            }
            
            if (!(OpenLayers.Util.isArray(this.targets))) {
                this.targets = [this.targets];
            }
            
        },
        
        setMap: function(map) {
            OpenLayers.Control.prototype.setMap.apply(this,arguments);
            this.initTip();
        },
        
        initTip: function(){
            this.tip = OpenLayers.Util.createDiv(this.id);
            this.tip.className = 'feature-tip';
            this.tip.setAttribute("unselectable", "on", 0);
            this.tip.onselectstart = OpenLayers.Function.False;
            this.map.viewPortDiv.appendChild(this.tip);
        },
        
        hover: function(){
            var arg = arguments, self = this;
            self.currentFeature = null;
            self.tip.style.display = 'none';
            this.map.viewPortDiv.style.cursor = 'default';
            clearTimeout(this._t);

            var m = arg[0].xy;
            var lonlat = self.map.getLonLatFromViewPortPx(m);
            var geometry = new OpenLayers.Geometry.Point(lonlat.lon,lonlat.lat);
            var geojson = new OpenLayers.Format.GeoJSON();

            this._t = setTimeout(function(){
                for(var j=0,l = self.targets.length; j < l; j++){
                    var layer = self.targets[j];

                    //根据当前缩放等级，固定一个像素值，将像素转换为实际距离
                    var bfr = 0.009*self.map.getScale();//固定缓冲像素为0.01pixels
                    var url = layer.queryURL + '&spatialRel=intersects&geometry='
                            + geometry.toString() + '&buffer='+bfr;

                    $.ajax({
                        url: url,
                        dataType:'JSONP',
                        success: function(data){ 
                            var features = geojson.read(data);
                            if (features[0]){
                                var feature = features[0]; //该处只做简单处理，可优化
                                feature.style = OpenLayers.Feature.Vector.style['SELECT'];
                                self.currentFeature = new OpenLayers.Feature.Vector(feature.geometry,
                                                                                    feature.attributes,
                                                                                    feature.style);                          
                                self.map.viewPortDiv.style.cursor = 'pointer';
                                if(!feature.lonlat){
                                    var centroid = feature.geometry.getCentroid();  //点要素也统一处理
                                    feature.lonlat = new OpenLayers.LonLat([centroid.x,centroid.y]);
                                    self.currentFeature.guid = centroid.x + '-' + centroid.y;
                     
                                }
                                var pixel = self.map.getPixelFromLonLat(feature.lonlat);
                                self.tip.style.left = (pixel.x + 10) + 'px';
                                self.tip.style.top = (pixel.y - 10) + 'px';
                                self.tip.innerHTML = feature.attributes.TIP||'空';
                                self.tip.style.display = 'block';

                                //线、面要素的tip显示在鼠标附近是否更佳？
                            }
                            
                        }
                    });
                }
            },200);
        },
        
        click: function(){
            var ft = this.currentFeature;
            if(!ft) return;
            
            this.map.events.triggerEvent('feature:click', {feature: ft});

            var centroid = ft.geometry.getCentroid(); 
            var guid = centroid.x + '-' + centroid.y;

            var exsit = this.layer.getFeatureBy('guid',guid);
            
            if(exsit){
                this.layer.removeFeatures([exsit]);
                return;
            }
            this.layer.addFeatures([ft]);
            
        },
        
        activate: function(){
            OpenLayers.Control.prototype.activate.apply(this);
            this.map.events.register('mousemove', this, this.hover);
            this.map.events.register('click', this, this.click);
        },
        
        deactivate: function(){
            OpenLayers.Control.prototype.deactivate.apply(this);
            this.map.events.unregister('mousemove', this, this.hover);
            this.map.events.unregister('click', this, this.click);
        },
        
        setTargets: function(targets){
            this.targets = targets;
        },
        
        CLASS_NAME: "OpenLayers.Control.DyLayerSelect"
    }
);

OpenLayers.Control.ExSelectFeature2 = OpenLayers.Class(
    OpenLayers.Control.Panel, {

    buffer: 500,
    isBufferDraw:false,//表示缓冲区是否绘制
    initialize: function(layer,options) {
        OpenLayers.Control.Panel.prototype.initialize.apply(this, [options]);
        
        this.resultLayer =  layer;

        var layer = this.vector = new OpenLayers.Layer.Vector("edit",{displayInLayerSwitcher:false});
        
        var onFeatureadded = function(event){
            
            this.activateControl(this.dySelCtl);
            
            //删除结果图层上的数据
            this.resultLayer.removeAllFeatures();
            layer.removeAllFeatures();
            layer.addFeatures([event.feature],{silent:true});

            this.isBufferDraw = false;
            var feature = event.feature;
            var geometry = feature.geometry;

            var geojson = new OpenLayers.Format.GeoJSON();
            var self = this;

            if(geometry.CLASS_NAME == "OpenLayers.Geometry.LineString"){
                this.targets.forEach(function(layer){
                    var url = layer.queryURL + '&spatialRel=intersects&geometry='
                            + geometry.toString() + '&buffer='+self.buffer ;
                    $.ajax({
                        url: url,
                        dataType:'JSONP',
                        success: function(data){
                            if(!self.isBufferDraw){ //确保多个动态图层，但缓冲区只绘制一遍。
                                bufferFeature = new OpenLayers.Format.WKT().read(data.bufferArea);
                                self.resultLayer.addFeatures([bufferFeature]); 
                                self.isBufferDraw = true;
                            }
                            
                            var features = geojson.read(data);
                            features.forEach(function(feature){
                                feature.style = OpenLayers.Feature.Vector.style['SELECT'];

                                var centroid = feature.geometry.getCentroid();  //点要素也统一处理
                                feature.guid = centroid.x + '-' + centroid.y;
                            });
                            self.resultLayer.addFeatures(features);
                        }
                    });   
                });
                

            }else if(geometry.CLASS_NAME == "OpenLayers.Geometry.Polygon"){
                this.targets.forEach(function(layer){
                    var url = layer.queryURL + '&spatialRel=intersects&geometry='
                            + geometry.toString();
                    $.ajax({
                        url: url,
                        dataType:'JSONP',
                        success: function(data){
                            var features = geojson.read(data);
                            features.forEach(function(feature){
                                feature.style = OpenLayers.Feature.Vector.style['SELECT'];

                                var centroid = feature.geometry.getCentroid();  //点要素也统一处理
                                feature.guid = centroid.x + '-' + centroid.y;
                            });
                            self.resultLayer.addFeatures(features);
                        }
                    });
                });
            }  

        };
        
        layer.events.register('featureadded', this, onFeatureadded);
        
        this.dySelCtl =  new OpenLayers.Control.DyLayerSelect(this.resultLayer,{
            displayClass: 'olControlDrawFeaturePoint'
        });
        
        this.pathCtl = new OpenLayers.Control.DrawFeature(layer, OpenLayers.Handler.Path, {
            displayClass: 'olControlDrawFeaturePath',
            handlerOptions: {citeCompliant: this.citeCompliant}
        });
        
        this.polygonCtl = new OpenLayers.Control.DrawFeature(layer, OpenLayers.Handler.Polygon, {
            displayClass: 'olControlDrawFeaturePolygon',
            handlerOptions: {citeCompliant: this.citeCompliant}
        });
        
        var controls = [
            this.dySelCtl,
            this.pathCtl,
            this.polygonCtl
//            ,new OpenLayers.Control.DrawFeature(layer, OpenLayers.Handler.RegularPolygon, {
//                displayClass: 'olControlDrawFeatureRegularPolygon',
//                handlerOptions: {citeCompliant: this.citeCompliant,sides: 4}
//            })
        ];
        
        this.addControls(controls);
    },
    
    setTargets: function(targets){
        this.targets = targets;
        this.dySelCtl.setTargets(targets);
    },
    
    setMap: function(map){
        OpenLayers.Control.Panel.prototype.setMap.apply(this, arguments);
        map.addLayer(this.vector);
        map.setLayerIndex(this.vector, 0);
    },
    
    draw: function() {
        var div = OpenLayers.Control.Panel.prototype.draw.apply(this, arguments);
        if (this.defaultControl === null) {
            this.defaultControl = this.controls[0];
        }
        return div;
    },

    CLASS_NAME: "OpenLayers.Control.EditingToolbar"
});    
