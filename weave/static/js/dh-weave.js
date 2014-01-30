/*WEAVE JS tools, requires Jquery
 * requires XML.ObjTree http://www.kawa.net/works/js/xml/objtree-e.html*/
var DHWEAVE = DHWEAVE || {};

DHWEAVE.Settings = {
	baseUrl:'',
	WObj:null,
	callbacks : [],
	apiready: false
}

extend(DHWEAVE, {
	getCurrentViz:function(){
		var self = this;
		var g = $GET(window.location.search);
		if(g.hasOwnProperty('file')){
			if(g.file !== 'default.xml'){
				return g.file;
			}else{
				return g.cc;
			}
		}
	},
	getEmbedCode:function(viz){
		var self = this;
		if(typeof viz == 'undefined'){
			viz = self.getCurrentViz();
		}

		var code = "<!-- Begin Weave Code-->\n";
		code += '<script type="text/javascript" charset="utf-8">\n';
		code += '/* The Following variables are required!*/\n';
		code += "var DHW_HOST='%s';\n".replace(/%s/,  window.location.host);
		code += "var DHW_ID ='weave-container'; // this should be the 'id' of the div you want to use to contain the Weave Vizie\n";
		code += "var DHW_VIZ = '%s';\n".replace("%s", viz);
		code += '</script>\n';
		code += '<script src="http://%s/static/js/embed.js"></script>\n'.replace(/%s/, window.location.host);
		code += '<!-- end Weave Code-->';
		return code;
		
	},
	getWeaveStateKeys:function(){
		/*return a list of default weave session state items
		 * TODO: SHould this use path().getNames()?
		 * */
		var self = this;
		var ssKeys = [];
		var state = self.Settings.WObj.path().getState();
		for(var i in state){
			ssKeys.push(state[i].className)
		}
		return ssKeys;
	},
	updatePageFromHash:function(){
		/*a way to communicate back via the iframe*/
		var self = this;
		var h = window.location.hash.replace("#","").split("=");
		var action = h[0];
		var param = h[1];
		//var validKeys = self.getWeaveStateKeys();
		if(action==="lwf"){
			//load the weave file by the id
			self.loadClientConfig(param);
		}else if(action ==="swf"){
			self.saveClientConfig(param, function(data){
				if(data.status =="success-json"){
					if(data.action == 'create'){
						self.showMessage("Your Weave File has been saved");
					}else{
						self.showMessage("Your Weave File has been updated");
					}
				}
			});
		}else if(action==="acb"){
			self.addCallback(param);
		}	
	},
	updateWeaveFileName:function(name){
		/*Update the name of the weave file in the GUI*/
		$("#weave-file-name").html('<b>Current Weave File:</b> ' + name)
	},
    updateSessionDataSources:function(category_label, data){
        /*Update the Weave Datasources from well formated json*/
        var self = this;
        var output;
        output = "<hierarchy>%s</hierarchy>";
        var dataStr = "";
        var new_hierarchy = self.Settings.WObj.path().push(category_label).request('WeaveDataSource');
        var currObj;

        for(var prop in data){
                dataStr += '<category title="'+self.cleanCategoryTitle(prop)+'">';
                // now we have to create he nested categories
                currObj = data[prop];
                for(var prop in currObj){
                        dataStr += '<category title="'+self.cleanCategoryTitle(prop)+'">'; // this is the dataTable level
                        for(var attr in currObj[prop]){
                                var obj = currObj[prop][attr];
                                
                                dataStr += "<attribute";
                                for(var i in obj){
                                        dataStr +=' ' + i + '="' + obj[i] + '"';
                                }
                                dataStr += "/>";
                        
                        }
                        dataStr +="</category>"
                }

                dataStr +="</category>"

                
        }
        
        output = output.replace("%s", dataStr);
        output = output.replace(/<(?=\d)/g, "Less Than ");
        output = output.replace(/>(?=\d)/g, "Greater Than ");

        var newState = {
                attributeHierarchy : output
        }

        new_hierarchy.state(newState);

    },
	loadClientConfig:function(id){
		var self = this;
		var validKeys = ['weave.data.DataSources::WeaveDataSource']; // This is a list of weave session state objects we dont want to let the saved session state overwrite.
		//load the weave file by the id
		self.fetchClientConfig(id, function(data){
			var cleaned_data =[]; // We need to clean up old client configurations data sources.
			var match;
			self.updateWeaveFileName(data.cc_name);
			var data = data.content
			for(var i=0 in data){
				match = 0;
			
				for(var k in validKeys){
					if(data[i].className===validKeys[k]){
					
						match ++;
					}
				}
				if(match==0){
					cleaned_data.push(data[i]);
				}
			}
			self.clearTools()
			self.Settings.WObj.path().diff(cleaned_data);
				
		});
	},
	getToolsNames:function(){
		/* get a list of the tools in the weave sessions*/
		var self = this;
		var currState = self.Settings.WObj.path().getNames();
		var tools = [];
		for(var i in currState){
			if(currState[i].indexOf("Tool") != -1){
				tools.push(currState[i]);
			}
		}
		return tools;
	},
	clearTools:function(){
		/*Remove all tools in weave session*/
		var self = this;
		var tools = self.getToolsNames();
		var path = self.Settings.WObj.path();
		for(var i in tools){
			path.remove(tools[i]);
		}
	},
	setWeaveObj:function(weaveObj){
		var self = this;
		self.Settings.WObj = weaveObj;
		//self.Settings.WObj.path('WeaveDataSource', 'idFields').state(['title', 'name','object_id', 'keyType', 'year']);
                self.Settings.WObj.path('WeaveDataSource','idFields').state(['dataTable','object_id','year','keyType','dataType']);
                
	},
	
	getSessionDataSources:function(){
		var self = this;
		// iterate the session state objects and return the DataSources member attribute column
		var stateList = self.Settings.WObj.path().getState();
		var state;
		for(var i in stateList){
			state = stateList[i];
			if(state.objectName === "WeaveDataSource"){
				break;
			}
		}
		return state;
	},

	
	cleanCategoryTitle:function(text){
		return text;
	},
	
	loadSessionState:function(){
		var self = this;

	},

	fetchClientConfig:function(id, callback){
		var self = this;
		$.getJSON(self.Settings.baseUrl + 'weave/cc/' + id, callback);
	},

	saveClientConfig:function(name, callback){
		var self = this;
		$.post(self.Settings.baseUrl + 'weave/cc-save/',
			       	{ 
					cc_data:JSON.stringify(self.Settings.WObj.path().getState()),
					cc_name: name
				}, 
				"json"
		).done(function(data){
			self.updateWeaveFileName(name);
			if(typeof(callback)!=='undefined'){
				callback(data);
			}
		});

	},

	getUserConfigs:function(callback){
		var self = this;
	},

	showMessage:function(mssg){
		var self = this;
		var mbox = document.createElement('div');
		mbox.innerHTML = mssg;
		mbox.className="weave-mbox";
		$(mbox).css({
			'position':'absolute',
			'top': ($(window).height()/2 - 100) + "px",
			'left': ($(window).width()/2 -100) + "px"
			
		})

		$("body").append(mbox);
		$(mbox).delay(3000).fadeOut('slow', function(){
			$(mbox).remove();	
		});

	},

	addCallback:function(callback){
		var self = this;
		var path = self.Settings.WObj.path("CompoundBarChartTool", "children", "visualization", "plotManager", "plotters", "plot", "heightColumns", "DynamicColumn")
		self.Settings.callbacks.push(callback);
		path.addCallback(function(weave){
			self.runCallback(this.weave, callback); //the weave data
		}, false);
	},

	runCallback:function(weave, callbackName){
		if(self != top) window.parent.DHWEAVE.callbacks[callbackName](weave);
	},
	
	getAPIReady:function(){
		var self = this;
		window.apiInt = setInterval(function(){
			var p = self.Settings.WObj.path();
			if(p.hasOwnProperty('weave')){

				clearInterval(window.apiInt);
				self.Settings.apiready = true;
                self.DsObj = self.Settings.WObj.path('WeaveDataSource');
                // set the inital ds state
                self.Settings.DataSource = self.DsObj.getState().attributeHierarchy.XMLString;
                self.DsObj.addCallback(DHWEAVE.updateDataSource)
				// alert parent window
				if(window != top){
					if(window.parent.DHWEAVE != undefined){
				       		window.parent.DHWEAVE.ready();
					}
				}
			}
		}, 1000);
		
	},
    
    updateDataSource:function(weave){
        var self = DHWEAVE;
        self.DsObj.removeCallback(DHWEAVE.updateDataSource);
        var ds = self.DsObj;
        var xP = new XML.ObjTree(); // xml parser
        xP.xmlDecl = "";
        var ogXML = xP.parseXML(self.Settings.DataSource);
        var ogCats = ogXML.hierarchy.category[0].category;// this gives us DataTable categories and no Geometries;
        var nXML = ds.getState().attributeHierarchy.XMLString;
        var upXML = xP.parseXML(nXML);
        var nCats = upXML.hierarchy.category[0].category;// this gives us DataTable categories and no Geometries;
        var inactive_cats = [];//categories that have not been fetched
        var new_active_cats = [];// cats that are being requested
        // lets inspect the current Datasource and figure out which categories have been fetched already
        for(var c in ogCats){
            if(!ogCats[c].hasOwnProperty("attribute")){
                inactive_cats.push(ogCats[c]['-title']);
            }
        }
        // now we have to see what new category is being requested
        for(var c in nCats){
            var t = nCats[c]['-title'];
            if(nCats[c].hasOwnProperty("attribute")){

                if($.inArray(t, inactive_cats) != -1){
                   // this cat has previously inactive;
                   new_active_cats.push(t);
                    // we update it now in the session state

                   upXML.hierarchy.category[0].category[c].attribute = [];
                   var new_state = ds.getState();
                   new_state.attributeHierarchy.XMLString = xP.writeXML(upXML);
                   ds.state(new_state);

                   $.get("/weave/ds", {dsname:t}, function(data){
                        upXML.hierarchy.category[0].category[c].attribute = data;
                         // update the session state
                        var new_state = ds.getState();
                        new_state.attributeHierarchy.XMLString = xP.writeXML(upXML);
                        ds.state(new_state);
                        self.Settings.DataSource = new_state.attributeHierarchy.XMLString;
                        self.DsObj.addCallback(DHWEAVE.updateDataSource);

                   });

                   break;
                }
            }
        }

    },

	showEmbedCode:function(htmlStr){
		try{
			$.fn
		}catch(err){
			$ = jQuery;
		}
		$('.weave-mbox').remove();
		var mbox = document.createElement('div');
		mbox.className = "weave-mbox";
		mbox.className += " left";
		mbox = $(mbox);
		mbox.html("<h4> Place this code in your webpage</h4><textarea>" + htmlStr + "</textarea>");
		mbox.css({
			position:"absolute",
			width: window.innerWidth > 300 ? 400 : window.innerWidth,
		});

		mbox.css({
			'left': (window.innerWidth/2) - (mbox.width()/2),
			'top': 100,
		});

		var cb = document.createElement('a');
		$(cb).text("X");
		cb.href = "#";
		cb.className = "close-btn";

		mbox.prepend(cb);

		$(cb).click(function(e){
			e.preventDefault();
			$(".weave-mbox").remove();
		});
		
		$('body').append(mbox);

	}
		
});

