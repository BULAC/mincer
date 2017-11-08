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

# To manipulate path
import os

# To create a web server c.f. http://flask.pocoo.org/
from flask import Flask

# For easy database ~ python binding c.f. http://www.sqlalchemy.org/
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy

# Flask application context all purpose variable
from flask import g

# For rendering Jinja2 HTML template as pages
from flask import render_template

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
    from HTTPStatus import NOT_FOUND, INTERNAL_SERVER_ERROR, BAD_REQUEST
except Exception as e:
    from http.client import NOT_FOUND, INTERNAL_SERVER_ERROR, BAD_REQUEST

# Html extraction tools
from mincer import utils

# The web application named after the main file itself
app = Flask(__name__)

# Config of the application

# Default values
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{path}".format(
    path=os.path.join(app.instance_path, 'mincer.db'))

# If we want to overload the setting with a config file
app.config.from_envvar('MINCER_SETTINGS', silent=True)

# Add the database support to our application
db = SQLAlchemy(app)


class HtmlClasses(object):
    """HTML classes used when generating returned HTML contents."""

    """Class used to embed returned content when we have no results."""
    NO_RESULT = "no-result"

    """Class used to embed returned content when we have some results."""
    RESULT = "some-results"


# TODO: Add a selectors_to_remove list of selector that target nodes to remove


class Provider(db.Model):
    """A web data provider for Mincer.

    It can be a search provider or a book list provider."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)
    remote_url = db.Column(db.String, unique=False, nullable=False)
    result_selector = db.Column(db.String, unique=False, nullable=False)
    no_result_selector = db.Column(db.String, unique=False, nullable=False, default="")
    no_result_content = db.Column(db.String, unique=False, nullable=False, default="")

    def __init__(self, **kwargs):
        assert "slug" not in kwargs, "slug is auto-computed and must not be provided"

        # Add the slug param since it is built from name
        kwargs["slug"] = slugify(kwargs["name"])

        super(Provider, self).__init__(**kwargs)


class DatabaseError(Exception):
    """Raised if an non repairable error occured while dealing with database."""
    pass


def init_db():
    """Remove everything from database and then nitialize it with the SQL schema.

    This function must be called at least once before using the database in any way.

    See `Flask-SQLAlchemy Tutorial - A Minimal Application
    <http://flask-sqlalchemy.pocoo.org/2.3/quickstart/#a-minimal-application>`_
    """
    if not os.path.exists(app.instance_path):
        raise DatabaseError(
            "Impossible to create or access database."
            "The instance path {path} used to store "
            "the database does not exist.".format(path=app.instance_path)
            )

    db.drop_all()
    db.create_all()


def load_sample_db():
    """Load some basic providers to the database for test purpose.

    This function needs :function:`init_db` to be called first.
    """
    # Create the providers
    koha_search = Provider(
        name="koha search",
        remote_url="https://koha.bulac.fr/cgi-bin/koha/opac-search.pl?idx=&q={param}&branch_group_limit=",
        result_selector="#userresults .searchresults",
        no_result_selector=".span12 p",
        no_result_content="Aucune réponse trouvée dans le catalogue BULAC.")
    koha_booklist = Provider(
        name="koha booklist",
        remote_url="https://koha.bulac.fr/cgi-bin/koha/opac-shelves.pl?op=view&shelfnumber={param}&sortfield=title",
        result_selector="#usershelves .searchresults")

    providers = [
        koha_search,
        koha_booklist]

    # Add them to the database
    db.session.add_all(providers)

    # Commit the transaction
    db.session.commit()

    return providers


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database via command line.

    See `Flask Tutorial - Creating The Database
    <http://flask.pocoo.org/docs/0.12/tutorial/dbinit/>`_
    """
    try:
        init_db()
    except DatabaseError as e:
        print(e)
        print('*** Database NOT initialized!!!')
    else:
        print('*** Database initialized.')


