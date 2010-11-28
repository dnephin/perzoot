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

		var tt = document.createElement("div");
		tt.className = "tooltip";
		tt.innerHTML = "<p>" + elem.attr('title') + "</p>";
		document.body.appendChild(tt);

		var tooltip = $(tt);
		tooltip.css({'opacity': 0.8, 'display': 'none'});
		var top = elem.position().top - tooltip.outerHeight() - 4;
		top = (top > 0) ? top : tooltip.height() + 8;
		var left = elem.position().left - tooltip.width() / 2 + elem.width() / 2;
		left = (left > 0) ? left : 2;
		tooltip.css({'left': left, 'top': top});

		elem.removeAttr('title')
			.hover(function() { tooltip.fadeIn(200); }, 
				function() { tooltip.fadeOut(10); })
			.click(function() { tooltip.fadeOut(10); });
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

			var d = $('#dialog_window');
			// TODO: Move into CSS
			d.dialog({'width': 500, 'minHeight': 400});
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


/*
 * Log the user out
 */
function logout(elem) {

	event.preventDefault();
	$('#user_block').html();
	$.ajax({
			'url': $(elem).attr('href'), 
			'success': update_user_block, 
	});
}


var INPUT	= 'input';
var OK 		= 'ok';
var LOGIN	= 'login';


/*
 * Handle the login and register form submission
 */
function handle_user_account_action(elem) {
	event.preventDefault();
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
			update_user_block();
		},
	});
}




function default_doc_ready() {
	build_tooltips();
	build_async_links();
	build_input_select();
	update_user_block();
}
