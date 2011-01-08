/*
 * Search Page javascript.
 *
 * Functions called for events on the search page.
 */

var GLOBAL_FETCHING_PAGE = false;
var CONST_NUM_RESULTS = 20;
var GLOBAL_SEARCH_EVENT;
var GLOBAL_END_OF_RESULTS = false;
var GLOBAL_SCROLL_TOP = 0;


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

	// TODO: clear out search filters from old search

	ga_track();
}

/*
 * search_type
 *		Perform a search due to some user action that was not the standard
 *		event of clicking the search button. Used for next_page, filter, 
 *		and sorting.
 */
function search_type(extra_params, append, event_url) {
	GLOBAL_FETCHING_PAGE = true;
	var form_data = build_form_data();
	perform_search(form_data + extra_params, append, event_url);
	set_page_data(form_data);

	ga_track();
}


/*
 * handle_search_scroll
 *		Called when page is scrolled.
 */
function handle_search_scroll(event) {

	update_sidebar_location();

	if (GLOBAL_FETCHING_PAGE) return;
	if (GLOBAL_END_OF_RESULTS) return; 

	var view_bottom = $(window).scrollTop() + $(window).height();
	var document_bottom = $(document).height();

	if (view_bottom + 250 > document_bottom) {
		var start = $('#results').children().length;
		search_type("&start=" + start, true);
		var form_data = build_form_data();
		set_page_data(form_data + "&rows=" + (start+CONST_NUM_RESULTS));
	}
}

/*
 * Update the location of the search sidebars when the user scrolls down the 
 * page.  There are two possible cases here: The sidebar is shorter then the
 * available space and it should stick to the top, or the sidebar is taller 
 * then the available space and it should stick to the bottom.
 */
function update_sidebar_location() {

	var view_bottom = $(window).scrollTop() + $(window).height();
	var doc_bottom = $('body').height();
	var pad = 20;
	var padding_from_top = 18;

	var down = (GLOBAL_SCROLL_TOP < $(window).scrollTop())
	var up = !down;
	GLOBAL_SCROLL_TOP = $(window).scrollTop();

	$('#left_bar,#right_bar').each(function() {
		var bot = $(this).position()['top'] + $(this).height();
		var top = $(this).position()['top'];
		var orig_top = $(this).data('orig_top');
		var taller = ($(this).height() > $(window).height());


		// The bar is shorter then the window
		if ($(window).scrollTop() != top && !taller &&
				((down && bot + pad < doc_bottom) ||
				(up && top >= orig_top))) {
			$(this).css({position: "absolute", 
					top: Math.max(
						$(window).scrollTop() + padding_from_top, 
						orig_top)});
		}

		// The bar is taller then the window
		if (taller &&
				((down && bot < doc_bottom && bot < view_bottom) ||
				(up && top >= orig_top ))) {
			$(this).css({position: "absolute", 
					top: Math.max(view_bottom - $(this).height(), orig_top)});
		}
	});
}



/*
 * update_search
 *		Update the fields in the search form from the form_data.
 *		This is called from pz.pagedata.js update_page
 */
function update_search(form_data) {
	$.each(form_data.split('&'), function(i, d) {
		var parts = d.split('=');
		$("#search input[name='"+parts[0]+"']").val(format_value(parts[1]));
	});
}

function format_value(value) {
	return unescape(value).replace(/\+/g, ' ');
}

