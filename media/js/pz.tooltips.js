/*
 * Tooltips javascript.
 */


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


