/*
 * Javascript to enhance page elements, such as building tooltips, and
 * creating ajax links.
 */



function build_input_select() {
	var tags = ['1','2','3','7','14'];

	$("#id_days").autocomplete({
		source: tags	
	});

}


/*
 * build_tooltips
 *		Create tooltip elements for all elements with the tt_link class.
 *		Tooltips appear above the target element.
 */
function build_tooltips(selector) {

	var target = selector || $('body');
	target.find('.tt_link').each(function(i) {
		var elem = $(this);
		var tooltip = $('#tooltip');

		elem.data('tooltip', elem.attr('title'));
		elem.removeAttr('title');
		elem.hover(function() {
				tooltip.clearQueue();
				tooltip.find('p').html(elem.data('tooltip'));
				tooltip.css({'opacity': 0.8, 'display': 'none'});

				var top = elem.position().top - tooltip.outerHeight() - 2;
				top = (top > 0) ? top : elem.position().top + elem.outerHeight() + 2;
				var left = elem.position().left - tooltip.outerWidth() / 2 + elem.width() / 2;
				left = (left > 0) ? left : 2;
				tooltip.css({'left': left, 'top': top});
				tooltip.fadeIn(200);
			}, function() { 
				tooltip.clearQueue();
				tooltip.fadeOut(50); 
			});
		elem.click(function() { tooltip.fadeOut(50); });
		// In some cases the fadeOut will trigger after the fadeIn, this will
		// ensure that a tooltip is always displayed when the mouse is over a
		// tooltip element.
		elem.mousemove(function() { tooltip.show() });
	});
}

/*
 * add_asyn_param
 *		Add the 'async=1' param correctly to the url.
 */
function add_async_param(url) {
	if (url.indexOf('?') >= 0) {
		return url + '&async=1';
	}
	return url + '?async=1';
}

/*
 * build_async_links
 *		Add onClick events to all links of async class which open a window 
 *		instead of following the url to another page.  An 'async' param is
 *		also added so that the view understands to only return content without
 *		html.
 */
function build_async_links() {

	setup_async_callbacks($('.async'), function(data, code) {
		var d = $('#dialog_window');
		d.html('<p>' + data.content.page_data.content + '</p>');
		d.dialog('option', 'title', data.content.page_data.title);
	});
}


/*
 * setup_async_callbacks
 *		set onclick events with a callback for the selector.
 */
function setup_async_callbacks(selector, success_func) {
	selector.each(function(i) {
		var elem = $(this);
		elem.click(function(event) { 
			event.preventDefault();

			open_dialog();
			var d = $('#dialog_window');
			d.html('Loading ...');

			// Fetch the content
			$.ajax({
				url: add_async_param($(this).attr('href')), 
				dataType: 'json',
				success: success_func,
				error: function(data, status, error) {
					d.dialog('close');
					handle_error(data);
				}
			});
		});
	});
}


function open_dialog() {
	var d = $('#dialog_window');
	d.dialog({'width': 750, 'height': 500});
}

/*
 * update_user_block
 *		Called to update the html contents of the user_block section.
 */
function update_user_block() {
	$('#user_block').load('/auth_status', function() {
		setup_async_callbacks($('.async_frame'), function(data, code) {
			var d = $('#dialog_window');
			d.html(data.content.body);
			d.dialog('option', 'title', data.content.title);
			open_remote(data.content.service_url);
		});
		build_tooltips($('#user_block'));

		// build login/register links
		setup_async_callbacks($('#login_link'), function(data, code) {
			var d = $('#dialog_window');
			d.html(data.content);
			d.dialog('option', 'title', 'Login');
			// TODO: focus login box
		});
		setup_async_callbacks($('#register_link'), function(data, code) {
			var d = $('#dialog_window');
			d.html(data.content);
			d.dialog('option', 'title', 'Register');
			// TODO: focus first field
		});


	});
}


function open_remote(url) {
	window.location.assign(url); 
	return false;
}



/*
 * Log the user out
 */
function logout(elem) {
	$('#user_block').html();
	$.ajax({
			'url': $(elem).attr('href'), 
			'success': function () { window.location.reload() },
	});
	return false;
}


var INPUT	= 'input';
var OK 		= 'ok';
var LOGIN	= 'login';


/*
 * Handle the login and register form submission
 */
function handle_user_account_action(elem) {
	$.ajax({
		'url': add_async_param($(elem).attr('action') + '?' + $(elem).serialize()),
		'success': function(data, code) {
			var d = $('#dialog_window');
			// problem
			if (data.code == INPUT) {
				d.html(data.content);
				return;
			}

			// Success
			d.dialog('close');
			window.location.reload()
		},
	});
	return false;
}


function default_doc_ready() {
	build_tooltips();
	build_async_links();
	build_input_select();
	update_user_block();
	//summary_hover_delay();
}



/*
function makeTall() {
	$('div.result_summary').css({'max-height': '9em', 'overflow': 'auto'});
}
function makeShort() {
	$('div.result_summary').css({'max-height': '3em', 'overflow': 'hidden'});
}
*/

//function summary_hover_delay() {}
/*
$(document).ready(function() {
	$('#result_1 button.expand_summary').click(
		function() {
			//$(this).toggleClass('short long'); 
			alert("Hello");
		}
	);
});
*/
	





