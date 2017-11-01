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
def tmp_db_uri(tmpdir):
    # Store the old URI to restore it later
    OLD_URI = mincer.app.config["SQLALCHEMY_DATABASE_URI"]

    # Generate a temp file for the test database
    TMP_DB = tmpdir.join("test.db")
    pathlib.Path(TMP_DB).touch()
    TMP_URI = "sqlite:///{path}".format(path=str(TMP_DB))

    # Set the temp database
    mincer.app.config["SQLALCHEMY_DATABASE_URI"] = TMP_URI

    yield TMP_URI

    # Some cleanup: when messing with the config, always give it back in its original state.
    mincer.app.config["SQLALCHEMY_DATABASE_URI"] = OLD_URI


@pytest.fixture
def tmp_db(tmp_db_uri):
    # Initialize the temp database
    mincer.init_db()

    return mincer.db


@pytest.fixture
def client():
    """Returns a test client for the mincer Flask app."""
    return mincer.app.test_client()

@pytest.fixture
def bulac_prov(tmp_db):
    """Add BULAC specific providers to the database."""
    # Create the providers
    koha_search = mincer.Provider(
        name="koha search",
        remote_url="https://koha.bulac.fr/cgi-bin/koha/opac-search.pl?idx=&q={param}&branch_group_limit=",
        result_selector="#userresults .searchresults",
        no_result_selector=".span12 p",
        no_result_content="Aucune réponse trouvée dans le catalogue BULAC.")
    koha_booklist = mincer.Provider(
        name="koha booklist",
        remote_url="https://koha.bulac.fr/cgi-bin/koha/opac-shelves.pl?op=view&shelfnumber={param}&sortfield=title",
        result_selector="#usershelves .searchresults")

    # Add them to the database
    mincer.db.session.add_all([
        koha_search,
        koha_booklist])

    # Commit the transaction
    mincer.db.session.commit()


class TestWebInterface(object):
    def test_home_page_give_links_to_all_providers(self, client, tmp_db, bulac_prov):
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

    def test_has_status_page(self, client, tmp_db, bulac_prov):
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

    def test_return_not_found_for_inexistant_providers_status(self, client, tmp_db, bulac_prov):
        URL = "/status/dummy"

        response = client.get(URL)

        # We have an answer...
        assert response.status_code == NOT_FOUND


# TODO: Add test for inefficient search selector: no result
class TestGenericKohaSearch(object):
    def _build_url(self, param):
        BASE_URL = '/providers/koha-search/'

        url = '{url}{param}'.format(
            url=BASE_URL,
            param=quote_plus(param))

        return url

    def test_koha_search_is_a_provider(self, client, tmp_db, bulac_prov):
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

    def test_return_error_page_with_empty_query(self, client, tmp_db, bulac_prov):
        SEARCH_QUERY = ''

        url = self._build_url(SEARCH_QUERY)
        response = client.get(url)

        # We have an answer...
        assert response.status_code == NOT_FOUND

    def test_search_works(self, client, tmp_db, bulac_prov):
        # This search returns only a few results
        SEARCH_QUERY = 'afrique voiture'

        url = self._build_url(SEARCH_QUERY)
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

    def test_search_works_with_unicode_query(self, client, tmp_db, bulac_prov):
        # This search returns only a few results (in japanese)
        SEARCH_QUERY = '龍 車 日'  # dragon car day

        url = self._build_url(SEARCH_QUERY)
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

    def test_return_a_no_result_partial_if_no_result_are_found(self, client, tmp_db, bulac_prov):
        # This search returns absolutly no result
        SEARCH_QUERY = 'zxkml'

        url = self._build_url(SEARCH_QUERY)
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

    def test_links_are_fullpath(self, client, tmp_db, bulac_prov):
        # This search returns only a few results
        SEARCH_QUERY = 'afrique voiture'

        url = self._build_url(SEARCH_QUERY)
        response = client.get(url)

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        links = all_links(data)

        assert len(links) > 0
        for l in links:
            assert is_absolute_url(l)


class TestGenericKohaBooklist(object):
    def _build_url(self, param):
        BASE_URL = '/providers/koha-booklist/'

        url = '{url}{param}'.format(
            url=BASE_URL,
            param=quote_plus(param))

        return url

    def test_koha_booklist_is_a_provider(self, client, tmp_db, bulac_prov):
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

    def test_return_error_page_when_asking_for_empty_list_id(self, client):
        LIST_ID = ''

        url = self._build_url(LIST_ID)
        response = client.get(url)

        # We have an answer...
        assert response.status_code == NOT_FOUND

    def test_return_result_partial_if_result_are_found(self, client, tmp_db, bulac_prov):
        # We are using the ID of of an existing list
        LIST_ID = "9896"

        url = self._build_url(LIST_ID)
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

    def test_links_are_fullpath(self, client, tmp_db, bulac_prov):
        # We are using the ID of of an existing list
        LIST_ID = "9896"

        url = self._build_url(LIST_ID)
        response = client.get(url)

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        links = all_links(data)

        assert len(links) > 0
        for l in links:
            assert is_absolute_url(l)


def test_return_not_found_for_inexistant_providers_query(client, tmp_db, bulac_prov):
    URL = "/providers/dummy/abcde"

    response = client.get(URL)

    # We have an answer...
    assert response.status_code == NOT_FOUND

# TODO: add test for single ressource provider (koha for example)


class TestDatabase(object):
    def test_app_has_a_database_in_config(self):
        assert "SQLALCHEMY_DATABASE_URI" in mincer.app.config

        # Let's build the expected path
        DB_PATH = os.path.join(mincer.app.instance_path, "mincer.db")
        EXPECTED_URI = "sqlite:///{path}".format(path=DB_PATH)

        assert mincer.app.config["SQLALCHEMY_DATABASE_URI"] == EXPECTED_URI

    def test_can_initialize_database(self, tmp_db_uri):
        mincer.init_db()

        # Get the content of the database
        assert len(mincer.Provider.query.all()) == 0

    def test_app_can_get_actual_database(self, tmp_db):
        assert mincer.db is not None
