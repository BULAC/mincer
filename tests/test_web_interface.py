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

# Behavior Driven Development framework using the cucumber/Gherkin language

"""Web interface feature tests."""

# To create tmp files
import pathlib

# Convenient constant for HTTP status codes
try:
    # Python 3.5+ only
    from HTTPStatus import OK, NOT_FOUND, BAD_REQUEST
except Exception as e:
    from http.client import OK, NOT_FOUND, BAD_REQUEST

# To access real url
from flask import url_for

# Test framework that helps you write better programs !
import pytest

# Behavior Driven Development framework using the cucumber/Gherkin language
from pytest_bdd import (
    given,
    scenario,
    then,
    when,
    parsers,
)

# Module we are going to test
import mincer
from mincer import Dependency

# Helpers to analyse HTML contents
from tests.utils import (
    is_html5_page,
    has_page_title,
    has_header_title,
    has_header_subtitle,
    all_links,
    has_table,
    all_table_column_headers,
    has_form,
    all_form_groups,
    has_form_submit_button,
)


@pytest.fixture
def ctx():
    """
    A fixture used to store scenario data to be inspected.

    You can add any attribute to that fixture whenever you want.
    """
    # HACK: We create a easy container by creating a class on-the-fly
    # c.f. http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991#c12
    return type('Context', (), {})()


# SCENARIOS ###################################################################

@scenario('web_interface.feature', 'Access home page')
def test_access_home_page():
    pass


@scenario('web_interface.feature', 'Access status page')
def test_access_status_page():
    pass


@scenario('web_interface.feature', 'Access admin page')
def test_access_admin_page():
    pass

# GIVEN STEPS #################################################################

@given('there is a client to connect to the site')
def client():
    """Returns a test client for the mincer Flask app."""
    with mincer.app.app_context():
        with mincer.app.test_request_context():
            yield mincer.app.test_client()


@given('there is a temporary address for the database', scope='function')
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

    # Some cleanup: when messing with the config, always give it back in its
    # original state.
    mincer.app.config["SQLALCHEMY_DATABASE_URI"] = OLD_URI


@given('there is a temporary database', scope='function')
def tmp_db(tmp_db_uri):
    # Initialize the temp database
    mincer.init_db()

    return mincer.db


@given('there are bulac providers in the database')
def bulac_prov(tmp_db):
    """Add BULAC specific providers to the database."""
    return mincer.load_bulac_db()


# WHEN STEPS ##################################################################

@when(parsers.parse('I go to the "{dest}" page'))
def home(client, ctx, dest):
    URL = url_for(dest)

    ctx.response = client.get(URL)


# THEN STEPS #################################################################

@then('I have an answer')
def i_have_an_answer(ctx):
    # We have an answer...
    assert ctx.response.status_code == OK


@then('the answer is a text/html document')
def the_answer_is_a_texthtml_document(ctx):
    # ...it's an HTML document...
    assert ctx.response.mimetype == "text/html"


@then('I can retreive a page from the answer')
def i_can_retreive_a_page_from_the_answer(ctx):
    # Let's get and convert data for easy inspection
    ctx.page = ctx.response.get_data(as_text=True)

    assert ctx.page


@then('the page is an HTML5 page')
def the_answer_is_an_html5_page(ctx):
    # Test if we recieved a full HTML page
    assert is_html5_page(ctx.page)


@then(parsers.parse('the page title is "{page_title}"'))
def the_page_title_is_mincer(ctx, page_title):

    assert has_page_title(ctx.page, page_title)


@then(parsers.parse('the page header is titled "{title}"'))
def the_page_header_is_titled(ctx, title):
    assert has_header_title(ctx.page, title)


@then(parsers.parse('the page header is subtitled "{subtitle}"'))
def the_page_header_is_subtitled(ctx, subtitle):
    assert has_header_subtitle(ctx.page, subtitle)


@then('the page contains links')
def the_page_contains_links(ctx):
    ctx.links = all_links(ctx.page)

    assert ctx.links


@then(parsers.parse('the page has a link to the "{destfor}" page for "{slug}"'))
def the_page_has_a_link_to_page_for(ctx, destfor, slug):
    assert url_for(destfor, provider_slug=slug) in ctx.links


@then(parsers.parse('the page has a link to the "{dest}" page'))
def the_page_has_a_link_to_page(ctx, dest):
    assert url_for(dest) in ctx.links


@then(parsers.parse('the page has a external link to "{url}"'))
def the_page_has_a_external_link_to_url(ctx, url):
    assert url in ctx.links


@then('the page contains a table')
def the_page_contains_a_table(ctx):
    assert has_table(ctx.page)

    # We add the table headers to the context for further inspection
    ctx.table_headers = all_table_column_headers(ctx.page)


@then(parsers.parse('the table has "{header}" in its headers'))
def the_table_has_in_its_headers(ctx, header):
    assert header in ctx.table_headers


@then('the page contains a form')
def the_page_contains_a_form(ctx):
    assert has_form(ctx.page)

    # We add the form groups to the context for further inspection
    ctx.form_groups = all_form_groups(ctx.page)


@then('the database contains the site dependancies')
def the_database_contains_the_site_dependancies(ctx):
    # We add the dependencies to the context for further inspection
    ctx.dependencies = {e.name: e for e in Dependency.query.all()}

    assert ctx.dependencies


@then(parsers.parse('the form has a "{grp}" group with the url of "{dep}" dependency'))
def the_form_has_a_group_with_the_url_of_a_dependency(ctx, grp, dep):
    assert ctx.form_groups[grp] == ctx.dependencies[dep].url


@then(parsers.parse('the form has a "{grp}" group with the sha of "{dep}" dependency'))
def the_form_has_a_group_with_the_sha_of_a_dependency(ctx, grp, dep):
    assert ctx.form_groups[grp] == ctx.dependencies[dep].sha


@then('the form has a submit button')
def the_form_has_a_submit_button(ctx):
    # Do we have a button to validate the form ?
    assert has_form_submit_button(ctx.page)
