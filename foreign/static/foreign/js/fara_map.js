var testvar1,
    testvar2,
    testvar3;

var country_data = {};
var sub_regions = {};
var centered;
var focusedCountry;
var info;

//var target_domain = 'http://realtime.influenceexplorer.com'
var target_domain = 'http://foreign.influenceexplorer.com'

//TODO: dispatch for zoom events


var dispatch = d3.dispatch(     "clickSubRegion", 
                                "clickCountry", 
                                "mouseoverSubRegion", 
                                "mouseoverCountry", 
                                "mouseoutSubRegion", 
                                "mouseoutCountry", 
                                "resetZoom");

function initializeMap() {

    var color_map = {
                        'ONE': "#5C8100",
                        'MORE': "#0C4E00",
                        'defaultFill': "#E5E2E0"
                    };

    _.each(_.keys(country_data), function(k) {
        if (country_data.locations) {
            if (country_data[k].locations.length === 1){
                country_data[k].fillKey = 'ONE';
            } else if (country_data[k].locations.length > 1){
                country_data[k].fillKey = 'MORE';
            }
        } else {
            country_data[k].fillKey = null;
        }
    });

    var faraMap = new Datamap({
        element: document.getElementById('fara_map'),
        scope: 'world',
        projection: 'equirectangular',
        geographyConfig: {
            highlightBorderColor: '#000000',
            popupOnHover: false,
            highlightOnHover: true,
            highlightFillColor: function(d) { return d3.select(this).style('fill'); },
            /*
             popupTemplate: function(geography, data) {
                // TODO: make sure this isn't clashing with IE css
                var content = '<div class="hoverinfo">';
                var close_tag = '';
                content += '<strong>'+ geography.properties.name + '</strong>';
                if (data !== null && data.locations) {
                    content += '<hr/>';
                    if (data.locations.length > 0) {
                        content += '<ul>';
                        _.each(data.locations, function(location) {
                            content += '<li><a href="'+ target_domain +'/location-profile/';
                            content += location.id +'">';
                            content += location.name +'</a></li>';
                            });
                        close_tag = '</ul>';
                    }
                    content += close_tag + '</div>';
                }
                return content;
            },
            */
            highlightBorderWidth: 1
        },
        fills: color_map,
        data: country_data,
        done: function(datamap) {
            map_height = datamap.options.element.clientHeight;
            map_width = datamap.options.element.clientWidth;
            //datamap.svg.selectAll('.datamaps-subunit')
            //   .on('mouseover', function(d){ dispatch.mouseoverCountry(d);})
            //   .on('mouseout', function(d){ dispatch.mouseoutCountry(d);});

            
            var region_fill = datamap.addLayer( "fara-region-fill", "fara-region-fill", false);
            //var region_boundary = datamap.addLayer( "fara-region-boundary", null, false);
            var meta_layer = datamap.addLayer( "meta-layer", null, false);
            var map_layer = d3.select('.datamaps-subunits');
                
            d3.select("g.datamaps-subunits").style("pointer-events","none"); 

            var resetZoomButton = meta_layer.append('g')
                                        .attr('id','resetZoomButton')
                                        .style('visibility','hidden')
                                        .on("click", function(d){ dispatch.resetZoom();});

            resetZoomButton.append('rect')
                .attr('x',10)
                .attr('y',10)
                .attr('rx',5)
                .attr('ry',5)
                .style('fill', '#E5E2E0')
                .style('padding', '5px')
                .attr('height',40)
                .attr('width',100);

            resetZoomButton.append('text')
                .style('fill','#8E8883')
                .style('text-transform','uppercase')
                .attr('x',17)
                .attr('y',35)
                .text('zoom out');

            dispatch.on("mouseoverCountry", function(d){
                //d3.select('.datamaps-subunit.'+d.id)
                //  .style('stroke', 'black');
                //console.log('called');

                d3.select('text.'+d.id).style("visibility","visible");
            });
            
            dispatch.on("mouseoutCountry", function(d){
                //d3.select('.datamaps-subunit.'+d.id)
                //  .style('stroke', 'white');
                
                d3.select('text.'+d.id).style("visibility","hidden");
            }); 
                

            function optimizeZoom(selection_bounds, centroid, height, width){
                var step = 1;
                var zright = selection_bounds[1][0];
                var zleft = selection_bounds[0][0];
                var ztop = selection_bounds[0][1];
                var zbottom = selection_bounds[1][1];
                if (zleft <= 0) {
                    var dcent = zright - centroid[0];
                    zleft = centroid[0] - dcent;
                }
                selection_width = zright > zleft ? zright - zleft : zwidth - zleft;
                selection_height = zbottom > ztop ? zbottom - ztop : zheight - ztop;
                console.log(selection_bounds);
                console.log("top: "+ztop);
                console.log("bottom: "+zbottom);
                console.log("left: "+zleft);
                console.log("right: "+zright);
                var zoom_level = 1;
                selection_height = selection_height * 1.15;
                do
                  zoom_level += step
                while ((selection_width * (zoom_level + step) < width) && (selection_height * (zoom_level + step) < height));
                return zoom_level;
            }

            function resetZoom() {
                x = map_width / 2;
                y = map_height / 2;
                k = 1;
                centered = null; 

                d3.select("g.datamaps-subunits").transition()
                  .duration(750)
                  .attr("transform", "translate(" + map_width / 2 + "," + map_height / 2 + ")scale(" + k + ")translate(" + -x + "," + -y + ")")
                  .style("stroke-width", 1.5 / k + "px");
              
                d3.select("g.fara-region-fill").transition()
                  .duration(750)
                  .attr("transform", "translate(" + map_width / 2 + "," + map_height / 2 + ")scale(" + k + ")translate(" + -x + "," + -y + ")")
                  .style("stroke-width", 1.5 / k + "px");
                
            }

            function clickZoom(d) {
              var x, y, k;

              if (centered) {
                d3.select('#fara-region-fill path[data-subregion-id="'+centered.id+'"]').style("visibility", "visible");
              }

              if (d && centered !== d) {
                d3.select('#fara-region-fill path[data-subregion-id="'+d.id+'"]').style("visibility", "hidden");
                d3.select("g.datamaps-subunits").style("pointer-events","auto"); 
                testvar2 = d;
                var centroid = datamap.path.centroid(d.selection);
                var bounds = datamap.path.bounds(d.selection);
                x = centroid[0];
                y = centroid[1];
                k = optimizeZoom(bounds, centroid, map_height, map_width);
                centered = d;
              } else {
                d3.select("g.datamaps-subunits").style("pointer-events","none"); 
                x = map_width / 2;
                y = map_height / 2;
                k = 1;
                centered = null;
              }


              d3.select("g.datamaps-subunits").transition()
                  .duration(750)
                  .attr("transform", "translate(" + map_width / 2 + "," + map_height / 2 + ")scale(" + k + ")translate(" + -x + "," + -y + ")")
                  .style("stroke-width", 1.5 / k + "px");
              
              d3.select("g.fara-region-fill").transition()
                  .duration(750)
                  .attr("transform", "translate(" + map_width / 2 + "," + map_height / 2 + ")scale(" + k + ")translate(" + -x + "," + -y + ")")
                  .style("stroke-width", 1.5 / k + "px");
              
              d3.select("g.labels").transition()
                  .duration(750)
                  .attr("transform", "translate(" + map_width / 2 + "," + map_height / 2 + ")scale(" + k + ")translate(" + -x + "," + -y + ")")
                  .style("stroke-width", 1.5 / k + "px");

              d3.selectAll("g.labels text")
                .style('font-size', 1 / k + "em");

              datamap.options.geographyConfig.highlightBorderWidth = 1 / k;
              datamap.svg.selectAll('.datamaps-subunit').style('stroke-width', 1 / k);
            };

            function showInfo(d) {
                fallbackName = d.properties.name;
                infoBox = d3.select("#infoBox");
                info = _.has(country_data, d.id) ? country_data[d.id] : null;
                if (info && info.locations) {
                    infoBoxTitle = d3.select('#infoBoxTitle');
                    infoBoxTitle.html('');
                    infoBoxTitle.append('h3')
                        .text(info.name);
                    infoBoxDetails = d3.select('#infoBoxDetails');
                    infoBoxDetails.html('');
                    infoBoxDetails.append("ul")
                        .selectAll("li")
                        .data(info.locations)
                        .enter().append("li")
                            .append("a")
                            .attr("href", function(l) { return "location-profile/"+l.id;})
                            .text(function(l){ return l.name;});
                } else {
                    infoBoxTitle = d3.select('#infoBoxTitle');
                    infoBoxTitle.html('');
                    infoBoxTitle.append("h3")
                        .text(fallbackName);
                    infoBoxDetails = d3.select('#infoBoxDetails');
                    infoBoxDetails.html('');
                }
            }

            function toggleInfo(d) {
                if (d && d !== focusedCountry) {
                    //populateInfo(d);
                    showInfo(d);
                    focusedCountry = d;
                } else {
                    hideInfo(d);
                    focusedCountry = null;
                }
            }

            dispatch.on("clickSubRegion", function(d){ clickZoom(d); resetZoomButton.style('visibility','visible'); });
            dispatch.on("clickCountry", function(d){ toggleInfo(d);});
            dispatch.on("resetZoom", function(){ clickZoom(null); resetZoomButton.style('visibility','hidden');});

            testvar1 = datamap;
            datamap.svg.selectAll('.datamaps-subunit').on('click', function(d) { dispatch.clickCountry(d); });
            
            var region_colors = d3.scale.category20().domain(_.keys(_.pluck(sub_regions, 'id')));

            var country_featureset = topojson.feature(datamap.worldTopo, datamap.worldTopo.objects.world);
            _.each(sub_regions, function(sub_region){
                var filtered_features;

                filtered_features = country_featureset.features.filter(
                    function(d) { return _.indexOf(_.pluck(sub_region.countries, 'alpha-3'), d.id) >= 0; });

                var selection = {  type: "FeatureCollection",
                                    features: filtered_features};

                sub_region.selection = selection;
            });

            region_fill.selectAll("path")
                .data(sub_regions)
                .enter().append("path")
                .style("fill", function(d){ return region_colors(d.name); })
                .style("stroke", "none")
                .style("stroke-width", "0px")
                .attr("d", function(d){ return datamap.path(d.selection);})
                .attr("data-subregion-id", function(d) { return d.id; })
                .on("click", function(d){ dispatch.clickSubRegion(d);});
        
            datamap.labels({'fontSize':'1em'})
            d3.selectAll("g.labels text")
                .style('visibility', "hidden")
                .style('pointer-events', "none")
                .style('font-family', 'sans-serif');


        }

    });


};