@app.cli.command('loadsampledb')
def loadsampledb_command():
    """Load some basic providers to the database via command line."""
    try:
        load_sample_db()
    except DatabaseError as e:
        print(e)
        print('*** Sample providers NOT loaded!!!')
        print('    > Did you initialize the database first?')
    else:
        print('*** Sample providers loaded.')


@app.errorhandler(sqlalchemy.exc.OperationalError)
def handle_db_operational_error(err):
    # Improve the error message with revelent advice
    if "unable to open database file" in str(err):
        msg = "{err} - check if you initialized the database using mincer.init_db() function.".format(err=err)
    else:
        msg = str(err)

    app.logger.error(msg)

    abort(INTERNAL_SERVER_ERROR, msg)

@app.route("/")
def home():
    """
    Provide a home page of the server.

    .. :quickref: Home; The home page
    """
    return render_template(
        "home.html",
        providers=Provider.query.order_by(Provider.slug).all(),
        title="Mincer",
        subtitle="Home")


# TODO improve the status page with at least the logo
@app.route("/status")
def status():
    """
    Provide a status page showing if all the adaptation works.

    .. :quickref: Status; Get status of all providers
    """
    app.logger.info(Provider.query.order_by(Provider.slug).all())
    return render_template(
        "status.html",
        providers=Provider.query.order_by(Provider.slug).all(),
        title="Mincer",
        subtitle="Status report")


@app.route("/status/<string:provider_slug>")
def provider_status(provider_slug):
    # Retrieve the provider from database
    provider = Provider.query.filter(Provider.slug == provider_slug).first()
    if not provider:
        app.logger.error(
            'Provider %s was requested for status but this provider name '
            'does not exist.',
            provider_slug)
        abort(NOT_FOUND)

    return render_template(
        "provider_status.html",
        provider=provider,
        title=provider.name,
        subtitle="Status report")


@app.route("/providers/<string:provider_slug>/<string:param>")
@utils.add_response_headers({"Access-Control-Allow-Origin": "*"})
def providers(provider_slug, param):
    """
    Retrieve a search result list from the KOHA server of the BULAC.

    :query string provider_slug: slugified name of the provider as registered
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
    # Retrieve the provider from database
    provider = Provider.query.filter(Provider.slug == provider_slug).first()
    if not provider:
        app.logger.error(
            'Provider %s was asked for "%s" but this provider name '
            'does not exist.',
            provider_slug,
            unquote_plus(param))
        abort(NOT_FOUND)

    # Build the full remote url by replacing param
    full_remote_url = provider.remote_url.format(param=param)

    # Extract the base url from the full url
    remote_host = utils.get_base_url(full_remote_url)

    # Get the content of the page
    # HACK: we force copy the accept-language from the recieved request
    #       see: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language
    page = requests.get(
        full_remote_url,
        headers={'accept-language': 'fr-FR'}).text

    try:
        # Search for an answer in the page
        answer_div = utils.extract_node_from_html(
            selector=provider.result_selector,
            html=page,
            base_url=remote_host)
        return PyQuery(answer_div)\
            .add_class(HtmlClasses.RESULT)\
            .outer_html()
    except utils.NoMatchError:
        app.logger.info(
            'Provider %s was asked for "%s" but no result structure could be '
            'found in it\'s result page. Now searching for a no result '
            'structure...',
            provider_slug,
            unquote_plus(param))

    # TODO: test test the case where this fails for exemple if we have
    #   a "loading page"
    try:
        # Search for a no answer message in the page
        no_answer_div = utils.extract_content_from_html(
            provider.no_result_selector,
            provider.no_result_content,
            page)
        return PyQuery(no_answer_div)\
            .add_class(HtmlClasses.NO_RESULT)\
            .outer_html()
    except utils.NoMatchError:
        # TODO: test this behavior
        app.logger.error(
            'Provider %s was asked for "%s" but neither result structure nor '
            'a no result message could be found in it\'s result page. The '
            'remote url used was <%s>.',
            provider_slug,
            unquote_plus(param),
            full_remote_url)
        # TODO: replace this with a valide answer
        abort(BAD_REQUEST)
