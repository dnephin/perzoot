/*
 * Custom JQuery UI widgets
 * Perzoot
 */

/*
 * Turn the selector element(s) into an open accordian widget.  This widget
 * expects tags layed out the same way as an accordian.
 *
 * Supports h3.tile_default_closed to set a section to be closed by default. 
 */
function tiles(selector) {
	selector.addClass("ui-accordion ui-widget ui-helper-reset ui-accordion-icons")
	.find("h3:not(.ui-accordion-header)")
		.addClass("ui-accordion-header ui-helper-reset ui-corner-top")
		.addClass("ui-accordion-header-active ui-state-active ")
		.prepend('<span class="ui-icon ui-icon-triangle-1-s"/>')
		.click(function() {
			$(this) // h3
					.toggleClass("ui-accordion-header-active")
					.toggleClass("ui-state-active")
					.toggleClass("ui-state-default")
					.toggleClass("ui-corner-bottom")
			.find("> .ui-icon") // Icon span
					.toggleClass("ui-icon-triangle-1-e")
					.toggleClass("ui-icon-triangle-1-s")
			.end().next()	// body div
					.toggleClass("ui-accordion-content-active")
					.toggle("blind", 200);
			return false;
		})
		.next()	// body div
			.addClass("ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom")
			.addClass("ui-accordian-content-active")
			.show();

	// close any sections that are set to default close and are currently active.
	selector.find('h3.tile_default_closed.ui-state-active').trigger('click');
}

