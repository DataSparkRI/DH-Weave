Ext.require([
    'Ext.tip.QuickTipManager',
    'Ext.menu.*',
    'Ext.form.field.ComboBox',
    'Ext.layout.container.Table',
    'Ext.container.ButtonGroup'
]);

heightColumnsPath = ['CompoundBarChartTool','children','visualization','plotManager','plotters','plot','heightColumns'];



function makeItem(hPath){
    var item = [{
                className: "weave.data.AttributeColumns::DynamicColumn",
                objectName: "DynamicColumn2",
                sessionState: [{
                    className: "weave.data.AttributeColumns::ReferencedColumn",
                    objectName: null,
                    sessionState:{
                                dynamicColumnReference:[{
                                            className: "weave.data.ColumnReferences::HierarchyColumnReference",
                                            objectName: null,
                                            sessionState:{
                                                    dataSourceName: "WeaveDataSource",
                                                    hierarchyPath:{
                                                            XMLString: hPath
                                                    }
                                            }                                            
                                }]
                    }
            }]
        }];
    return item;
}

function getCurrentXMLString(){
    var current_path = []
    for(var i=0; i<heightColumnsPath.length; i++){
        current_path.push(heightColumnsPath[i]);
    }
    
    var condition = true;
    do{
        try{
            if (weave.path(current_path).getState().hierarchyPath === undefined){
                current_path.push(weave.path(current_path).getNames()[0]);
            }
            else {
                condition = false;
            }
            console.log(current_path);
         }
         catch(err){ return '<hierarchy><category name="Data Tables" title="Data Tables"><category name="Postsecondary Institution" title="Postsecondary Institution"><attribute content_type_id="" year="" keyType="" name="" title="" max="100" dataTable="" object_id="" id="" dataType=""/></category></category></hierarchy>';
         }
    }
    while (condition);
    return weave.path(current_path).getState().hierarchyPath.XMLString;
}


function currentYear(){
   
    return StringtoXML(getCurrentXMLString()).getElementsByTagName("attribute")[0].getAttribute("year");
}
function StringtoXML(text){
                if (window.ActiveXObject){
                  var doc=new ActiveXObject('Microsoft.XMLDOM');
                  doc.async='false';
                  doc.loadXML(text);
                } else {
                  var parser=new DOMParser();
                  var doc=parser.parseFromString(text,'text/xml');
                }
                return doc;
}

function getXmlString(xml) {
  if (window.ActiveXObject) { return xml.xml; }
  return new XMLSerializer().serializeToString(xml);
}


function onItemCheck(item, checked){
        var weave = document.getElementById('weave');
        XMLDoc = StringtoXML(getCurrentXMLString());
        XMLDoc_attribute = XMLDoc.getElementsByTagName("attribute")[0];

        
        if(checked){

        
        XMLDoc_attribute.setAttribute("year", item.year);
        XMLDoc_attribute.setAttribute("keyType", item.keyType);
        XMLDoc_attribute.setAttribute("content_type_id", item.content_type_id);
        XMLDoc_attribute.setAttribute("object_id", item.object_id);
        XMLDoc_attribute.setAttribute("name", item.name);
        XMLDoc_attribute.setAttribute("dataType", item.dataType);
        XMLDoc_attribute.setAttribute("dataTable", item.dataTable);
        XMLDoc_attribute.setAttribute("id", item.id);
        
        
            item = makeItem('<hierarchy><category name="Data Tables" title="Data Tables"><category name="'+item.keyType+'" title="'+item.keyType+'">'+getXmlString(XMLDoc_attribute)+'</category></category></hierarchy>');
            
            weave.setSessionState(this.heightColumnsPath, item);
        }
        else{
              weave.setSessionState(this.heightColumnsPath);
        }
}

Ext.define('data_attribute', {
    extend: 'Ext.data.Model',
    fields: [{name: 'name', mapping: '@name', type: 'string'},
             {name: 'keyType', mapping: '@keyType', type: 'string'},
             {name: 'content_type_id', mapping: '@name', type: 'string'},
             {name: 'title', mapping: '@title', type: 'string'},
             {name: 'object_id', mapping: '@object_id', type: 'string'},
             {name: 'dataType', mapping: '@dataType', type: 'string'},
             {name: 'year', mapping: '@year', type: 'string'},
             {name: 'id', mapping: '@id', type: 'string'},
             {name: 'dataTable', mapping: '@dataTable', type: 'string'},
             ],
});

Ext.define('data_category', {
    extend: 'Ext.data.Model',
    fields: [{name: 'name', mapping: '@name', type: 'string'},
             {name: 'keyType', mapping: '@keyType', type: 'string'},
             {name: 'content_type_id', mapping: '@name', type: 'string'},
             {name: 'title', mapping: '@title', type: 'string'},
             {name: 'max', mapping: '@max', type: 'string'},
             {name: 'object_id', mapping: '@object_id', type: 'string'},
             {name: 'dataType', mapping: '@dataType', type: 'string'},
             {name: 'year', mapping: '@year', type: 'string'},
             {name: 'dataTable', mapping: '@dataTable', type: 'string'},
             {name: 'id', mapping: '@id', type: 'string'},
             ],
});
var list_attributes = [];

function search_attribute(object_id, year){
    for(var i =0; i<list_attributes.length; i++){
        if((list_attributes[i].year==year)&&(list_attributes[i].object_id==object_id)){
            return list_attributes[i];
        }
     }
    return false;


}

