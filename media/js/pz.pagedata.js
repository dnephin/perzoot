/*
 * Page Data javascript
 *
 * Provides functionality for refresh, back, forward, and bookmarking with
 * ajax requests.
 */


var GLOBAL_TIMESTAMP = new Date().getTime();

/*
 * get_page_data
 *		Retrieve the page data from the encoded string in the location.hash
 */
function get_page_data() {
	var loc_hash = decodeURIComponent(document.location.hash.substring(1));
	var page_data_part = loc_hash.split('#')[1];

	var page_data = new Object();
	jQuery.map(page_data_part.split(','), function (i) {
		var parts = i.split(':');
		page_data[parts[0]] = parts[1];
	});
	return page_data;
}

function build_page_data(search_data) {
	GLOBAL_TIMESTAMP = new Date().getTime();
	return encodeURIComponent(GLOBAL_TIMESTAMP + "#search:" + search_data );
}

function set_page_data(search_form) {
	document.location.href = '#' + build_page_data(search_form);
}

function check_page_data_has_changed() {
	var timestamp = get_timestamp_data();

	if (timestamp == GLOBAL_TIMESTAMP || timestamp.length < 1) {
		return;
	}

	update_page(timestamp, get_page_data());
}


function get_timestamp_data() {
	var loc_hash = decodeURIComponent(document.location.hash.substring(1));
	return loc_hash.split('#')[0];
}


/*
 * update_page
 *		Update the page by calling the functions with the data encoded
 *		in the page_data.
 */
function update_page(timestamp, page_data) {
	GLOBAL_TIMESTAMP = timestamp;
	// TODO: is this safe?
	$.each(page_data, function(f, d) {
		new Function('d', 'return perform_' + f + '(d)')(d);
		new Function('d', 'return update_' + f + '(d)')(d);
	});
}

