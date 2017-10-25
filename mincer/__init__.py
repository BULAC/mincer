#!/usr/bin/env python3
"""
Mincer: stuff your websites with the best ingredients

Mincer is a web server used to extract results from one web service by parsing
its html result page.

Mincer is developed for the `BULAC
<http://www.bulac.fr/bulac-in-english/who-are-we/>`_ library in Paris.
"""

__author__ = "Pierre-Yves Martin <pym.aldebaran@gmail.com>"
__copyright__ = "Copyright (C) 2017 GIP BULAC"
__license__ = "GNU AGPL V3"

# This file is part of Mincer.
#
# Mincer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mincer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Mincer.  If not, see <http://www.gnu.org/licenses/>.

# To use clean enumeration type
from enum import Enum

# To decode form-encoded values
from urllib.parse import unquote_plus

# To create a web server c.f. http://flask.pocoo.org/
from flask import Flask

# For rendering Jinja2 HTML template as pages
from flask import render_template

# For building HTTP response and be able to modify them
from flask import make_response

# For easy redirecting to error page
from flask import abort

# To manipulate HTML DOM using JQuery query syntax
from pyquery import PyQuery

# HTTP library for Python, safe for human consumption
# See http://docs.python-requests.org/en/master/
import requests

# A Python slugify application that handles unicode.
# See https://github.com/un33k/python-slugify
from slugify import slugify

# Convenient constant for HTTP status codes
try:
    # Python 3.5+ only
    from HTTPStatus import NOT_FOUND
except Exception as e:
    from http.client import NOT_FOUND

# Html extraction tools
from mincer import utils

# The web application named after the main file itself
app = Flask(__name__)


class HtmlClasses(str, Enum):
    """HTML classes used when generating returned HTML contents."""

    """Class used to embed returned content when we have no results."""
    NO_RESULT = "no-result"


# TODO: Add a selectors_to_remove list of selector that target nodes to remove
# Poor man database...
class Provider(object):
    """A web data provider for Mincer.

    It can be a search provider or a book list provider."""
    ALL = {}

    def __init__(
            self,
            name,
            remote_url,
            result_selector,
            no_result_selector="",
            no_result_content=""):
        self.name = name
        self.slug = slugify(name)
        self.remote_url = remote_url
        self.result_selector = result_selector
        self.no_result_selector = no_result_selector
        self.no_result_content = no_result_content

        self.ALL[self.slug] = self


# TODO remove this abomination of global hidden variable!!!
Provider(
    name="koha search",
    remote_url="https://koha.bulac.fr/cgi-bin/koha/opac-search.pl?idx=&q={param}&branch_group_limit=",
    result_selector="#userresults .searchresults",
    no_result_selector=".span12 p",
    no_result_content="Aucune réponse trouvée dans le catalogue BULAC.")
Provider(
    name="koha booklist",
    remote_url="https://koha.bulac.fr/cgi-bin/koha/opac-shelves.pl?op=view&shelfnumber={param}&sortfield=title",
    result_selector="#usershelves .searchresults")


@app.route("/")
def home():
    """
    Provide a home page of the server.

    .. :quickref: Home; The home page
    """
    return render_template("home.html", providers=Provider.ALL)


# TODO improve the status page with at least the logo
@app.route("/status")
def status():
    """
    Provide a status page showing if all the adaptation works.

    .. :quickref: Status; Get status of all providers
    """
    return render_template("status.html")


# TODO: test the case of a inexistant provider
@app.route("/status/<string:provider_slug>")
def provider_status(provider_slug):
    try:
        provider = Provider.ALL[provider_slug]
    except KeyError:
        abort(NOT_FOUND)

    return render_template("provider_status.html", provider=provider)


# TODO: return only DIV and never HTML pages (even for errors)
@app.route("/providers/<string:provider_name>/<string:param>")
@utils.add_response_headers({"Access-Control-Allow-Origin": "*"})
def providers(provider_name, param):
    """
    Retrieve a search result list from the KOHA server of the BULAC.

    :query string provider_name: slugified name of the provider as registered
        in the database in the database.
    :query string param: parameter of the request already url encoded
        (meaning space and special char are replaced see `urllib
        <https://docs.python.org/3.6/library/urllib.html>`_ for reference). It
        could be a search query, an list id... all depend of the context. It
        will be transfered to the final provider url registered in the
        database.

    :status 200: everything was ok
    :status 404: when no `param` is provided

    .. :quickref: Search; Retrieve search result list from KOHA
    """
    provider = Provider.ALL[provider_name]

    full_remote_url = provider.remote_url.format(param=param)

    # Get the content of the page
    # TODO: copy the accept-language from the recieved request
    #       see: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language
    page = requests.get(
        full_remote_url,
        headers={'accept-language': 'fr-FR'}).text

    try:
        # Search for an answer in the page
        return utils.extract_node_from_html(
            provider.result_selector,
            page)
    except utils.NoMatchError:
        app.logger.info(
            "Provider %s was asked for %s but no result structure could be "
            "found in it's result page. Now searching for a no result "
            "structure...",
            provider_name,
            unquote_plus(param))

    # TODO: test test the case where this fails for exemple if we have
    #   a "loading page"
    # Search for a no answer message in the page
    no_answer_div = utils.extract_content_from_html(
        provider.no_result_selector,
        provider.no_result_content,
        page)
    return PyQuery(no_answer_div)\
        .add_class(HtmlClasses.NO_RESULT)\
        .outer_html()
