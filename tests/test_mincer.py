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

# To manipulate path
import os

# To create tmp files
import pathlib

# To translate query from natural text to url encoded
from urllib.parse import quote_plus

# Convenient constant for HTTP status codes
try:
    # Python 3.5+ only
    from HTTPStatus import OK, NOT_FOUND
except Exception as e:
    from http.client import OK, NOT_FOUND

# Helpers to analyse HTML contents
from tests.utils import is_div
from tests.utils import is_html5_page
from tests.utils import has_page_title
from tests.utils import has_header_title
from tests.utils import has_header_subtitle
from tests.utils import all_links
from tests.utils import has_table
from tests.utils import all_table_column_headers
from tests.utils import is_absolute_url

# Test framework that helps you write better programs !
import pytest


@pytest.fixture
def client():
    """Returns a test client for the mincer Flask app."""
    return mincer.app.test_client()


class TestMincer(object):
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

        assert has_page_title(data, "Mincer Status report")
        assert has_header_title(data, "Mincer")
        assert has_header_subtitle(data, "Status report")

        assert has_table(data)
        assert "Provider's name" in all_table_column_headers(data)
        assert "Server online?" in all_table_column_headers(data)
        assert "Server responding?" in all_table_column_headers(data)
        assert "Correctly formed answer?" in all_table_column_headers(data)

        # Test the presence of essencial links
        assert "/status/koha-search" in all_links(data)
        assert "/status/koha-booklist" in all_links(data)


# TODO: Add test for inefficient search selector: no result
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

        # Any web page can use this content
        assert response.headers["Access-Control-Allow-Origin"] == "*"

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

    def test_search_works_with_unicode_query(self, client):
        # This search returns only a few results (in japanese)
        SEARCH_QUERY = '龍 車 日'  # dragon car day

        url = self.build_url(SEARCH_QUERY)
        response = client.get(url)

        # We have an answer...
        assert response.status_code == OK

        # Any web page can use this content
        assert response.headers["Access-Control-Allow-Origin"] == "*"

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

        # Any web page can use this content
        assert response.headers["Access-Control-Allow-Origin"] == "*"

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

    def test_return_result_partial_if_result_are_found(self, client):
        # We are using the ID of of an existing list
        LIST_ID = "9896"

        url = self.build_url(LIST_ID)
        response = client.get(url)

        # We have an answer...
        assert response.status_code == OK

        # Any web page can use this content
        assert response.headers["Access-Control-Allow-Origin"] == "*"

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

    def test_return_error_page_when_asking_for_empty_list_id(self, client):
        LIST_ID = ''

        url = self.build_url(LIST_ID)
        response = client.get(url)

        # We have an answer...
        assert response.status_code == NOT_FOUND

    def test_links_are_fullpath(self, client):
        # We are using the ID of of an existing list
        LIST_ID = "9896"

        url = self.build_url(LIST_ID)
        response = client.get(url)

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        links = all_links(data)

        assert len(links) > 0
        for l in links:
            assert is_absolute_url(l)


def test_koha_search_is_a_provider(client):
    URL = '/status/koha-search'
    response = client.get(URL)

    # We have an answer...
    assert response.status_code == OK

    # ...it's an HTML document...
    assert response.mimetype == "text/html"

    # Let's convert it for easy inspection
    data = response.get_data(as_text=True)

    # Test if we recieved a full HTML page
    assert is_html5_page(data)

    # Do we have the essential info in it
    # Provider name
    assert "koha search" in data

    # Slugified name
    assert "koha-search" in data

    # Query url (we don't check for the full one)
    assert "https://koha.bulac.fr/cgi-bin/koha/opac-search.pl" in data

    # Result list selector
    assert "#userresults .searchresults" in data

    # No result selector
    assert ".span12 p" in data

    # No result content
    assert "Aucune réponse trouvée dans le catalogue BULAC." in data


def test_koha_booklist_is_a_provider(client):
    URL = '/status/koha-booklist'
    response = client.get(URL)

    # We have an answer...
    assert response.status_code == OK

    # ...it's an HTML document...
    assert response.mimetype == "text/html"

    # Let's convert it for easy inspection
    data = response.get_data(as_text=True)

    # Test if we recieved a full HTML page
    assert is_html5_page(data)

    assert has_page_title(data, "Koha booklist Status report")
    assert has_header_title(data, "Koha booklist")
    assert has_header_subtitle(data, "Status report")

    # Do we have the essential info in it
    # Provider name
    assert "koha booklist" in data

    # Slugified name
    assert "koha-booklist" in data

    # Query url (we don't check for the full one)
    assert "https://koha.bulac.fr/cgi-bin/koha/opac-shelves.pl" in data

    # Result list selector
    assert "#usershelves .searchresults" in data


def test_return_not_found_for_inexistant_providers_status(client):
    URL = "/status/dummy"

    response = client.get(URL)

    # We have an answer...
    assert response.status_code == NOT_FOUND


def test_return_not_found_for_inexistant_providers_query(client):
    URL = "/providers/dummy/abcde"

    response = client.get(URL)

    # We have an answer...
    assert response.status_code == NOT_FOUND


def test_home_page_give_links_to_all_providers(client):
    response = client.get('/')

    # We have an answer...
    assert response.status_code == OK

    # ...it's an HTML document...
    assert response.mimetype == "text/html"

    # Let's convert it for easy inspection
    data = response.get_data(as_text=True)

    # Test if we recieved a full HTML page
    assert is_html5_page(data)

    assert has_page_title(data, "Mincer Home")
    assert has_header_title(data, "Mincer")
    assert has_header_subtitle(data, "Home")

    # Test the presence of essenciel links
    assert "/status/koha-search" in all_links(data)
    assert "/status/koha-booklist" in all_links(data)

# TODO: add test for single ressource provider (koha for example)


class TestDatabase(object):
    def test_app_has_a_database_in_config(self):
        assert "DATABASE" in mincer.app.config

        EXPECTED_PATH = os.path.join(mincer.app.instance_path, "mincer.db")
        assert mincer.app.config["DATABASE"] == EXPECTED_PATH

    @pytest.fixture
    def app_context(self, tmpdir):
        tmp_db = tmpdir.join("test.db")
        pathlib.Path(tmp_db).touch()
        mincer.app.config["DATABASE"] = str(tmp_db)

        with mincer.app.app_context():
            yield

    def test_can_initialize_database(self, app_context):
        mincer.init_db()

        # Get the content of the database
        db = mincer.get_db()
        cur = db.execute('select title, text from entries order by id desc')
        entries = cur.fetchall()

        # Check for emptyness
        assert len(entries) == 0

    def test_app_can_connect_to_database(self, app_context):
        mincer.init_db()
        assert mincer.connect_db() is not None

    def test_app_can_get_actual_database(self, app_context):
        mincer.init_db()
        assert mincer.get_db() is not None
