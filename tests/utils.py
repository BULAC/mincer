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


# TODO: don't use this since we should only return partials
def is_html5_page(page):
    """Helper function to detect if we have a well formated HTML5 page.

    Params:
        page (str): the page to test.

    Returns:
        bool: True if the page is a well formated HTML5 page, False if not.
    """
    has_doctype = page.startswith("<!DOCTYPE html>")
    has_html_open_tag = "<html" in page
    has_html_close_tag = "</html>" in page
    return has_doctype and has_html_open_tag and has_html_close_tag


def is_div(partial: 'str', cls_name: 'str|None'=None) -> 'bool':
    """Helper function to detect if we have a well formated div partial.

    Params:
        partial (str): an HTML content (partial HTML code) page to test.
        class_name (str|None): if not `None` the name of the class that the div
            in `partial` must have.

    Returns:
        bool: True if `partial` is a well formated div page with the provided
            class (if provided), False if not.
    """
    d = PyQuery(partial)
    if cls_name:
        return d.is_("div") and d.has_class(cls_name)
    else:
        return d.is_("div")
