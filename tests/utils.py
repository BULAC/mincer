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

# To elegantly analyze urls
from urllib.parse import urlparse

# To analyse deeply HTML pages or partials
from pyquery import PyQuery


def is_html5_page(page):
    """Helper function to detect if we have a well formated HTML5 page.

    Params:
        page (str): the page to test.

    Returns:
        bool: True if the page is a well formated HTML5 page, False if not.

    Examples:
        >>> is_html5_page("<!DOCTYPE html><html>Hello</html>")
        True
    """
    has_doctype = page.startswith("<!DOCTYPE html>")
    has_html_open_tag = "<html" in page
    has_html_close_tag = "</html>" in page
    return has_doctype and has_html_open_tag and has_html_close_tag


def is_div(partial, cls_name=None):
    """Helper function to detect if we have a well formated div partial.

    Params:
        partial (str): an HTML content (partial HTML code) page to test.
        class_name (str|None): if not `None` the name of the class that the div
            in `partial` must have.

    Returns:
        bool: True if `partial` is a well formated div page with the provided
            class (if provided), False if not.

    Examples:
        >>> is_div("<div>Plop</div>")
        True

        >>> is_div("<span>Plop</span>")
        False

        >>> is_div("<!DOCTYPE html><html>Hello</html>")
        False

        >>> is_div('<div class="useful">Plop</div>', "useful")
        True

        >>> is_div('<div class="useless">Plop</div>', "useful")
        False
    """
    d = PyQuery(partial)
    if cls_name:
        return d.is_("div") and d.has_class(cls_name)
    else:
        return d.is_("div")


def has_page_title(page, title):
    """Helper function to detect if a page as a specific title defined in it's
    <head> section.

    Params:
        page (str): an HTML page to test.
        title (str): title to look for in the page.

    Returns:
        bool: True if `page` has the correct title in it's <head> section,
            False if not.

    Examples:
        >>> has_page_title("<!DOCTYPE html><html><head><title>hello</title></head></html>", "hello")
        True

        >>> has_page_title("<!DOCTYPE html><html><head><title>hello</title></head></html>", "nonono")
        False

        >>> has_page_title("<!DOCTYPE html><html><head></head></html>", "hello")
        False
    """
    d = PyQuery(page)

    return title == d("head>title").text()


def has_header_title(page, title):
    """Helper function to detect if a page as a specific <h1> title defined
    in it's `body header` section.

    All whitespace before and after the title are removed before comparison.

    Any subtitle (in the boostrap sense: h1>small) is removed before
    comparison.

    Params:
        page (str): an HTML page to test.
        title (str): title to look for in the page.

    Returns:
        bool: True if `page` has the correct title in its `body header h1`, False if not.

    Examples:
        >>> has_header_title("<!DOCTYPE html><html><body><header><h1>hello</h1></header></body></html>", "hello")
        True

        >>> has_header_title("<!DOCTYPE html><html><body><header><img><h1>hello</h1></header></body></html>", "hello")
        True

        >>> has_header_title("<!DOCTYPE html><html><body><header>hello</header></body></html>", "hello")
        False

        >>> has_header_title("<!DOCTYPE html><html><body><h1>hello</h1></body></html>", "hello")
        False

        >>> has_header_title("<!DOCTYPE html><html><body>hello</body></html>", "hello")
        False

        >>> has_header_title("<!DOCTYPE html><html><body><header><h1>hello</h1></header></body></html>", "nonono")
        False

        >>> has_header_title("<!DOCTYPE html><html><body><header><h1>hello<small>subhello</small></h1></header></body></html>", "hello")
        True

        >>> has_header_title("<!DOCTYPE html><html><body><header><h1>hello <small>subhello</small></h1></header></body></html>", "hello")
        True
    """
    d = PyQuery(page)
    selected = d("body header h1")
    cleaned = selected.remove("small")

    return title == cleaned.text().strip()


