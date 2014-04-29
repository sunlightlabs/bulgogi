var testvar1,
    testvar2,
    testvar3;

var country_data = {};
var sub_regions = {};
var centeredRegion;
var focusedCountry;
var info;

//var target_domain = 'http://realtime.influenceexplorer.com'
var target_domain = 'http://foreign.influenceexplorer.com'

//TODO: dispatch for zoom events

var colors = {
        "country": {
            "default" : "rgb(238, 212, 117)",
            "highlighted" : "rgb(227, 186, 34)",
            },
        "ocean": "rgba(105,165,159,.17)",
        "subRegion" : {
            "default" : "rgba(207, 207, 202, 1)",
            "highlighted" : "rgba(168, 168, 160, 1)",
            }
}

var dispatch = d3.dispatch(     "clickSubRegion", 
                                "clickCountry", 
                                "mouseoverSubRegion", 
                                "mouseoverCountry", 
                                "mouseoutSubRegion", 
                                "mouseoutCountry", 
                                "resetZoom");

function initializeMap() {

    var color_map = {
                        "unrecognized": colors.subRegion.default,
                        "defaultFill": colors.country.default
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

    country_data['-99'] = {'fillKey': 'unrecognized'};

    var faraMap = new Datamap({
        element: document.getElementById('fara_map'),
        scope: 'world',
        projection: 'equirectangular',
        geographyConfig: {
            highlightBorderColor: '#FFFFFF',
            popupOnHover: false,
            highlightOnHover: true,
            //highlightFillColor: function(d) { return d3.select(this).style('fill'); },
            highlightFillColor: colors.country.highlighted,
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
            datamap.svg.style("background-color", "rgba(105,165,159,.17)");
            map_height = datamap.options.element.clientHeight;
            map_width = datamap.options.element.clientWidth;
            //datamap.svg.selectAll('.datamaps-subunit')
            //   .on('mouseover', function(d){ dispatch.mouseoverCountry(d);})
            //   .on('mouseout', function(d){ dispatch.mouseoutCountry(d);});

            
            var region_fill = datamap.addLayer( "fara-region-fill", "fara-region-fill", false);
            //var region_boundary = datamap.addLayer( "fara-region-boundary", null, false);
            var meta_layer = datamap.addLayer( "meta-layer", null, false);
            var map_layer = d3.select('.datamaps-subunits');
                
            d3.select("g.datamaps-subunits")
                .style("pointer-events","none")
                .style("cursor","pointer"); 

            var resetZoomButton = meta_layer.append('g')
                                        .attr('id','resetZoomButton')
                                        .style('visibility','hidden')
                                        .style('cursor','pointer')
                                        .on("click", function(d){ dispatch.resetZoom();});

            resetZoomButton.append('rect')
                .attr('x',10)
                .attr('y',10)
                .attr('rx',5)
                .attr('ry',5)
                .style('fill', '#0a6e92')
                .style('padding', '5px')
                .attr('height',40)
                .attr('width',40);

            resetZoomButton.append('path')
                .attr('d', "m 12.015625,12.015625 8,0 0,8.00001 -8,0 z M 23.95625,32 32,32 l 0,-8.04062 -1.97812,3.04999 -6.00625,-6.99375 0,4 -4,0 6.99374,6.00626 z m 0.05938,-19.98438 5.975,-7.1125 L 32,7.9875 32,0 23.95938,0 27.025,1.97187 l -7.00937,6.04375 4,0 z M 7.9875,0 0,0 0,7.9875 1.95313,4.96562 l 6.0625,7.05 0,-4 4,0 -7.05,-6.0625 z M 0,23.95938 0,32 l 7.98438,0 -3.08125,-2.00937 7.1125,-5.97501 -4,0 0,-4 -6.04375,7.00938 z")
                .attr('transform','translate(14,14)')
                .style('fill','#ffffff');

            function showCountryLabel(d) {
                if (d) {
                   d3.select('text.'+d.id).style("visibility","visible");
                }
            }
                   
            function hideCountryLabel(d) {
                if (d) {
                   d3.select('text.'+d.id).style("visibility","hidden");
                }
            }

            dispatch.on("mouseoverCountry", function(d){
                //d3.select('.datamaps-subunit.'+d.id)
                //  .style('stroke', 'black');
                //console.log('called');
                if (d && d !== focusedCountry){
                    showCountryLabel(d);
                }
            });
            
            dispatch.on("mouseoutCountry", function(d){
                //d3.select('.datamaps-subunit.'+d.id)
                //  .style('stroke', 'white');
                if (d && d !== focusedCountry){
                    hideCountryLabel(d);
                }
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
                centeredRegion = null; 

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

              if (centeredRegion) {
                d3.select('#fara-region-fill path[data-subregion-id="'+centeredRegion.id+'"]').style("visibility", "visible");
              }

              if (d && centeredRegion !== d) {
                d3.select('#fara-region-fill path[data-subregion-id="'+d.id+'"]').style("visibility", "hidden");
                d3.select("g.datamaps-subunits").style("pointer-events","auto"); 
                testvar2 = d;
                var centroid = datamap.path.centroid(d.selection);
                var bounds = datamap.path.bounds(d.selection);
                x = centroid[0];
                y = centroid[1];
                k = optimizeZoom(bounds, centroid, map_height, map_width);
                centeredRegion = d;
              } else {
                d3.select("g.datamaps-subunits").style("pointer-events","none"); 
                x = map_width / 2;
                y = map_height / 2;
                k = 1;
                centeredRegion = null;
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

            function setInfoBoxTitle(string){
                    infoBoxTitle = d3.select('#infoBoxTitle');
                    infoBoxTitle.html('');
                    infoBoxTitle.append('h3')
                        .text(string);
            }
                    
            function setInfoBoxDetails(info){
                infoBoxDetails = d3.select('#infoBoxDetails');
                infoBoxDetails.html('');
                infoBoxDetails.append('span')
                        .classed('tip',true)
                        .text("Filings were found for the following locations:");
                if (info && info.locations) {
                    infoBoxDetails.append("ul")
                        .selectAll("li")
                        .data(info.locations)
                        .enter().append("li")
                            .append("a")
                            .attr("href", function(l) { return "location-profile/"+l.id;})
                            .text(function(l){ return l.name;});
                } else {
                    infoBoxDetails.append("p")
                        .text("No filings exist for this selection.") 
                }
            }

            function showCountryInfo(d) {
                fallbackName = d.properties.name;
                infoBox = d3.select("#infoBox");
                info = _.has(country_data, d.id) ? country_data[d.id] : null;
                if (info) {
                    setInfoBoxTitle(info.name);
                    setInfoBoxDetails(info);
                } else {
                    setInfoBoxTitle(fallbackName);
                    setInfoBoxDetails(info);
                }
            }

            function showRegionInfo(d){
                if (d && d === centeredRegion) {
                   setInfoBoxTitle('Select a Country');
                   infoBoxDetails = d3.select('#infoBoxDetails');
                   infoBoxDetails.html('');
                }
            }

            function defaultInfo(d) {
                setInfoBoxTitle('Select a Region')
                infoBoxDetails = d3.select('#infoBoxDetails');
                infoBoxDetails.html('');
                infoBoxDetails.append('span')
                        .classed('tip',true)
                        .text("Click on the map to find foreign influence information about the country or location.");
            }
                

            function changeInfo(d) {
                if (d && d === focusedCountry) {
                    //populateInfo(d);
                    showCountryInfo(d);
                } else if (d && d === centeredRegion) {
                    showRegionInfo(d);
                } else {
                    defaultInfo(d);
                }
            }

            function dehighlightCountry(d) {
                if (d) {
                    c = d3.select('.datamaps-subunit.'+d.id);
                    c.style('fill', colors.country.default);
                }
            }

            function highlightCountry(d) {
                c = d3.select('.datamaps-subunit.'+d.id);
                c.style('fill', colors.country.highlighted);
            }

            function dehighlightSubRegion(d) {
                if (d) {
                    d3.select('#fara-region-fill path[data-subregion-id="'+d.id+'"]')
                      .style('fill',colors.subRegion.default)
                }
            }

            function highlightSubRegion(d) {
                if (d) {
                    d3.select('#fara-region-fill path[data-subregion-id="'+d.id+'"]')
                      .style('fill',colors.subRegion.highlighted)
                }
            }

            function changeFocusedCountry(d) {
                // unfocus last focused country
                dehighlightCountry(focusedCountry);
                hideCountryLabel(focusedCountry);
                if (d && d !== focusedCountry) {
                    // focus new focused country
                    highlightCountry(d);
                    showCountryLabel(d);
                    focusedCountry = d;
                    changeInfo(d);
                } else {
                    focusedCountry = null;
                    changeInfo(d);
                }
            }

            dispatch.on("clickSubRegion", function(d){ clickZoom(d); changeInfo(d); resetZoomButton.style('visibility','visible'); });
            dispatch.on("clickCountry", function(d){ if (d !== focusedCountry) {changeFocusedCountry(d);}});
            dispatch.on("resetZoom", function(){ clickZoom(null); resetZoomButton.style('visibility','hidden'); changeFocusedCountry(null)});
            
            dispatch.on("mouseoverSubRegion", function(d){ 
                highlightSubRegion(d);
            })
            dispatch.on("mouseoutSubRegion", function(d){ 
                dehighlightSubRegion(d); 
            })

            testvar1 = datamap;
            datamap.svg.selectAll('.datamaps-subunit').on('click', function(d) { dispatch.clickCountry(d); });
            
            //var region_colors = d3.scale.category20().domain(_.keys(_.pluck(sub_regions, 'id')));

            var country_featureset = topojson.feature(datamap.worldTopo, datamap.worldTopo.objects.world);
            _.each(sub_regions, function(sub_region){
                var filtered_features;

                filtered_features = country_featureset.features.filter(
                    function(d) { 
                        three_letter_codes = _.pluck(sub_region.countries, 'alpha-3');
                        return _.indexOf(three_letter_codes, d.id) >= 0; 
                    });

                var selection = {  type: "FeatureCollection",
                                    features: filtered_features};

                sub_region.selection = selection;
            });

            region_fill.selectAll("path")
                .data(sub_regions)
                .enter().append("path")
                .classed('subregion',true)
                .style("fill", colors.subRegion.default)
                .style("stroke", "none")
                .style("stroke-width", "0px")
                .style("cursor", "pointer")
                .attr("d", function(d){ return datamap.path(d.selection);})
                .attr("data-subregion-id", function(d) { return d.id; })
                .on("mouseover", function(d){ dispatch.mouseoverSubRegion(d);})
                .on("mouseout", function(d){ dispatch.mouseoutSubRegion(d);})
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
                            return _.indexOf(alpha_codes, country_code) >= 0;
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



