

/* code to autosubmit poem dropdown */

// bind change event to select
$('#poem-selection').on('change', function () {
	var url = $(this).val(); // get selected value
	if (url) { // require a URL
		window.location = url; // redirect
	}
	return false;
});

/* code to autosubmit poem dropdown end */

/* Enable Tooltips */
$( document ).ready(function() {
	// Enable Tooltips 
	$(function () {
		  $('[data-toggle="tooltip"]').tooltip()
		})
});

/* Enable Tooltips end */