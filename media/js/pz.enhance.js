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
function build_tooltips() {

	$('.tt_link').each(function(i) {
		var elem = $(this);
		$('body').append(
			'<div class="tooltip" id="tooltip_'+i+'"><p>' + 
			elem.attr('title') + '</p></div>');
		var tooltip = $('#tooltip_'+i);

		elem.removeAttr('title');
		elem.mouseover(function() {
			tooltip.css({'opacity': 0.8, 'display': 'none'}).fadeIn(400);
		});
		elem.mousemove(function(event) {
			var top = $(event.target).position()['top'] - tooltip.outerHeight();
			var left = event.pageX - tooltip.width() / 2;
			left = (left > 0) ? left : 2;
			tooltip.css({'left': left, 'top': top});
		});
		elem.mouseout(tooltip, function() {
			tooltip.fadeOut(400);
		});
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

	$('.async').each(function(i) {
		var elem = $(this);
		elem.click(function(event) { 
			event.preventDefault();

			var d = $('#dialog_window');
			d.dialog({'width': 500, 'minHeight': 400});
			d.html('Loading ...');

			// Fetch the content
			$.ajax({
				url: add_async_param($(this).attr('href')), 
				dataType: 'json',
				success: function(data, code) {
					d.html('<p>' + data.content.page_data.content + '</p>');
					d.dialog('option', 'title', data.content.page_data.title);
				},
				error: function(data, status, error) {
					d.dialog('close');
					handle_error(data);
				}
			});
		});
	});
}


function update_user_block() {
	$('#user_block').load('/auth_status');
}


function logout(elem) {

	event.preventDefault();
	$('#user_block').html();
	$.ajax({
			'url': $(elem).attr('href'), 
			'success': update_user_block, 
	});
}


function default_doc_ready() {
	build_tooltips();
	build_async_links();
	build_input_select();
	set_search_keybind();
	update_user_block();
}