def has_header_subtitle(page, subtitle):
    """Helper function to detect if a page as a specific h1>small subtitle
    defined in it's `body header` section.

    All whitespace before and after the title are removed before comparison.

    It's a subtitle as defined in the Bootstrap documentation.

    Params:
        page (str): an HTML page to test.
        subtitle (str): subtitle to look for in the page.

    Returns:
        bool: True if `page` has the correct subtitle defined in
            its body header h1>small, False if not.

    Examples:
        >>> has_header_subtitle("<!DOCTYPE html><html><body><header><h1>hello<small>world</small></h1></header></body></html>", "world")
        True

        >>> has_header_subtitle("<!DOCTYPE html><html><body><header><img><h1>hello<small>world</small></h1></header></body></html>", "world")
        True

        >>> has_header_subtitle("<!DOCTYPE html><html><body><header><h1>hello <small>world</small></h1></header></body></html>", "world")
        True

        >>> has_header_subtitle("<!DOCTYPE html><html><body><header><h1>hello<small> world</small></h1></header></body></html>", "world")
        True

        >>> has_header_subtitle("<!DOCTYPE html><html><body><header><h1>hello<small>world</small></h1></header></body></html>", "nonono")
        False

        >>> has_header_subtitle("<!DOCTYPE html><html><body><h1>hello</h1></body></html>", "hello")
        False
    """
    d = PyQuery(page)
    selected = d("body header h1>small")

    return subtitle == selected.text().strip()


def all_links(page):
    """Helper function that returns all `<a>` link `href` content.

    Params:
        page (str): an HTML page to analyse.

    Returns:
        list(str): List of `href` content of all the `<a>` elements in the
            page.

    Examples:
        >>> all_links('<a href="toto">le toto</a><a href="tutu">le tutu</a>')
        ['toto', 'tutu']

        >>> all_links('<a href="toto">le toto</a><a>le tutu</a>')
        ['toto']

        >>> all_links('<div><a href="toto">le toto</a><a href="tutu">le tutu</a></div>')
        ['toto', 'tutu']
    """
    d = PyQuery(page)

    return [e.attrib["href"] for e in d("a") if "href" in e.attrib]


def has_table(page):
    """Helper function to detect if a page contains at least one table element.

    Params:
        page (str): an HTML page to analyse.

    Returns:
        bool: True if the page contains at least one `<table>` element,
            False if not.

    Examples:
        >>> has_table("<html><body><table></table></body></html>")
        True

        >>> has_table("<html><body><table></table><table></table></body></html>")
        True

        >>> has_table("<html><body></body></html>")
        False
    """
    d = PyQuery(page)

    return d("table") != []


def has_form(page):
    """Helper function to detect if a page contains at least one form element.

    Params:
        page (str): an HTML page to analyse.

    Returns:
        bool: True if the page contains at least one `<form>` element,
            False if not.

    Examples:
        >>> has_form("<html><body><form></form></body></html>")
        True

        >>> has_form("<html><body><form></form><form></form></body></html>")
        True

        >>> has_form("<html><body></body></html>")
        False
    """
    d = PyQuery(page)

    return d("form") != []


def has_form_submit_button(page):
    """Helper function to detect if a page contains at least one form submit
    button.

    Params:
        page (str): an HTML page to analyse.

    Returns:
        bool: True if the page contains at least one `<button type="submit">`
            element in a `<form>` element, False if not.

    Examples:
        >>> has_form_submit_button('<html><body><form><button type="submit">Click me</button></form></body></html>')
        True

        >>> has_form_submit_button('<html><body><button type="submit">Click me</button></body></html>')
        False

        >>> has_form_submit_button('<html><body><form><button>Click me</button></form></body></html>')
        False
    """
    d = PyQuery(page)

    buttons = d("form button")

    submit_buttons = [
        e for e in buttons if e.attrib.get("type", "") == "submit"]

    return submit_buttons != []