// extend.js
// written by andrew dupont, optimized by addy osmani
function extend(destination, source) {
    var toString = Object.prototype.toString,
        objTest = toString.call({});
    for (var property in source) {
        if (source[property] && objTest == toString.call(source[property])) {
            destination[property] = destination[property] || {};
            extend(destination[property], source[property]);
        } else {
            destination[property] = source[property];
        }
    }
    return destination;
};


window.onload = function(){
 
	  // exit if the browser implements that event
	  if ( window.document.body.hasOwnProperty('onhashchange') ) { return; }
	 
	  var location = window.location,
	    oldURL = location.href,
	    oldHash = location.hash;
	 
	  // check the location hash on a 100ms interval
	  setInterval(function() {
	    var newURL = location.href,
	      newHash = location.hash;
	 
	    // if the hash has changed and a handler has been bound...
	    if ( newHash != oldHash && typeof window.onhashchange === "function" ) {
	      // execute the handler
	      window.onhashchange({
	        type: "hashchange",
	        oldURL: oldURL,
	        newURL: newURL
	      });
	 
	      oldURL = newURL;
	      oldHash = newHash;
	    }
	  }, 100);

	
}

function $GET(url){
    /*
    * Converts get params to an object. Ex: &foo=bar => {foo:bar}
    *
    * */
    var argsRaw = url.split("&");
    var args = {};
    // split up the args into an objects
    for (var i in argsRaw){
        var vals = argsRaw[i].split("=");
        args[vals[0].replace("?",'')] = vals[1];
    }

    return args;
}


