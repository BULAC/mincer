Feature: Web interface
	Mincer has a web interface.

	Background:
		Given there is a client to connect to the site
		And there is a temporary address for the database
		And there is a temporary database
		And there are bulac providers in the database

	Scenario: Access home page
		When I go to the "home" page

		Then I have an answer
		And the answer is a text/html document
		And I can retreive a page from the answer
		And the page is an HTML5 page

		And the page title is "Mincer Home"
		And the page header is titled "Mincer"
		And the page header is subtitled "Home"

		And the page contains links
		And the page has a link to the "provider_status" page for "koha-search"
		And the page has a link to the "provider_status" page for "koha-booklist"
		And the page has a link to the "provider_new" page
		And the page has a link to the "status" page
		And the page has a link to the "admin" page


	Scenario: Access status page
		When I go to the "status" page

		Then I have an answer
		And the answer is a text/html document
		And I can retreive a page from the answer
		And the page is an HTML5 page

		And the page title is "Mincer Status report"
		And the page header is titled "Mincer"
		And the page header is subtitled "Status report"

		And the page contains a table
		And the table has "Provider's name" in its headers
		And the table has "Server online?" in its headers
		And the table has "Server responding?" in its headers
		And the table has "Correctly formed answer?" in its headers

		And the page contains links
		And the page has a link to the "provider_status" page for "koha-search"
		And the page has a link to the "provider_status" page for "koha-booklist"


	Scenario: Access admin page
		When I go to the "admin" page

		Then I have an answer
		And the answer is a text/html document
		And I can retreive a page from the answer
		And the page is an HTML5 page

		And the page title is "Mincer Administration"
		And the page header is titled "Mincer"
		And the page header is subtitled "Administration"

		And the page contains a form
		And the database contains the site dependancies
		And the form has a "JQuery minified javascript" group with the url of "jquery-js" dependency
		And the form has a "JQuery minified javascript SHA" group with the sha of "jquery-js" dependency
		And the form has a "Popper minified javascript" group with the url of "popper-js" dependency
		And the form has a "Popper minified javascript SHA" group with the sha of "popper-js" dependency
		And the form has a "Bootstrap minified javascript" group with the url of "bootstrap-js" dependency
		And the form has a "Bootstrap minified javascript SHA" group with the sha of "bootstrap-js" dependency
		And the form has a "Bootstrap minified CSS" group with the url of "bootstrap-css" dependency
		And the form has a "Bootstrap minified CSS SHA" group with the sha of "bootstrap-css" dependency
		And the form has a "Font-Awesome minified CSS" group with the url of "font-awesome-css" dependency
		And the form has a "Font-Awesome minified CSS SHA" group with the sha of "font-awesome-css" dependency
		And the form has a submit button

		And the page contains links
		And the page has a external link to "https://code.jquery.com/"
		And the page has a external link to "https://github.com/FezVrasta/popper.js#installation"
		And the page has a external link to "https://www.bootstrapcdn.com/"
		And the page has a external link to "https://www.srihash.org/"  # Hash generator to ensure the ressources are correct using SRI
		And the page has a external link to "https://hacks.mozilla.org/2015/09/subresource-integrity-in-firefox-43/"  # Doc about SRI
