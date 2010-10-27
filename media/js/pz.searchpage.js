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
	}
}


