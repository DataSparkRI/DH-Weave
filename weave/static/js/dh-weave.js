/*WEAVE JS tools, requires Jquery*/
var DHWEAVE = DHWEAVE || {};

DHWEAVE.Settings = {
	baseUrl:'http:127.0.0.1:8000',
	WObj:null,
}

extend(DHWEAVE, {
	setWeaveObj:function(weaveObj){
		var self = this;
		self.Settings.WObj = weaveObj;
	},

	getSessionState:function(){
		var self = this;
		
	},

	loadSessionState:function(){
		var self = this;

	},

	fetchClientConfig:function(slug, callback){
		var self = this;
	},

	saveClientConfig:function(name, callback){
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
