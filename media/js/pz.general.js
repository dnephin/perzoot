/*
 * General JS, including: 
 *	Tracking and Analytics
 *	Error handling
 *  Helper and utility functions
 */

function track_outbound(event, id) {
	// TODO: does this need a delay to fire ?

	// PZ
	$.ajax({
		url: '/jax/track/open/' + id,
		success: function(data) {},
	});

	// GA
	var tracker = _gat._getTrackerByName();
	// TODO: add label and session id as value
	tracker._trackEvent('outbound', 'open', undefined, undefined);
}


// TODO: 
// http://code.google.com/apis/analytics/docs/tracking/eventTrackerGuide.html#Categories


var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-19341877-1']);
_gaq.push(['_setDomainName', '.perzoot.com']);
_gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();


function ga_track() {
	_gat._getTrackerByName()._trackPageview();
}

function handle_error(data) {
	var e = $('#dialog_error');
	e.dialog();
	e.html(
		new EJS({url: '/m/js/templates/form_error.ejs'})
		.render({'field': 'Oops!', 'error_list': ['Something went wrong. ' +
			'We\'re terribly sorry, and we\'re working on fixing it now.']}));
	e.dialog('option', 'title', 'Error');
}

/*
 * Get the size of the object (aka associative array).
 */
function size(obj) {
	var size = 0, key;
	for (key in obj) {
		if (obj.hasOwnProperty(key)) size++;
	}
	return size;
}


