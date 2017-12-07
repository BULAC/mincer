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

# To manipulate path and environmet variable
import os

# To create tmp files
import pathlib

# To wait a little bit for thing to settle...
from time import sleep

# To translate query from natural text to url encoded
from urllib.parse import quote_plus

# To start and stop fake server
from subprocess import Popen

# Convenient constant for HTTP status codes
try:
    # Python 3.5+ only
    from HTTPStatus import OK, NOT_FOUND, BAD_REQUEST
except Exception as e:
    from http.client import OK, NOT_FOUND, BAD_REQUEST

# To access real url
from flask import url_for

# Module we are going to test
import mincer
from mincer import Provider, Dependency

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
from tests.utils import has_form
from tests.utils import all_form_groups
from tests.utils import has_form_submit_button

# Test framework that helps you write better programs !
import pytest

bulac_test_only = pytest.mark.skipif(
    "BULAC_TESTS" not in os.environ,
    reason="only if we want BULAC specific tests to run")


@pytest.fixture(scope='function')
def tmp_db_uri(tmpdir):
    # Store the old URI to restore it later
    OLD_URI = mincer.app.config["SQLALCHEMY_DATABASE_URI"]

    # Generate a temp file for the test database
    TMP_DB = tmpdir.join("test.db")
    pathlib.Path(TMP_DB.strpath).touch()
    TMP_URI = "sqlite:///{path}".format(path=TMP_DB.strpath)

    # Set the temp database
    mincer.app.config["SQLALCHEMY_DATABASE_URI"] = TMP_URI

    yield TMP_URI

    # Some cleanup: when messing with the config, always give it back in its original state.
    mincer.app.config["SQLALCHEMY_DATABASE_URI"] = OLD_URI


@pytest.fixture(scope='function')
def tmp_db(tmp_db_uri):
    # Initialize the temp database
    mincer.init_db()

    return mincer.db


@pytest.fixture
def client():
    """Returns a test client for the mincer Flask app."""
    with mincer.app.app_context():
        yield mincer.app.test_client()


@pytest.fixture
def bulac_prov(tmp_db):
    """Add BULAC specific providers to the database."""
    return mincer.load_bulac_db()


