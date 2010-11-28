/*
 * Search Page javascript.
 *
 * Functions called for events on the search page.
 */

var GLOBAL_FETCHING_PAGE = false;
var CONST_NUM_RESULTS = 20;
var GLOBAL_SEARCH_EVENT;
var GLOBAL_END_OF_RESULTS = false;


/*
 * build_form_data
 *		Construct the parameter string from the fields. on the page.
 */
function build_form_data() {
	var params = {};
	$('#search INPUT:not(.ignore)').each(function (i, t) {
		params[t.name] = t.value;
	});
	return $.param(params)

}

/*
 * search
 *		Called onSubmit of the search form.
 */
function search(event) {
	if (event) event.preventDefault();

	GLOBAL_FETCHING_PAGE = true;
	var form_data = build_form_data();
	perform_search(form_data);
	set_page_data(form_data);

	ga_track();
}


/*
 * handle_search_scroll
 *		Called when page is scrolled.
 */
function handle_search_scroll(event) {

	if (GLOBAL_FETCHING_PAGE) return;
	if (GLOBAL_END_OF_RESULTS) return; 

	var view_bottom = $(window).scrollTop() + $(window).height();
	var document_bottom = $(document).height();

	if (view_bottom + 150 > document_bottom) {
		GLOBAL_FETCHING_PAGE = true;
		var start = $('#results').children().length;
		var form_data = build_form_data();
		perform_search(form_data + "&start=" + start, true);
		set_page_data(form_data + "&rows=" + (start+CONST_NUM_RESULTS));

		ga_track();
	}
}


/*
 * update_search
 *		Update the fields in the search form from the form_data.
 *		This is called from pz.pagedata.js update_page
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
function perform_search(form_data, append, event_url) {

	if (!append) {
		$('#results').empty();
	}

	if (!event_url) {
		url = URL_SEARCH + '?' + form_data;
	} else {
		url = event_url;
	}

	$.ajax({
		url: add_async_param(url),
		dataType: 'json',
		success: function(data) {
			handle_search_response(data, append, event_url)
		},
		error: handle_error,	
	});
}

/*
 * Handles the response of the search by updating the page.  Also called on an
 * initial page load.
 */
function handle_search_response(data, append, event_url) {
	// TODO: Handle 0 results
	// TODO: handle input code

	// Build search results
	listing = new EJS({url: '/m/js/templates/search_result.ejs'});
	$.each(data.content.search_results.results, function(i, p) {
		$('#results').append(listing.render(p));
	});

	// updates
	if (!append) {
		update_search_filters(data.content.search_results.filters);
		update_search_history();
		update_sort();
	}
	update_result_view();

	// Add event handlers
	build_result_handlers();

	// If this search was from retrieving an event, then update the form
	// and page data
	if (event_url) {
		update_search($.param(data.content.search_form));
		var form_data = build_form_data();
		set_page_data(form_data);
	}

	// If this was an append search (page scrolling), and we didn't get any
	// more results, then it's the end of results
	GLOBAL_END_OF_RESULTS = (append && size(data.content.search_results.results) == 0);

	GLOBAL_SEARCH_EVENT = data.content.search_event;
	GLOBAL_FETCHING_PAGE = false;
}

/* 
 * Update the search filters block
 */
function update_search_filters(filter_data) {

	var filters = "";
	var filter_template = new EJS({url: '/m/js/templates/search_filter.ejs'});
	$.each(filter_data, function(title, content) {
		filters += filter_template.render({'title': title, 'content': content})
	});
	$('#left_menu').html(filters);
	tiles($('#left_menu'));

	$('#left_menu .filter').each(function (i) {
		$(this).change(function () {
			// TODO: add hidden field to search form
			// TODO: clear searches of that type from listing
			// TODO: remove this element and replace with a link to remove this filtering
		});
	});
	// TODO: add elements for removed filters and add hiden fields to search form

}


/*
 * Update the sort buttons.
 */
function update_sort()  {
	var sort = $('#id_sort').val() || 'date';
	$('#sort_buttons #' + sort).attr('checked', true);
	$('#sort_buttons').buttonset('refresh');
}

/*
 * Perform the search again, with a different sort.
 */
function resort_search() {
	$('#id_sort').val($(this).attr('id'));
	$('#search').submit();
}

/*
 * Update the search history block
 */
function update_search_history() {
	right_tile_helper(URL_SEARCH_HISTORY, '#search_history', URL_SEARCH);
}

/*
 * Update the saved search list
 */
function update_saved_search() {
	right_tile_helper(URL_SEARCH_SAVED, '#saved_searches', URL_SEARCH);
}

/*
 * Update the favorite postings block
 */
function update_favorite_postings() {
	// TODO: outbound url for click_url 
	right_tile_helper(URL_FAV_POSTINGS, '#favorite_posts', null);
}

function right_tile_helper(url, div_id, click_url) {
	$.ajax({
		url: url,
		dataType: 'json',
		success: function(data) {
			var list = new EJS({url: '/m/js/templates/search_list.ejs'});
			var elem = $(div_id);

			if (!data.content.list || data.content.list.length < 1) {
				return;
			}
			
			elem.next().remove();
			elem.replaceWith(list.render(
				{'title': elem.find('a').html(), 'id': elem.attr('id'),
				 'content': data.content.list, 'click_url': click_url
				 }));

			tiles($('#search_meta'));

			// add onClick
			$(div_id).next().find('.search_link').each(function () {
				$(this).click(function (event) {
					event.preventDefault();
					perform_search(null, false, $(this).attr('href'));
				});
			});

		},
		error: handle_error,
	});
}

/* 
 * Save the current search.
 */
function save_search(elem) {

	$.ajax({
		url: URL_SAVE_SEARCH + '?id=' + GLOBAL_SEARCH_EVENT,
		dataType: 'json',
		success: function() { 
			update_saved_search();
		},
		error: handle_error,
	});
	return false;
}


/*
 * Add event handlers to elements in the search results.
 */
function build_result_handlers() {

	build_tooltips($('#results'));
	$('.search_result').each(function(i, e) {

		var id = $(e).attr('post_id');
		$(e).find('.result_save').click(function() {
			event.preventDefault();
			track_event('save', id);
			update_favorite_postings();
		});
		$(e).find('.result_close').click(function() { 
			event.preventDefault();
			track_event('remove', id);
			$('#result_' + id).remove();
		});
	
		// TODO: outbound tracking links
		// TODO: open all above links
		
	});
}


/*
 * Track a user event.
 */
function track_event(name, id, callback) {

	var url = URL_TRACK_EVENT.replace('/name/', "/" + name + "/")
		.replace('/0', "/" + id);

	$.ajax({
		url: url,
		dataType: 'json',
		success: callback,
/*		error: handle_error, */
	});
}


/*
 * Update the search results to show only those DIV for this view.
 */
function update_result_view() {

	var view = $('#view_buttons INPUT:checked').attr('id');
	// Set full view as default, is nothing is set
	if (!view) {
		$('#full_view').attr('checked', 'checked');
		$('#view_buttons').buttonset('refresh');
		return;
	}
		
	$('#view_buttons').buttonset('refresh');
	if (view == 'full_view') {
		$('.search_result DIV').show();
		return;
	}

	if (view == 'summary_view') {
		$('.search_result DIV').show();
		$('.search_result .result_details').hide();
		return;
	}

	if (view == 'minimal_view') {
		$('.search_result DIV').hide();
		$('.search_result .result_title').show();
		return;	
	}
}