/*
 * perform_search
 * 		Perform a search, update the page location, and display the results.
 *		This function should most likely not be called directly, use search or
 *		search_type instead so that analytics and page_data are updated.
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
	// handle input code
	if (data.code == INPUT) {
		var e = $('#dialog_error');

		var errors = "";
		var error_template = new EJS({url: '/m/js/templates/form_error.ejs'});
		$.each(data.content.search_form.errors, function(f, error_list) {
			errors += error_template.render({'field': f , 'error_list': error_list});
		});
		e.dialog();
		e.html(errors);
		e.dialog('option', 'title', 'Error');
		return;
	};

	// Build search results
	listing = new EJS({url: '/m/js/templates/search_result.ejs'});
	$.each(data.content.search_results.results, function(i, p) {
		$('#results').append(listing.render(p));
	});

	// If this search was from retrieving an event, then update the form
	// and page data
	if (event_url) {
		update_search($.param(data.content.search_form));
		var form_data = build_form_data();
		set_page_data(form_data);
	}

	// updates
	if (!append) {
		update_search_filters(data.content.search_results.filters);
		update_search_history();
		update_sort();
	}
	update_result_view();
	highlight_toggle();

	// Add event handlers
	build_result_handlers();
	build_summary_hover_delay($('div.summary_box'));
	build_summary_hover_delay($('div.details_box'));


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
	$.each(filter_data, function(i, content) {
		filters += filter_template.render({'title': content[0], 'content': content[1]})
	});
	$('#left_menu').html(filters);
	tiles($('#left_menu'));

	$('#left_menu .filter').each(function (i) {
		$(this).change(function () {
			// add hidden field to search form
			update_filter_field($(this).attr('filter_type'), $(this).attr('name'));
			$(this).parent().remove();
			search_type('&otp_filter=1')
		});
	});
	// add elements for removed filters and add hidden fields to search form
	$('#search input[name^="filter_"]').each(function () {
		var filter_type = $(this).attr('name').split('_')[1];
		$.each($(this).val().split('|'), function(i, v) {
			if (!v.length) return true;

			var template = new EJS({text: 
				'<li><input type="checkbox" class="remove_filter" ' +
				'filter_type="<%= type %>" name="<%=name%>"/><%=name%></li>'
				});
			$('#list_' + filter_type).append(
				template.render({'type': filter_type, 'name': v})
			);
		});
	});
	// Add javascript to remove the remove_filters
	$('.remove_filter').change(function (event) {
		if (event) event.preventDefault();
		remove_filter(this);
	});

	// TODO: this does not display in the correct place
	//build_tooltips($('#left_menu'));

}

/*
 * Remove this exclusion filter from the search parameters.
 */
function remove_filter(elem) {

	var type = $(elem).attr('filter_type');
	var field = $('#search input[name="filter_'+type+'"]');
	if (!field.length) return;

	var values = (field.val().length) ? field.val().split("|") : [];
	var new_values = [];
	for (i in values) {
		if (values[i] == $(elem).attr('name'))
			continue;
		new_values.push(values[i]);
	}
	field.val(new_values.join("|"));
	$(this).parent().remove();
	search_type('&otp_filter=1')
}

/*
 * Add or Update a hidden field in the search form for the filter.
 */
function update_filter_field(filter_type, value) {

	var field = $('#search input[name="filter_'+filter_type+'"]');
	if (field.val().length) {
		var values = field.val().split("|");
		values.push(value);
		field.val(values.join("|"));
		return;
	}
	field.val(value);
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
	search_type('&otp_sort=1')
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
	right_tile_helper(URL_FAV_POSTINGS, '#favorite_posts', null);
}

function right_tile_helper(url, div_id, click_url) {
	var dynamic_click_url = (click_url == null);
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
				 'content': data.content.list, 'click_url': click_url,
				 'dynamic_click_url': dynamic_click_url
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
		$(e).find('.result_save').click(function(event) {
			event.preventDefault();
			track_event('save', id);
			update_favorite_postings();
			$(event.target).parents('.search_result').addClass('saved_event');
		});
		$(e).find('.result_close').click(function(event) { 
			event.preventDefault();
			track_event('remove', id);
			$('#result_' + id).remove();
		});

		// outbound tracking links
		$(e).find('.job_title A,.result_links A').each(function() {
			$(this).click( function(event) { 
				track_outbound(event, id) 
				$(event.target).parents('.search_result').addClass('opened_event');
			} );
		});
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
		$('.search_result div').show();
		return;
	}

	if (view == 'summary_view') {
		$('.search_result div').show();
		$('.search_result .result_details').hide();
		return;
	}

	if (view == 'minimal_view') {
		$('.search_result div').hide();
		$('.search_result .result_title').show();
		$('.search_result .result_links').show();
		return;	
	}
}


/*
 * jQuery hoverIntent plugin to delay hover time for summary and detail boxes
 */
function build_summary_hover_delay(selector) {
	
	var hoverConfig = {
		over: function() { $(this).animate({'max-height': '9em', 'overflow': 'auto'}, 500); },
		timeout: 300,
		out: function() { $(this).animate({'max-height': '3.5em', 'overflow': 'hidden'}, 500); },
		sensitivity: 20,
		interval: 200
	}
	
	selector.hoverIntent( hoverConfig );
}


/*
 * Toggle highlight of search results.
 */
function highlight_toggle() {
	var state = $('#hl_buttons INPUT:checked').attr('id');

	// Set off as default, is nothing is set
	if (!state) {
		$('#hl_off').attr('checked', 'checked');
		$('#hl_buttons').buttonset('refresh');
		return;
	}
		
	var selector = $('.result_details,.result_summary');

	$('#hl_buttons').buttonset('refresh');
	if (state == 'hl_on') {
		// TODO: handle quotes around terms
		var terms = $('#id_keywords').val().split(' ');
		for (i in terms) {
			selector.highlight(terms[i]);
		}
		return;
	}

	if (state == 'hl_off') {
		selector.removeHighlight();
		return;
	}
}
