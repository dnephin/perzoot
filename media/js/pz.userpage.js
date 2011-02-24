/*
 * JavaScript for the user page.
 *
 */



function field_success(status_elem, text) {
	status_elem.clearQueue().fadeIn(10);
	status_elem.removeClass('info error');
	status_elem.addClass('success');
	status_elem.html(text);
	status_elem.delay(2500).fadeOut(1000);
}

function field_error(status_elem, text) {
	status_elem.clearQueue().fadeIn(10);
	status_elem.removeClass('info success');
	status_elem.addClass('error');
	status_elem.html(text);
	status_elem.delay(2500).fadeOut(1000);
}


/*
 * handle_field
 *		Handle the focusout event the fields on account page.
 */
function handle_field(elem) {
	var name = elem.attr('name');
	var status = $('#status_' + name);
	var data;

	if (elem.attr('value').length < 1) {
		field_error(status, 'This field can not be blank.');
		return;
	}

	// special cases
	if (name == 'password1') {
		field_success(status, 'Confirm your password.');
		return;
	}
	if (name == 'password2') {
		if (elem.attr('value') != $('#id_password1').attr('value')) {
			field_error(status, 'Passwords do not match.')
			return;
		}
		data = { 'field': 'password', 'value': elem.attr('value') };
	} else {
		data = { 'field': name, 'value': elem.attr('value') };
	}
	
	var url = $('#account_form').attr('fieldaction');

	status.fadeIn(10);
	status.removeClass('error success');
	status.addClass('info');
	status.html('waiting ...');

	$.ajax({
		url: url + "?" + $.param(data),
		dataType: 'json',
		success: function(data, code) {
			if (data.code == INPUT) {
				field_error(status, data.content[0]);
				return;
			}
			field_success(status, 'Update successful');
		},
		error: function(data, code) {
			field_error(status, 'Server Error');
		},
	});	

}



/*
 * Select all elements in a user list.
 */
function select_all_user_list() {
	$('.list_data TBODY INPUT').attr('checked', true);
	$(this).button({'label': 'Unselect All'}).click(unselect_all_user_list);
}
function unselect_all_user_list() {
	$('.list_data TBODY INPUT').attr('checked', false);
	$(this).button({'label': 'Select All'}).click(select_all_user_list);
}

function delete_items_user_list() {

	$.ajax({
		url: URL_DEL_LIST_ITEMS + '?' + $('#user_list_form').serialize(),
		dataType: 'json',
		success: function(data) {
			// TODO: display message

			// refresh list
			fetch_list($('#user_list_form input[name="list_type"]').val())
		}
	});

}

function open_items_user_list() {
	$('.list_data TBODY TR').each(function (i, row) {
		if ($(this).find('input').attr('checked')) {
			open($(this).find('TD A.posting_link').attr('href'));
		}
	});
}

/*
 * Setup for users lists
 */
var USER_LIST_SETUP = {
		'saved_searches': {
			'template': '/m/js/templates/user_search_list.ejs',
			'buttons': [
				['Select All', 'select_all_button', select_all_user_list],
				['Delete', 'delete_button', delete_items_user_list],
			],
			'title': 'Saved Searches',
		},
		'search_history': {
			'template': '/m/js/templates/user_search_list.ejs',
			'buttons': [
				['Select All', 'select_all_button', select_all_user_list],
				['Delete', 'delete_button', delete_items_user_list],
			],
			'title': 'Search History',
		},
		'favorite_postings': {
			'template': '/m/js/templates/user_posting_list.ejs',
			'buttons': [
				['Select All', 'select_all_button', select_all_user_list],
				['Delete', 'delete_button', delete_items_user_list],
				['Open', 'open_button', open_items_user_list],
			],
			'title': 'Favorite Postings',
		},
		'deleted_postings': {
			'template': '/m/js/templates/user_posting_list.ejs',
			'buttons': [
				['Select All', 'select_all_button', select_all_user_list],
				['Un-Delete', 'delete_button', delete_items_user_list],
			],
			'title': 'Deleted Postings',
		},
};


/*
 * Retrieve a users search or posting lists and display them.
 */
function fetch_list(list_name) {

	var url = USER_URLS[list_name];
	var template = USER_LIST_SETUP[list_name]['template'];

	$.ajax({
		url: url,
		dataType: 'json',
		success: function(data) {

			if (!data.content.list)
				data.content.list = {}

			list = new EJS({url: template});
			$('#list_content').html(list.render({
				'name': list_name,
				'list': data.content.list,
				'buttons': USER_LIST_SETUP[list_name]['buttons'],
				'title': USER_LIST_SETUP[list_name]['title'],
			}));

			$.each(USER_LIST_SETUP[list_name]['buttons'], function(i, button) {
				$('#'+button[1]).button({text: button[0]}).click(button[2]);
			})
		},
		error: handle_error,
	});

	return false;
}


/*
 * Load the list in the user tab, if the hash contains a reference to a list.
 */
function load_sublist() {
	var hash = window.location.hash.substring(1);

	if (USER_LIST_SETUP[hash]) {
		fetch_list(hash);
		$('#user_tabs').tabs('select', '#user_lists');
	}
}

/*
 * Add focusout events to form fields on account page.
 */
function build_field_focusout() {

	$('.user_field input').each(function(i) {
		var elem = $(this);

		elem.focusout(function (event) {
			handle_field(elem);
		});
	});
}



$(document).ready(function() {

	default_doc_ready();
	$('#user_tabs').tabs();
	build_field_focusout();

});
