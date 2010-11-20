/*
 * Custom JQuery UI widgets
 * Perzoot
 */

/*
 * Turn the selector element(s) into an open accordian widget.
 */
function tiles(selector) {
	selector.addClass("ui-accordion ui-widget ui-helper-reset ui-accordion-icons")
	.find("h3")
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
					.toggle();
			return false;
		})
		.next()	// body div
			.addClass("ui-accordion-content ui-helper-reset ui-widget-content ui-corner-bottom")
			.addClass("ui-accordian-content-active")
			.show();
}