(function() {
        var initializeCountryData = function(json_data){
            
            _.each(json_data, function(country){        
                country_data[country['alpha-3']] = country;
            });
        
            _.each(sub_regions, function(sub_region){
                sub_region['countries'] = _.where(json_data, {'sub-region-code': sub_region.id});
            });
        };

        var initializeRegionData = function(json_data){
            sub_regions = _.flatten(_.pluck(json_data.world.regions, 'subregions'));
        };

        var updateCountryData = function(fara_data){
                //testvar = fara_data ;
                var alpha_codes = _.keys(country_data);

                filtered_codes = _.filter(_.keys(fara_data), function(country_code){ 
                            return _.indexOf(alpha_codes, country_code) > 0;
                        })
                //console.log(filtered_codes);
                _.each(filtered_codes, function(country_code) {
                    country_data[country_code].locations = fara_data[country_code]     
                    });

                _.each(country_data, function(v,k,l) { if (v.region) {regions[v.region] = {"countries":[]};}; });


                _.each(country_data, function(v,k,l) {
                        if (v.region) {
                            regions[v.region].countries = regions[v.region].countries.concat(k);
                            regions[v.region].name = v.region;
                        }; });

        };

        var doneWithPages = function(collected_results) {
            updateCountryData(collected_results);
            initializeMap();
        };


        var collected_results = [];
        var json_data;
        var processPage = function(url) {
            $.getJSON(url, function(page) {
                results = page.results;
                doneWithPages(results);
              });
        };

        var loadData = function(country_data_url, region_data_url, fara_url) {
            $.getJSON(region_data_url, function(json_data) {
                initializeRegionData(json_data);
                $.getJSON(country_data_url, function(json_data) {
                    initializeCountryData(json_data);
                    processPage(fara_url);
                });
            });
        };
        
        var fara_url = "http://fara.sunlightlabs.com/api/map?key=8675threeoh9";

        loadData('static/foreign/data/country_ids.json', 'static/foreign/data/regions.json', fara_url);

})();



