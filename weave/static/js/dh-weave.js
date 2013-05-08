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
		var validKeys = self.getWeaveStateKeys();
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
				self.Settings.WObj.path().diff(cleaned_data);	
			});
		}	
	},
	setWeaveObj:function(weaveObj){
		var self = this;
		self.Settings.WObj = weaveObj;
	},
	
	getSessionState:function(){
		var self = this;
		
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
	updateSessionDataSources:function(label, data){
		var self = this;
		var newState = {
			attributeHierarchy : '<hierarchy name="User Items"><category title="Nested"></category></hierarchy>'	
		}
		self.Settings.WObj.path()
		.push(label)
		.request('WeaveDataSource')
		.state(newState);
	},

	loadSessionState:function(){
		var self = this;

	},

	fetchClientConfig:function(id, callback){
		var self = this;
		$.getJSON(self.Settings.baseUrl + 'weave/cc/' + id, callback)
	},

	saveClientConfig:function(name, callback){
		var self = this;
	},

	getUserConfigs:function(callback){
		var self = this;
			
	},	
		
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
