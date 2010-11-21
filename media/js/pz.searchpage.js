/*
 * Search Page javascript.
 *
 * Functions called for events on the search page.
 */

var GLOBAL_FETCHING_PAGE = false;
var CONST_NUM_RESULTS = 20;


/*
 * build_form_data
 *		Construct the parameter string from the fields. on the page.
 */
function build_form_data() {
	var params = {};
	$('#search input[type!=hidden]').each(function (i, t) {
		params[t.name] = t.value;
	});
	return $.param(params)

}

/*
 * search
 *		Called onSubmit of the search form.
 */
function search() {
	GLOBAL_FETCHING_PAGE = true;
	var form_data = build_form_data();
	perform_search(form_data);
	set_page_data(form_data);

	ga_track();
	return false;
}


/*
 * handle_search_scroll
 *		Called when page is scrolled.
 */
function handle_search_scroll(event) {

	if (GLOBAL_FETCHING_PAGE) return;

	var view_bottom = $(window).scrollTop() + $(window).height();
	var document_bottom = $(document).height();

	// TODO: stop when results are complete.

	if (view_bottom + 150 > document_bottom) {
		GLOBAL_FETCHING_PAGE = true;
		var start = $('#results').children().length;
		var form_data = build_form_data();
		perform_search(form_data + "&start=" + start, true);
		set_page_data(form_data + "&rows=" + (start+CONST_NUM_RESULTS));

		ga_track();
	}
}


function set_search_keybind() {
	// Set keybinds
	$('#search input').keypress(function(e) { 
		if (e.keyCode == 13) $('#search_button').click();
	});
}



/*
 * update_search
 *		Update the fields in the search form from the form_data
 */
function update_search(form_data) {
	$.each(form_data.split('&'), function(i, d) {
		var parts = d.split('=');
		$("#search input[name='"+parts[0]+"']").val(parts[1]);
	});
}

/*
 * perform_search
 * 		Perform a search, update the page location, and display the results.
 */
function perform_search(form_data, append) {

	if (!append) {
		$('#results').empty();
	}

	$.ajax({
		url: add_async_param(URL_SEARCH + '?' + form_data),
		dataType: 'json',
		success: function(data) {
			// TODO: Handle 0 results

			// Build search results
			listing = new EJS({url: '/m/js/templates/search_result.ejs'});
			$.each(data.content.search_results.results, function(i, p) {
				$('#results').append(listing.render(p));
			});
			
			// Build search filters
			var filters = "";
			var filter_template = new EJS({url: '/m/js/templates/search_filter.ejs'});
			$.each(data.content.search_results.filters, function(title, content) {
				filters += filter_template.render({'title': title, 'content': content})
			});
			$('#left_menu').html(filters);
			tiles($('#left_menu'));

			// update history
			update_search_history();

			GLOBAL_FETCHING_PAGE = false;
		},
		error: handle_error,	
	});
}


/*
 * Update the search history block
 */
function update_search_history() {
	$.ajax({
		url: URL_SEARCH_HISTORY,
		dataType: 'json',
		success: function(data) {
			var list = new EJS({url: '/m/js/templates/search_list.ejs'});

			var elem = $('#search_history');
			elem.next().remove();
			elem.replaceWith(list.render(
				{'title': elem.find('a').html(), 'id': elem.attr('id'),
				 'content': data.content.list
				 }));

			tiles($('#search_meta'));
		},
		error: handle_error,
	});
}

/*
 * Update the saved search list
 */
function update_saved_search() {
	$.ajax({
		url: URL_SEARCH_SAVED,
		dataType: 'json',
		success: function(data) {
			var list = new EJS({url: '/m/js/templates/search_list.ejs'});
			var elem = $('#saved_searches');

			if (data.content.list.length < 1) {
				return;
			}
			
			elem.next().remove();
			elem.replaceWith(list.render(
				{'title': elem.find('a').html(), 'id': elem.attr('id'),
				 'content': data.content.list
				 }));

			tiles($('#search_meta'));
		},
		error: handle_error,
	});

}



/* 
 * Save the current search.
 */
function save_search(elem) {

	$.ajax({
		url: URL_SAVE_SEARCH,
		dataType: 'json',
		success: function() { 
			update_saved_search();
		},
		error: handle_error,
	});
	return false;
}