class TestWebInterface(object):
    # TODO: remove the static providers since we now have dynamic providers
    def test_has_home_page(self, client, tmp_db, bulac_prov):
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

        with mincer.app.test_request_context('/'):
            links = all_links(data)

            # Test the presence of essenciel links
            assert url_for(
                "provider_status",
                provider_slug="koha-search") in links
            assert url_for(
                "provider_status",
                provider_slug="koha-booklist") in links
            assert url_for("provider_new") in links

            # Do we have admin links ?
            assert url_for("status") in links
            assert url_for("admin") in links

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

        with mincer.app.test_request_context('/status'):
            links = all_links(data)
            # Test the presence of essencial links
            assert url_for(
                "provider_status",
                provider_slug="koha-search") in links
            assert url_for(
                "provider_status",
                provider_slug="koha-booklist") in links

    def test_has_admin_page(self, client, tmp_db):
        response = client.get('/admin')

        # We have an answer...
        assert response.status_code == OK

        # ...it's an HTML page
        assert response.mimetype == "text/html"

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        # Test if we recieved a full HTML page
        assert is_html5_page(data)

        assert has_page_title(data, "Mincer Administration")
        assert has_header_title(data, "Mincer")
        assert has_header_subtitle(data, "Administration")

        assert has_form(data)

        # Do we have the essential info in it
        form_groups = all_form_groups(data)

        # Do we have all the fields needed with the correct initial values ?
        dependencies = {e.name: e for e in Dependency.query.all()}
        assert form_groups["JQuery minified javascript"]\
            == dependencies["jquery-js"].url
        assert form_groups["JQuery minified javascript SHA"]\
            == dependencies["jquery-js"].sha

        assert form_groups["Popper minified javascript"]\
            == dependencies["popper-js"].url
        assert form_groups["Popper minified javascript SHA"]\
            == dependencies["popper-js"].sha

        assert form_groups["Bootstrap minified javascript"]\
            == dependencies["bootstrap-js"].url
        assert form_groups["Bootstrap minified javascript SHA"]\
            == dependencies["bootstrap-js"].sha

        assert form_groups["Bootstrap minified CSS"]\
            == dependencies["bootstrap-css"].url
        assert form_groups["Bootstrap minified CSS SHA"]\
            == dependencies["bootstrap-css"].sha

        assert form_groups["Font-Awesome minified CSS"]\
            == dependencies["font-awesome-css"].url
        assert form_groups["Font-Awesome minified CSS SHA"]\
            == dependencies["font-awesome-css"].sha

        # Do we have a button to validate the form ?
        assert has_form_submit_button(data)

        # Do we have the good links to all ressources ?
        links = all_links(data)
        # Places to get the ressources
        assert "https://code.jquery.com/" in links
        assert "https://github.com/FezVrasta/popper.js#installation" in links
        assert "https://www.bootstrapcdn.com/" in links
        # Hash generator to ensure the ressources are correct using SRI
        assert "https://www.srihash.org/" in links
        # Doc about SRI
        assert "https://hacks.mozilla.org/2015/09/subresource-integrity-in-firefox-43/" in links

    @pytest.mark.parametrize("data,expected,msg", [
        ({
            "jquery-js": "aaa",
            "jquery-js-sha": "bbb",
            "popper-js": "ccc",
            "popper-js-sha": "ddd",
            "bootstrap-js": "eee",
            "bootstrap-js-sha": "fff",
            "bootstrap-css": "ggg",
            "bootstrap-css-sha": "hhh",
            "font-awesome-css": "iii",
            "font-awesome-css-sha": "jjj"
        }, OK, "Valid post"),
        ({
            "jquery-js": "aaa",
        }, BAD_REQUEST, "Missing keys"),
        ({
            "jquery-js": "aaa",
            "jquery-js-sha": "bbb",
            "popper-js": "ccc",
            "popper-js-sha": "ddd",
            "bootstrap-js": "eee",
            "bootstrap-js-sha": "fff",
            "bootstrap-css": "ggg",
            "bootstrap-css-sha": "hhh",
            "font-awesome-css": "iii",
            "font-awesome-css-sha": "jjj",
            "should-not-be-here": "oh no"
        }, BAD_REQUEST, "Unknown key")
        ])
    def test_can_post_admin_values(self, client, tmp_db, data, expected, msg):
        response = client.post('/admin', data=data)

        # We have an answer...
        assert response.status_code == expected, msg

    def test_post_admin_values_updates_database(self, client, tmp_db):
        SENT_DATA = {
            "jquery-js": "aaa",
            "jquery-js-sha": "bbb",
            "popper-js": "ccc",
            "popper-js-sha": "ddd",
            "bootstrap-js": "eee",
            "bootstrap-js-sha": "fff",
            "bootstrap-css": "ggg",
            "bootstrap-css-sha": "hhh",
            "font-awesome-css": "iii",
            "font-awesome-css-sha": "jjj"
            }
        response = client.post('/admin', data=SENT_DATA)

        # We have an answer...
        assert response.status_code == OK

        # Check database content
        q = Dependency.query
        jquery_js = q.filter(Dependency.name == "jquery-js").one()
        assert jquery_js.url == SENT_DATA["jquery-js"]
        assert jquery_js.sha == SENT_DATA["jquery-js-sha"]

        popper_js = q.filter(Dependency.name == "popper-js").one()
        assert popper_js.url == SENT_DATA["popper-js"]
        assert popper_js.sha == SENT_DATA["popper-js-sha"]

        bootstrap_js = q.filter(Dependency.name == "bootstrap-js").one()
        assert bootstrap_js.url == SENT_DATA["bootstrap-js"]
        assert bootstrap_js.sha == SENT_DATA["bootstrap-js-sha"]

        bootstrap_css = q.filter(Dependency.name == "bootstrap-css").one()
        assert bootstrap_css.url == SENT_DATA["bootstrap-css"]
        assert bootstrap_css.sha == SENT_DATA["bootstrap-css-sha"]

    def test_has_new_provider_page(self, client, tmp_db):
        response = client.get('/provider/new')

        # We have an answer...
        assert response.status_code == OK

        # ...it's an HTML page
        assert response.mimetype == "text/html"

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        # Test if we recieved a full HTML page
        assert is_html5_page(data)

        assert has_page_title(data, "Provider Add a new provider")
        assert has_header_title(data, "Provider")
        assert has_header_subtitle(data, "Add a new provider")

        assert has_form(data)

        # Do we have the essential info in it
        form_groups = all_form_groups(data)

        assert form_groups["Name"] == ""
        # TODO: Remove slug that should not appear in the form at all
        assert form_groups["Slug"] == ""
        assert form_groups["Remote address"] == ""
        assert form_groups["Result selector"] == ""
        assert form_groups["No result selector"] == ""
        assert form_groups["No result content"] == ""

        # Do we have a button to validate the form ?
        assert has_form_submit_button(data)

    @pytest.mark.xfail(reason="New provider not fully implemented.")
    def test_can_post_new_provider(self, client, tmp_db):
        SENT_DATA = {
            "name": "aaa",
            "slug": "bbb",
            "remote-address": "ccc",
            "result-selector": "ddd",
            "no-result-selector": "eee",
            "no-result-content": "fff",
            }
        response = client.post('/provider', data=SENT_DATA)

        # We have an answer...
        assert response.status_code == OK

    @pytest.mark.xfail(reason="New provider not fully implemented.")
    def test_post_new_provider_updates_database(self, client, tmp_db):
        SENT_DATA = {
            "name": "aaa",
            "slug": "bbb",
            "remote-address": "ccc",
            "result-selector": "ddd",
            "no-result-selector": "eee",
            "no-result-content": "fff",
            }
        response = client.post('/provider', data=SENT_DATA)

        # We have an answer...
        assert response.status_code == OK

        # Check database content
        new = Provider.query.filter(Provider.slug == SENT_DATA['slug']).one()

        assert new.name == SENT_DATA["name"]
        assert new.slug == SENT_DATA["slug"]
        assert new.remote_address == SENT_DATA["remote-address"]
        assert new.result_selector == SENT_DATA["result-selector"]
        assert new.no_result_selector == SENT_DATA["no-result-selector"]
        assert new.no_result_content == SENT_DATA["no-result-content"]

    def test_return_not_found_for_inexistant_providers_status(self, client, tmp_db, bulac_prov):
        URL = "/status/dummy"

        response = client.get(URL)

        # We have an answer...
        assert response.status_code == NOT_FOUND


