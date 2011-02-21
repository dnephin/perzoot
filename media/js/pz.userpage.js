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



function fetch_list(list_name) {

	var url = USER_URLS[list_name];
	var template = '/m/js/templates/user_list.ejs';

	$.ajax({
		url: url,
		dataType: 'json',
		success: function(data) {
			list = new EJS({url: template});
			$('#list_content').html(list.render(data.content));
		},
		error: handle_error,
	});

	return false;
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
