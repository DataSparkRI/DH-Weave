/*WEAVE JS tools, requires Jquery*/
var DHWEAVE = DHWEAVE || {};

DHWEAVE.Settings = {
	baseUrl:'',
	WObj:null

}

extend(DHWEAVE, {
	getWeaveStateKeys:function(){
		/*return a list of default weave session state items
		 * TODO: SHould this use path().getNames()?
		 * */
		var self = this;
		var ssKeys = [];
		var state = self.Settings.WObj.path().getState()
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
		var validKeys = ['weave.data.DataSources::WeaveDataSource']; // This is a list of weave session state objects we dont want to let the saved session state overwrite.
		if(action==="lwf"){
			//load the weave file by the id
			self.fetchClientConfig(param, function(data){
				var cleaned_data =[]; // We need to clean up old client configurations data sources.
				var match;
				for(var i=0 in data){
					match = 0;
				
					for(var k in validKeys){
						if(data[i].className===validKeys[k]){
							//cleaned_data.push(data[i]);
							//this keeps us from overwriting existing data sources if the stored client config is old.
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
		}	
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
	},
	
	getSessionDataSources:function(){
		var self = this;
		// iterate the session state objects and return the DataSources member attribute column
		var stateList = self.Settings.WObj.path().getState();
		var state;
		for(var i in stateList){	
eave.html
			state = stateList[i];
			if(state.objectName === "WeaveDataSource"){
				break;
			}
		}
		return state;
	},
	updateSessionDataSources:function(hierarchy_label, category_label, data){
		/*Add session data source to the existing one
		 * label is the Hierchy label as see in the data sources
		 * data is the attribute columns formated as an array of dicts
eave.html
		 * that ends up formated like this <attribute weaveEntityId="230" name="% Chronically Absent [18 days+] - Grades 6-8 (30 day min)" year="SY05-06" object_id="3508" dataTable="District" dataType="number" title="% Chronically Absent [18 days+] - Grades 6-8 (30 day min), SY05-06"/>
		 * Then we need to munge it with existing dataset
		 * */
		var self = this;
		var output;
		var dataStr = '<category title="'+category_label+'">';
		var new_hierarchy = self.Settings.WObj.path().push(hierarchy_label).request('WeaveDataSource');
		for(var i in data){
			dataStr += "<attribute";
				for(var prop in data[i]){
					dataStr +=' ' + prop + '="' + data[i][prop] + '"';
				}
			dataStr+= "/>";
			
		}
		dataStr +="</category>"

		if(new_hierarchy.getState().attributeHierarchy === null ){
			output = "<hierarchy>%s</hierarchy>";
			output = output.replace("%s", dataStr);
		}else{
			output = new_hierarchy.getState().attributeHierarchy.replace("</hierarchy>", "%s");
			output = output.replace("%s", dataStr + "\n </hierarchy>");
		}
		var newState = {
			attributeHierarchy : output
		}
		new_hierarchy.state(newState);

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
