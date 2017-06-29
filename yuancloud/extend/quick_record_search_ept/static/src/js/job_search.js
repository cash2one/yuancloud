yuancloud.quick_record_search_ept = function (instance) 
{

var QWeb = instance.web.qweb,
    _t = instance.web._t;


/* 
Define : JobSearch to allow possibility to include inside 
some extra informations.
*/


	instance.quick_record_search_ept.JobSearch = instance.web.Widget.extend
	({
	    template: 'Systray.JobSearchWidget',
	
	    init: function()
	    {
	        this._super();
	        this.on('load', this, this.load);
	        this.on('display', this, this.display);
	    },
	    load: function() {

	    },
	    display: function(sc) {
	        var self = this;
	        var $sc = $(QWeb.render('Systray.Shortcuts.Item', {'shortcut': sc}));
	        $sc.appendTo(self.$el.find('.oe_systray'));
	    },
	
	});
	
	instance.web.UserMenu.include
	({
	    do_update: function() {
	        var self = this;
	        this._super.apply(this, arguments);
	        this.update_promise.done(function()
	        {
	            if (self.job_search) 
	            {
	            	alert("Load");
	            	self.job_search.trigger('load');
	             }
	            else 
	            {
		        	self.job_search = new instance.quick_record_search_ept.JobSearch(self);
		        	user_id=self.session.uid		        	
		        	res_id=user_id       	
        		   act_call = (new instance.web.Model('quick.search.record').call('check_search_record_preference', [ res_id ])).then(function(result) 
    			   {
    				var action = result;
    				if (action == 'True')
					{
    					self.job_search.appendTo(instance.webclient.$el.find('.oe_systray'));		       
		        		instance.webclient.$el.find('.oe_systray').find('#txtJobSearch').keydown(function(event)
		        		{
		        		 key = event.keyCode||event.which||event.charCode
		        		 if(key == 13 && $(this).val().length > 0)
		        		 {	
		        			//res_id = eval($(this).val())
		        			res_id=$(this).val()		        			
	        				act_call = (new instance.web.Model('quick.search.record').call('quick_record_search_def', [ res_id ])).then(function(result) 
	        				{
	        					var action = result;
	        					if (result['msg_id'])
	        					{	        						
	        						alert(result['msg_id'])
	        					}
	        					
	        					$(this).val('');
								instance.client.action_manager.do_action(action)
								
							})
							
		        		  }
		        		});   					
    					
					  }
		        	/*self.job_search.appendTo(instance.webclient.$el.find('.oe_systray'));		       
		        	instance.webclient.$el.find('.oe_systray').find('#txtJobSearch').keydown(function(event){
		        		key = event.keyCode||event.which||event.charCode
		        		if(key == 13 && $(this).val().length > 0)
		        		{	
		        			//alert('Value'+$(this).val())
		        			// call record search method
		        			//res_id = eval($(this).val())
		        			res_id=$(this).val()
		        			alert('Value : '+res_id)
	        				act_call = (new instance.web.Model('quick.search.record').call('quick_record_search_def', [ res_id ])).then(function(result) {
								var action = result;
								$(this).val('');
								instance.client.action_manager.do_action(action)
								
							})

		        		}*/
		        	});//act_call
	            }//else
	        });//this
	    },
	});

};
