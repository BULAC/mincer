#!/usr/bin/env python3
"""
Mincer: stuff your websites with the best ingredients

Mincer is a web server used to extract results from one web service by parsing
its html result page.

Mincer is developed for the `BULAC
<http://www.bulac.fr/bulac-in-english/who-are-we/>`_ library in Paris.
"""

# To create a web server c.f. http://flask.pocoo.org/
from flask import Flask

# For rendering Jinja2 HTML template as pages
from flask import render_template

# To manipulate HTML DOM using JQuery query syntax
from pyquery import PyQuery

# HTTP library for Python, safe for human consumption
# See http://docs.python-requests.org/en/master/
import requests

# Convenient constant for HTTP status codes
try:
    # Python 3.5+ only
    from HTTPStatus import BAD_REQUEST
except Exception as e:
    from http.client import BAD_REQUEST

# Html extraction tools
from mincer import utils

# The web application named after the main file itself
app = Flask(__name__)


@app.route("/")
def home():
    """
    Provide a home page of the server.

    .. :quickref: Home; The home page
    """
    return ""


@app.route("/status")
def status():
    """
    Provide a status page showing if all the adaptation works.

    .. :quickref: Status; Get status of all providers
    """
    return render_template("status.html")


# TODO: return only DIV and never HTML pages (even for errors)
# TODO: reprace the request param with a direct url param for readability
@app.route("/koha/liste-de-lecture/<int:booklist_id>")
def koha_book_list(booklist_id):
    """
    Retrieve a book list from the KOHA server of the BULAC.

    :query int booklist_id: numeric id of the book list for KOHA

    :status 200: everything was ok
    :status 404: when no `booklist_id` is provided

    .. quickref: Liste de lecture; Retrieve a book list from KOHA
    """
    URL = "https://koha.bulac.fr/cgi-bin/koha/opac-shelves.pl?op=view&shelfnumber={booklist_id:d}&sortfield=title"\
        .format(booklist_id=booklist_id)
    SELECTOR = "#usershelves .searchresults"

    # Get the content of the page
    page = requests.get(URL).text

    return utils.extract_node_from_html(SELECTOR, page)


# TODO: return only DIV and never HTML pages (even for errors)
@app.route("/koha/recherche/<string:search_query>")
def koha_search(search_query):
    """
    Retrieve a search result list from the KOHA server of the BULAC.

    :query string search_query: the terms to search already url encoded
        (meaning space and special char are replaced see `urllib
        <https://docs.python.org/3.6/library/urllib.html>`_ for reference)

    :status 200: everything was ok
    :status 404: when no `search_query` is provided

    .. :quickref: Search; Retrieve search result list from KOHA
    """
    URL = "https://koha.bulac.fr/cgi-bin/koha/opac-search.pl?idx=&q={search_query:s}&branch_group_limit="\
        .format(search_query=search_query)
    RESULT_SELECTOR = "#userresults .searchresults"
    NO_RESULT_SELECTOR = ".span12 p"
    # In english "No results found for that in BULAC catalog."
    # in french "Aucune réponse trouvée dans le catalogue BULAC."
    NO_RESULT_CONTENT_KOHA = "Aucune réponse trouvée dans le catalogue BULAC."

    # Get the content of the page
    # TODO: copy the accept-language from the recieved request
    #       see: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language
    page = requests.get(URL, headers={'accept-language': 'fr-FR'}).text

    try:
        # Search for an answer in the page
        return utils.extract_node_from_html(RESULT_SELECTOR, page)
    except utils.NoMatchError:
        # Search for a no answer message in the page
        no_answer_div = utils.extract_content_from_html(
            NO_RESULT_SELECTOR, NO_RESULT_CONTENT_KOHA, page)
        return PyQuery(no_answer_div).add_class("no-result").outer_html()
