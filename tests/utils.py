# To analyse deeply HTML pages or partials
from pyquery import PyQuery

# To use design by contract in python
from contracts import contract


# TODO: don't use this since we should only return partials
@contract
def is_html5_page(page: 'str') -> 'bool':
    """Helper function to detect if we have a well formated HTML5 page."""
    has_doctype = page.startswith("<!DOCTYPE html>")
    has_html_open_tag = "<html" in page
    has_html_close_tag = "</html>" in page
    return has_doctype and has_html_open_tag and has_html_close_tag


@contract
def is_div(partial: 'str', cls_name: 'str|None'=None) -> 'bool':
    """Helper function to detect if we have a well formated div partial."""
    d = PyQuery(partial)
    if cls_name:
        return d.is_("div") and d.has_class(cls_name)
    else:
        return d.is_("div")