# TODO: Add test for inefficient search selector: no result
@bulac_test_only
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

        assert has_page_title(data, "Koha search Status report")
        assert has_header_title(data, "Koha search")
        assert has_header_subtitle(data, "Status report")

        assert has_form(data)

        # Do we have the essential info in it
        form_groups = all_form_groups(data)

        assert form_groups["Name"] == "koha search"
        assert form_groups["Slug"] == "koha-search"
        assert form_groups["Remote address"] == "https://koha.bulac.fr/cgi-bin/koha/opac-search.pl?idx=&q={param}&branch_group_limit="
        assert form_groups["Result selector"] == "#userresults .searchresults"
        assert form_groups["No result selector"] == ".span12 p"
        assert form_groups["No result content"] == "Aucune réponse trouvée dans le catalogue BULAC."

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
        assert is_div(data, cls_name=mincer.HtmlClasses.RESULT)

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
        assert is_div(data, cls_name=mincer.HtmlClasses.RESULT)

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
        assert is_div(data, cls_name=mincer.HtmlClasses.NO_RESULT)

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


@bulac_test_only
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

        assert has_form(data)

        # Do we have the essential info in it
        form_groups = all_form_groups(data)

        assert form_groups["Name"] == "koha booklist"
        assert form_groups["Slug"] == "koha-booklist"
        assert form_groups["Remote address"] == "https://koha.bulac.fr/cgi-bin/koha/opac-shelves.pl?op=view&shelfnumber={param}&sortfield=title"
        assert form_groups["Result selector"] == "#usershelves .searchresults"
        assert form_groups["No result selector"] == ""
        assert form_groups["No result content"] == ""

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
        assert is_div(data, cls_name=mincer.HtmlClasses.RESULT)

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

        # Check the global content of the database
        assert len(Provider.query.all()) == 0
        assert len(Dependency.query.all()) > 0

        # Do we have default dependency ?
        assert Dependency.query\
            .filter(Dependency.name == "jquery-js").one()
        assert Dependency.query\
            .filter(Dependency.name == "popper-js").one()
        assert Dependency.query\
            .filter(Dependency.name == "bootstrap-js").one()
        assert Dependency.query\
            .filter(Dependency.name == "bootstrap-css").one()

    def test_app_can_get_actual_database(self, tmp_db):
        assert mincer.db is not None

    def test_has_provider_in_database(self, tmp_db):
        assert Provider.query.all() is not None

    def test_has_dependancy_in_database(self, tmp_db):
        assert Dependency.query.all() is not None