def has_sub_div(partial):
    """Helper function to detect if a partial has direct div child.

    Params:
        partial (str): an HTML partial to analyse it must be a div element.

    Returns:
        bool: True if the partial contains at least one `<div>` element as a
            direct child,
            False if not.

    Examples:
        >>> has_sub_div("<div><div></div></div>")
        True

        >>> has_sub_div("<div><div></div><div></div><div></div></div>")
        True

        >>> has_sub_div("<div></div>")
        False

        >>> has_sub_div("<section><div></div></section>")
        False
    """
    d = PyQuery(partial)

    if not d(":root").is_("div"):
        return False

    if d(":root>div") == []:
        return False

    return True


def all_sub_div(partial):
    """Helper function that returns all the direct sub div of the given partial.

    Params:
        partial (str): an HTML partial to analyse it must be a div element.

    Returns:
        list(str): List of the content of all the direct `div` child elements
            in the partial.
            Empty list if the root element is not a div or if not direct div child exist.

    Examples:
        >>> all_sub_div('<div></div>')
        []

        >>> all_sub_div('<section></section>')
        []

        >>> all_sub_div('<div><div>toto</div><div>titi</div></div>')
        ['toto', 'titi']

        >>> all_sub_div('<div><div>toto</div></div>')
        ['toto']

        >>> all_sub_div('<section><div>toto</div></section>')
        []
    """
    d = PyQuery(partial)

    if not d(":root").is_("div"):
        return []

    return [elem.text for elem in d(":root>div")]


def all_table_column_headers(page):
    """Helper function that returns all table column headers.

    Params:
        page (str): an HTML page to analyse.

    Returns:
        list(str): List of the content of all `table thead th` elements with
            `scope="col"` in the page.

    Examples:
        >>> all_table_column_headers('<html><body><table><thead><tr><th scope="col">toto</th><th scope="col">titi</th></tr></thead></table></body></html>')
        ['toto', 'titi']

        >>> all_table_column_headers('<html><body><table><thead><tr><th>toto</th><th>titi</th></tr></thead></table></body></html>')
        []

        >>> all_table_column_headers('<html><body><table><tbody><tr><th>rowtoto</th><th>rowtiti</th></tr></tbody></table></body></html>')
        []
    """
    d = PyQuery(page)
    selected = d("table thead th")

    return [e.text for e in selected if e.attrib.get("scope", "") == "col"]


def all_form_groups(page):
    """Helper function that returns all div .form-group as a dict.

    Params:
        page (str): an HTML page to analyse.

    Returns:
        dict of str to str: Dict mapping label text to input value.

    Examples:
        >>> all_form_groups('<html><body><form><div class="form-group"><label>lablab</label><input value="toto"></div></form></body></html>')
        {'lablab': 'toto'}

        >>> all_form_groups('<html><body><form><div class="form-group"><label>lablab</label><input value=""></div></form></body></html>')
        {'lablab': ''}
    """
    d = PyQuery(page)
    selected = d("form .form-group")

    res = {}
    for grp in selected.items():
        label = grp("label").text()
        input_val = grp("input").val()
        res[label] = input_val

    return res


def is_absolute_url(url):
    """Helper function that tells whether or not a given url is absolute.

    Any url is in the form ``scheme://netloc/path;parameters?query#fragment``
    and this function detects url where the ``netloc`` part is correctly
    introduce by a ``//``. Otherwise the url is considered relative.

    Params:
        url (str): Url to analyze.

    Returns:
        bool: True if the link netloc is introduce by a valid ``//``. For more
            details see `URL Parsinf documentation
            <https://docs.python.org/3.5/library/urllib.parse.html#url-parsing>`_

    Examples:
        >>> is_absolute_url("http://myhost.com")
        True

        >>> is_absolute_url("http://myhost.com/anything.html")
        True

        >>> is_absolute_url("/myhost.com")
        False

        >>> is_absolute_url("/bip/bap/bop.html")
        False
    """
    return urlparse(url).netloc != ''
