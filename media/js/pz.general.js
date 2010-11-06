/*
 * General JS, including: 
 *	Tracking and Analytics
 *	Error handling
 */

function track_outbound(id) {
	// GA
	var tracker = _gat._getTrackerByName();
	// TODO: add label and session id as value
	tracker._trackEvent('outbound', 'open', undefined, undefined);

	// PZ
	$.ajax({
		url: '/track/outbound/' + id,
		success: function(data) {},
	});
}


// TODO: 
// http://code.google.com/apis/analytics/docs/tracking/eventTrackerGuide.html#Categories

function ga_track() {
	_gat._getTrackerByName()._trackPageview();
}


  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-19341877-1']);
  _gaq.push(['_setDomainName', '.perzoot.com']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();


function handle_error(data) {
	var e = $('#dialog_error');
	e.dialog();
	e.html('Oops! Something went wrong. We\'re on it.');
}