class TestWithFakeProvider(object):
    @pytest.fixture(scope='class')
    def fake_serv(self):
        # Set the path of the server (depends of how the tests are launched)
        path = "tests/fakeprov.py"
        if not os.path.exists(path):
            path = os.path.join("..", path)

        fake_server = Popen(path)
        # Wait for the process to start
        sleep(2)

        yield fake_server

        fake_server.terminate()

    @pytest.fixture
    def fake_prov(self):
        # Create the providers
        fake_provider = Provider(
            name="fake server",
            remote_url="http://0.0.0.0:5555/fake/{param}",
            result_selector=".result",
            no_result_selector=".noresult",
            no_result_content="no result")

        # Add them to the database
        mincer.db.session.add(fake_provider)

        # Commit the transaction
        mincer.db.session.commit()

    def _build_url_from_query(self, query):
        BASE_URL = '/providers/fake-server/'

        url = '{url}{query}'.format(
            url=BASE_URL,
            query=quote_plus(query))

        return url

    # This is just to test that the fake server works
    def test_canary(self, client, tmp_db, fake_serv, fake_prov):
        URL = self._build_url_from_query('canary')
        response = client.get(URL)

        # We have an answer...
        assert response.status_code == OK

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        # And we have the correct books in it
        assert "Pew Pew" in data

    def test_return_not_found_for_inexistant_providers_query(self, client, tmp_db, fake_serv, fake_prov):
        URL = "/providers/dummy/abcde"

        response = client.get(URL)

        # We have an answer...
        assert response.status_code == NOT_FOUND

    def test_provider_has_status_page(self, client, tmp_db, fake_serv, fake_prov):
        URL = '/status/fake-server'
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
        assert has_page_title(data, "Fake server Status report")
        assert has_header_title(data, "Fake server")
        assert has_header_subtitle(data, "Status report")

        assert has_form(data)

        form_groups = all_form_groups(data)

        assert form_groups["Name"] == "fake server"
        assert form_groups["Slug"] == "fake-server"
        assert form_groups["Remote address"] == "http://0.0.0.0:5555/fake/{param}"
        assert form_groups["Result selector"] == ".result"
        assert form_groups["No result selector"] == ".noresult"
        assert form_groups["No result content"] == "no result"

    # TODO: change this behavior to have a valid response partial
    def test_return_404_error_if_no_query_provided(self, client, tmp_db, fake_serv, fake_prov):
        QUERY = ''
        URL = self._build_url_from_query(QUERY)
        response = client.get(URL)

        # We have a NOT FOUND answer
        assert response.status_code == NOT_FOUND

    def test_returned_links_are_fullpath(self, client, tmp_db, fake_serv, fake_prov):
        # We are using the ID of of an existing list
        QUERY = "search with links"
        URL = self._build_url_from_query(QUERY)
        response = client.get(URL)

        # We have an answer...
        assert response.status_code == OK

        # ...it's an HTML document
        assert response.mimetype == "text/html"

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        links = all_links(data)

        assert len(links) > 0
        for l in links:
            assert is_absolute_url(l)

    def test_return_result_partial_if_result_are_found(self, client, tmp_db, fake_serv, fake_prov):
        QUERY = "search with multiple results"
        URL = self._build_url_from_query(QUERY)
        response = client.get(URL)

        # We have an answer...
        assert response.status_code == OK

        # Any web page can use this content
        assert response.headers["Access-Control-Allow-Origin"] == "*"

        # ...it's an HTML document
        assert response.mimetype == "text/html"

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        # ...containing only a <div>
        assert is_div(data, cls_name=mincer.HtmlClasses.RESULT)

        # And we have the correct books in it
        assert "Result number 1" in data
        assert "Result number 2" in data
        assert "Result number 3" in data

    def test_search_works_with_unicode_query(self, client, tmp_db, fake_serv, fake_prov):
        # A query with some japanese
        QUERY = "search with unicode 龍 車 日"  # dragon car day
        URL = self._build_url_from_query(QUERY)
        response = client.get(URL)

        # We have an answer...
        assert response.status_code == OK

        # Any web page can use this content
        assert response.headers["Access-Control-Allow-Origin"] == "*"

        # ...it's an HTML document...
        assert response.mimetype == "text/html"

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        # ...containing only a <div>
        assert is_div(data, cls_name=mincer.HtmlClasses.RESULT)

        # And we have the correct books in it
        assert "Result with japanese 新疆史志" in data
        assert "Result with japanese 永井龍男集" in data

    def test_return_a_no_result_partial_if_no_result_are_found(self, client, tmp_db, fake_serv, fake_prov):
        QUERY = "search without result"
        URL = self._build_url_from_query(QUERY)
        response = client.get(URL)

        # We have an answer...
        assert response.status_code == OK

        # Any web page can use this content
        assert response.headers["Access-Control-Allow-Origin"] == "*"

        # ...it's an HTML document...
        assert response.mimetype == "text/html"

        # Let's convert it for easy inspection
        data = response.get_data(as_text=True)

        # ...containing only a <div>
        assert is_div(data, cls_name=mincer.HtmlClasses.NO_RESULT)
