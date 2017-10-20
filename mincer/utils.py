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

# To analyse deeply HTML pages or partials
from pyquery import PyQuery


def once(lst: 'seq[N](bool),N>=0') -> 'bool':
    """
    Return `True` if one and only one element of the sequence is `True`.

    Examples:
        `True` if only one element is `True`...

        >>> once([True, False, False])
        True

        ...whatever the position...

        >>> once([False, True, False])
        True

        ...but false in all other case:

        >>> once([True, True, True])
        False

        >>> once([False, False, False])
        False

        >>> once([True, True, False])
        False
    """
    found_true = False

    for e in lst:
        if e:
            if found_true:
                return False
            else:
                found_true = True
        else:
            continue

    return found_true


class MultipleMatchError(Exception):
    """
    Raised by :func:`extract_content_from_html` and
    :func:`extract_node_from_html` when multiple div are found.
    """
    pass


class NoMatchError(Exception):
    """
    Raised by :func:`extract_content_from_html` and
    :func:`extract_node_from_html` when no div are found.
    """
    pass


def extract_content_from_html(selector, expected_content, html):
    """Extract the content of an HTML node from a HTML document according to a
    JQuery selector and a string mattching that content.

    Arguments:
        selector (str): a JQuery selector query that define how we select the
            desired div in the document.
        expected_content (str): a string that must be present in the selected
            node.
        html (str): a string containing an HTML document..

    Returns:
        str: the selected content encapsuled in a div. There
        could be only one top-level div in the string returned. It may seem
        strange to return exactly the `expected_content` param encapsuled in a
        div but this ensure an interface similar to
        :func:`extract_node_from_html`.

    Raises:
        MultipleMatchError: Multiple div matched the selector query and the
            expected string in the document.
        NoMatchError: No div matched the selector query in the document.

    Examples:
        >>> PAGE = '<!DOCTYPE html><html><div id="hop">hip</div></html>'
        >>> extract_content_from_html("#hop", 'hip', PAGE)
        '<div>hip</div>'
        >>> extract_content_from_html("#hop", 'popopo', PAGE) # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
        NoMatchError
    """
    raw_q = PyQuery(html)
    filtered_q = raw_q(selector)

    # If the first match is empty (meaning no match at all)...
    if not filtered_q.eq(0):
        # ...then it's an error
        raise NoMatchError()

    # If we have more than one match...
    if filtered_q.eq(1):
        # ...then we only have a match if only one node match the content
        if not once(
                [(expected_content in e.text) for e in filtered_q if e.text]):
            raise MultipleMatchError()

    if expected_content not in filtered_q.text():
        raise NoMatchError()

    return "<div>{content}</div>".format(content=expected_content)


def extract_node_from_html(selector, html):
    """
    Extract one div from a html document according to a JQuery selector.

    Arguments:
        selector (str): a JQuery selector query that define how we select the
            desired div in the document.
        html (str): a string containing an HTML document.

    Returns:
        str: the selected div. There could be only one top-level div in the
            string returned.

    Raises:
        MultipleMatchError: Multiple div matched the selector query in the
            document.
        NoMatchError: No div matched the selector query in the document.

    Examples:
        >>> PAGE = '<!DOCTYPE html><html><div id="hop">hip</div></html>'
        >>> extract_node_from_html("#hop", PAGE)
        '<div id="hop">hip</div>'
    """

    raw_q = PyQuery(html)
    filtered_q = raw_q(selector)

    # If the first match is empty (meaning no match at all)...
    if not filtered_q.eq(0):
        # ...then it's an error
        raise NoMatchError()

    # If we have more than one match...
    if filtered_q.eq(1):
        # ...then it's an error
        raise MultipleMatchError()

    return filtered_q.outerHtml()
