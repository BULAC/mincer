#!/usr/bin/env python3

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

# Module we are going to test
import mincer

# To translate query from natural text to url encoded
from urllib.parse import quote_plus

# Convenient constant for HTTP status codes
try:
    # Python 3.5+ only
    from HTTPStatus import OK, NOT_FOUND
except Exception as e:
    from http.client import OK, NOT_FOUND

# Some useful func to analyse strings and determine if they are HTML
from tests.utils import is_div
from tests.utils import is_html5_page

# Test framework that helps you write better programs !
import pytest


@pytest.fixture
def client():
    """Returns a test client for the mincer Flask app."""
    return mincer.app.test_client()


class TestMincer(object):
    def test_has_an_empty_root_page(self, client):
        response = client.get('/')

        # We have an answer...
        assert response.status_code == OK

        # ...and it's empty
        assert b"" == response.data

    def test_has_status_page(self, client):
        response = client.get('/status')

        # We have an answer...
        assert response.status_code == OK

        # ...it's an HTML page
        assert response.mimetype == "text/html"

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        # Test if we recieved a full HTML page
        assert is_html5_page(data)

        # ...with the correct title and content
        assert "Mincer - status report" in data
        assert "Le serveur Mincer fonctionne parfaitement." in data


# TODO: Add test for inefficient search selector: no result
# TODO make a more generic version of the test using parametrized fixture
class TestGenericKohaSearch(object):
    def build_url(self, param):
        BASE_URL = '/providers/koha-search/'

        url = '{url}{param}'.format(
            url=BASE_URL,
            param=quote_plus(param))

        return url

    def test_search_works(self, client):
        # This search returns only a few results
        SEARCH_QUERY = 'afrique voiture'

        url = self.build_url(SEARCH_QUERY)
        response = client.get(url)

        # We have an answer...
        assert response.status_code == OK

        # ...it's an HTML document...
        assert response.mimetype == "text/html"

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        # ...containing only a <div>
        assert is_div(data, cls_name="searchresults")

        # And we have the correct books in it
        assert "Transafrique" in data
        assert "L'amour a le goût des fraises" in data
        assert "Les chemins de Mahjouba" in data

    def test_return_error_page_with_empty_query(self, client):
        SEARCH_QUERY = ''

        url = self.build_url(SEARCH_QUERY)
        response = client.get(url)

        # We have an answer...
        assert response.status_code == NOT_FOUND
        # TODO: Add more test here to ensure we have a valid HTML partial

    def test_search_works_with_unicode_query(self, client):
        # This search returns only a few results (in japanese)
        SEARCH_QUERY = '龍 車 日'  # dragon car day

        url = self.build_url(SEARCH_QUERY)
        response = client.get(url)

        # We have an answer...
        assert response.status_code == OK

        # ...it's an HTML document...
        assert response.mimetype == "text/html"

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        # ...containing only a <div>
        assert is_div(data, cls_name="searchresults")

        # And we have the correct books in it
        assert "新疆史志" in data
        assert "永井龍男集" in data

    def test_return_a_no_result_partial_if_no_result_are_found(self, client):
        # This search returns absolutly no result
        SEARCH_QUERY = 'zxkml'

        url = self.build_url(SEARCH_QUERY)
        response = client.get(url)

        # We have an answer...
        assert response.status_code == OK

        # ...it's an HTML document...
        assert response.mimetype == "text/html"

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        # ...containing only a <div>
        assert is_div(data, cls_name="no-result")


class TestGenericKohaBooklist(object):
    def build_url(self, param):
        BASE_URL = '/providers/koha-booklist/'

        url = '{url}{param}'.format(
            url=BASE_URL,
            param=quote_plus(param))

        return url

    def test_has_book_list_page(self, client):
        # We are using the ID of of an existing list
        LIST_ID = "9896"

        url = self.build_url(LIST_ID)
        response = client.get(url)

        # We have an answer...
        assert response.status_code == OK

        # ...it's an HTML document
        assert response.mimetype == "text/html"

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        # ...containing only a <div>
        assert is_div(data, cls_name="searchresults")

        # And we have the correct books in it
        assert "Africa in Russia, Russia in Africa" in data
        assert "Cahiers d'études africaines" in data
        assert "Étudier à l'Est" in data
        assert "Forced labour in colonial Africa" in data
        assert "Le gel" in data
        assert "Revue européenne des migrations internationales" in data
        assert "The Cold War in the Third World" in data

    def test_return_error_page_with_empty_list_id(self, client):
        LIST_ID = ''

        url = self.build_url(LIST_ID)
        response = client.get(url)

        # We have an answer...
        assert response.status_code == NOT_FOUND
        # TODO: Add more test here to ensure we have a valid HTML partial


# TODO: add test for inexistant provider

def test_koha_search_is_a_provider(client):
    URL = '/status/koha-search'
    response = client.get(URL)

    # We have an answer...
    assert response.status_code == OK

    # ...it's an HTML document...
    assert response.mimetype == "text/html"

    # Let's convert it for easy inspection
    data = response.get_data(as_text=True)

    # ...containing only a <div>
    assert is_html5_page(data)

    # Do we have the essential info in it
    # Provider name
    assert "koha" in data
    assert "search" in data

    # Slugified name
    assert "koha-search" in data

    # Query url (we don't check for the full one)
    assert "https://koha.bulac.fr/cgi-bin/koha/opac-search.pl" in data

    # Result list selector
    assert "#userresults .searchresults" in data

    # No result selector
    assert ".span12 p" in data


def test_koha_book_list_is_a_provider(client):
    URL = '/status/koha-booklist'
    response = client.get(URL)

    # We have an answer...
    assert response.status_code == OK

    # ...it's an HTML document...
    assert response.mimetype == "text/html"

    # Let's convert it for easy inspection
    data = response.get_data(as_text=True)

    # ...containing only a <div>
    assert is_html5_page(data)

    # Do we have the essential info in it
    # Provider name
    assert "koha" in data
    assert "booklist" in data

    # Slugified name
    assert "koha-booklist" in data

    # Query url (we don't check for the full one)
    assert "https://koha.bulac.fr/cgi-bin/koha/opac-shelves.pl" in data

    # Result list selector
    assert "#usershelves .searchresults" in data
