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



function onItemCheck(item, checked){
        var weave = document.getElementById('weave');

        if(checked){
            items = makeItem('<hierarchy><category name="Data Tables" title="Data Tables"><category name="'+item.keyType+'" title="'+item.keyType+'"><attribute keyType="'+item.keyType+'" content_type_id="'+item.content_type_id+'" title="'+item.title+'" object_id="'+item.object_id+'" name="'+item.name+'" dataType="'+item.dataType+'" dataTable="'+item.dataTable+'" year="'+item.year+'" id="'+item.id+'" /></category></category></hierarchy>');
            weave.setSessionState(this.heightColumnsPath, items);
            try
             {window.parent.update_info(item.object_id);}
            catch(err){console.log(err)}
        }
        else{
              weave.setSessionState(this.heightColumnsPath);
        }
        //Ext.example.msg('Item Check', 'You {1} the "{0}" menu item.', item.text, checked ? 'checked' : 'unchecked');
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
var years = Ext.create('Ext.menu.Menu', {
        id: 'mainMenu',
        style: {
            overflow: 'visible'     // For the Combo popup
        },
        items: [],
});

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
                                text: record.get('name'),
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

/*
var category_menu = new Ext.data.Store({
    model: 'data_category',
    autoLoad: true,
    proxy: {
        type: 'ajax',
        url : '/media/data_filter_files/ohe_only_report4_biog.xml',
        reader: {
            type: 'xml',
            record: 'attribute',
            root: 'AttributeMenuTool',
        }
    }
});
*/

Ext.onReady(function(){






    var tb = Ext.create('Ext.toolbar.Toolbar');
    tb.render('toolbar');
    tb.suspendLayouts();



   
   
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
        emptyText:'Topic',
        editable: false,
        width:300,
        listeners: {
            'select': function(t){
                 years.removeAll();
                 setup('/admin/hierarchy_tool/proxy/url={{weave_root}}'+t.value);
            }
        }
    });

 
    tb.add({
                text:'Terms',
                //iconCls: 'bmenu',  // <-- icon
                menu: years  // assign menu by instance
            });    
    tb.add(combo);

    tb.resumeLayouts(true);
});


    