function setup(url){
        
        var topic_obj = {};

        var topic = Ext.create('Ext.data.Store', {
                                   model: 'data_category',
                                   proxy: {
                                              type: 'ajax',
                                              url: url,
                                              reader: {
                                                        type: 'xml',
                                                        record: 'attribute',
                                                        root: 'AttributeMenuTool',
                                              }
                                   },
                                   listeners: {
                                        load: function(store) {
                                              store.filterBy(function(record) {
                                                    topic_obj[record.get('name')] = true;
                                              });
                                        }
                                   }
                    
                            });



        var attribute_menu = new Ext.data.Store({
            model: 'data_attribute',
            proxy: {
                type: 'ajax',
                url : url,
                reader: {
                    type: 'xml',
                    record: 'attribute',
                    root: 'WeaveDataSource',
                }
            },
            listeners: {
                load: function(store) {
                    // using a map of already used names
                    var hits = {};
                    store.filterBy(function(record) {
                        var name = record.get('title');
                        if (hits[name]) {
                            return false;
                        } else {
                            hits[name] = true;
                            return true;
                        }
                    });

                    // delete the filtered out records
                    delete store.snapshot;
                    
                    
                    
                    var hits = {};
                    store.filterBy(function(record) {
                          tmp_attribute=new Object();
                                tmp_attribute.name=record.get('name');
                                tmp_attribute.keyType=record.get('keyType');
                                tmp_attribute.content_type_id= record.get('content_type_id');
                                tmp_attribute.title=record.get('title');
                                tmp_attribute.object_id=record.get('object_id');
                                tmp_attribute.dataType=record.get('dataType');
                                tmp_attribute.year=record.get('year');
                                tmp_attribute.id=record.get('id');
                                tmp_attribute.dataTable=record.get('dataTable');
                            list_attributes.push(tmp_attribute);                    
                    /*
                        var year = record.get('year');
                        if (hits[year]) {

                        } else {
                            hits[year] = true;

                            years.add({

                                        text: record.get('year'),
                                        id: record.get('year'),
                                        menu: {}
                                 });
                        }
                        var each_year = Ext.getCmp(record.get('year'));
                        try{
                            
                            if(topic_obj[record.get('name')]){
                            each_year.menu.add({
                                text: record.get('title'),
                                value: record.get('object_id'),
                                name:record.get('name'),
                                keyType:record.get('keyType'),
                                content_type_id: record.get('content_type_id'),
                                title:record.get('title'),
                                object_id:record.get('object_id'),
                                dataType:record.get('dataType'),
                                year:record.get('year'),
                                id:record.get('id'),
                                dataTable:record.get('dataTable'),
                                checked: false,
                                group: 'attribute',
                                checkHandler: onItemCheck
                            
                            });
                            
                            //console.log("add");

                            }
                        }
                        catch (err){//these are not attribute
                           console.log("find");
                        }
*/
                    });


                    // delete the filtered out records
                    //delete store.snapshot;
                }
            }
        });

    topic.load({   // This works too!
        scope: this,
        callback: function(records, operation, success) {
              attribute_menu.load();
        }
    });
    

}
setup('/admin/hierarchy_tool/proxy/url={{weave_root}}{{weave_files.0.content_file}}');

Ext.define('data_year', {
    extend: 'Ext.data.Model',
    fields: [{name:'labelsLinkableString',mapping:'labelsLinkableString',type:'string'}],
});


var category_menu = new Ext.data.Store({
    model: 'data_category',
    autoLoad: true,
    proxy: {
        type: 'ajax',
        url : '/admin/hierarchy_tool/proxy/url={{weave_root}}{{weave_files.0.content_file}}',
        reader: {
            type: 'xml',
            record: 'attribute',
            root: 'AttributeMenuTool',
        }
    }
});

Ext.onReady(function(){

   Ext.QuickTips.init();




    var tb = Ext.create('Ext.toolbar.Toolbar');
    tb.render('toolbar');
    tb.suspendLayouts();


   var combo_category = new Ext.form.ComboBox({
        store: category_menu,
        displayField: 'name',
        emptyText:'Select an Indicator',
        valueField: 'object_id',
        tpl: '<tpl for="."><div class="x-boundlist-item" >{name}{freq}</div></tpl>',

        selectOnFocus: true,
        forceSelection: true,
        triggerAction: 'all',
        listConfig: {maxHeight: 100, minWidth:500},
        

        
        typeAhead: true,
        mode: 'local',
        triggerAction: 'all',
        
        editable: false,
        
        listeners: {
            'select': function(t){
                    item = search_attribute(t.value, currentYear());
                    console.log(item);
                    onItemCheck(item, true);
                    combo_category.setValue('');
                    combo.setValue('');

            }
        }
    });
   
   
   var combo = Ext.create('Ext.form.field.ComboBox', {
        hideLabel: true,
        store: new Ext.data.SimpleStore({
                fields: ['name','content_file'],
                data : [
                {% for file in weave_files%}['{{file.name}}','{{file.content_file}}'],{% endfor %}
                ]
        }),
        displayField: 'name',
        valueField: 'content_file',
        typeAhead: true,
        mode: 'local',
        triggerAction: 'all',
        emptyText:'Select a category',
        editable: false,
        width:300,
        listeners: {
            'select': function(t){
                var category_menu = new Ext.data.Store({
                    model: 'data_category',
                    autoLoad: true,
                    proxy: {
                        type: 'ajax',
                        url : '/admin/hierarchy_tool/proxy/url={{weave_root}}/'+t.value,
                        reader: {
                            type: 'xml',
                            record: 'attribute',
                            root: 'AttributeMenuTool',
                        }
                    }
                });
                combo_category.setValue('');
                combo_category.bindStore( category_menu );



                 //years.removeAll();
                 setup('/admin/hierarchy_tool/proxy/url={{weave_root}}/'+t.value);
            }
        }
    });

 
    tb.add(combo);
    tb.add(combo_category);
    tb.resumeLayouts(true);
});


    

