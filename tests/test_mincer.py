#!/usr/bin/env python3

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


class TestMincer(object):
    def test_has_an_empty_root_page(self):
        with mincer.app.test_client() as client:
            response = client.get('/')

            # We have an answer...
            assert response.status_code == OK

            # ...and it's empty
            assert b"" == response.data

    def test_has_status_page(self):
        with mincer.app.test_client() as client:
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
            assert "ADAPTER - status report" in data
            assert "Le serveur Mincer fonctionne parfaitement." in data


class TestAdapterKohaBooklist(object):
    URL_WITHOUT_QUERY = '/koha/liste-de-lecture/'

    def test_has_book_list_page(self):
        with mincer.app.test_client() as client:
            # We are using the ID of of an existing list
            LIST_ID = 9896
            URL = '{url}{id:d}'.format(
                url=self.URL_WITHOUT_QUERY,
                id=LIST_ID)
            response = client.get(URL)

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

    def test_return_error_page_with_empty_list_id(self):
        with mincer.app.test_client() as client:
            LIST_ID = ''
            URL = '{url}{id}'.format(
                url=self.URL_WITHOUT_QUERY,
                id=LIST_ID)
            response = client.get(URL)

            # We have an answer...
            assert response.status_code == NOT_FOUND
            # TODO: Add more test here to ensure we have a valid HTML partial


# TODO: Add test for inefficient search selector: no result
class TestAdapterKohaSearch(object):
    URL_WITHOUT_QUERY = '/koha/recherche/'

    def test_search_works(self):
        with mincer.app.test_client() as client:
            # This search returns only a few results
            SEARCH_QUERY = 'afrique voiture'
            URL = '{url}{query}'.format(
                url=self.URL_WITHOUT_QUERY,
                query=quote_plus(SEARCH_QUERY))
            response = client.get(URL)

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

    def test_return_error_page_with_empty_query(self):
        with mincer.app.test_client() as client:
            SEARCH_QUERY = ''
            URL = '{url}{query}'.format(
                url=self.URL_WITHOUT_QUERY,
                query=quote_plus(SEARCH_QUERY))
            response = client.get(URL)

            # We have an answer...
            assert response.status_code == NOT_FOUND
            # TODO: Add more test here to ensure we have a valid HTML partial

    def test_search_works_with_unicode_query(self):
        with mincer.app.test_client() as client:
            # This search returns only a few results (in japanese)
            SEARCH_QUERY = '龍 車 日'  # dragon car day
            URL = '{url}{param}'.format(
                url=self.URL_WITHOUT_QUERY,
                param=quote_plus(SEARCH_QUERY))
            response = client.get(URL)

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

    def test_return_a_no_result_partial_if_no_result_are_found(self):
        with mincer.app.test_client() as client:
            # This search returns absolutly no result
            SEARCH_QUERY = 'zxkml'
            URL = '{url}{param}'.format(
                url=self.URL_WITHOUT_QUERY,
                param=quote_plus(SEARCH_QUERY))
            response = client.get(URL)

            # We have an answer...
            assert response.status_code == OK

            # ...it's an HTML document...
            assert response.mimetype == "text/html"

            # Let's convert it for easy inspection
            data = response.get_data(as_text=True)

            # ...containing only a <div>
            assert is_div(data, cls_name="no-result")
