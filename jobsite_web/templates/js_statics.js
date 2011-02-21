{% comment %}

 js_statics.js

 This file is used to create javascript global variables for urls.  Since urls
 should only be hardcoded in urls.py, and javascript files are not served
 through django, this is a way to access those urls without hardcoding them
 in javascript files.


{% endcomment %}
var URL_SEARCH = "{% url jobsite_main.views.search %}";
var URL_SEARCH_HISTORY = "{% url search_history %}";
var URL_SEARCH_SAVED = "{% url saved_searches %}";
var URL_FAV_POSTINGS = "{% url jobsite_main.views.favorite_postings %}";
var URL_SAVE_SEARCH = "{% url jobsite_main.views.save_search %}"; 
var URL_TRACK_EVENT = "{% url track 'name' 0 %}";


var USER_URLS = {
		'saved_searches': "{% url all_saved_searches %}",
		'search_history': "{% url all_search_history %}",
		'favorite_postings': "{% url all_favorite_postings %}",
		'deleted_postings': "{% url all_deleted_postings %}",
};

{% comment %}
TODO: Change to ajax call
{% endcomment %}
var CITIES = ['Montreal', 'St Laurent', 'Pointe Clair', 'Anjou', 'Dorval', 
		'Lachine', 'St Léonard', 'Laval', 'Kirkland', 'Dollard', 'Pierrefond',
		'Mont Royal'];
var DAYS = ['1', '3', '7', '14', '30'];
