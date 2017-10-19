# Module we are going to test
import mincer

# Unittesting module made simple !
import pytest

# Some useful func to analyse strings and determine if they are HTML
from tests.utils import is_div


class TestExtractContentFromHtml(object):
    def test_detect_matching_content(self):
        CONTENT_TO_MATCH = "ca va matcher"
        TARGET_NODE = '<div class="cible" id="bob">{content}</div>'.format(
            content=CONTENT_TO_MATCH)
        PAGE = """<!DOCTYPE html>
            <html lang="fr">
                <head>
                    <meta charset="utf-8">
                    <title>test page</title>
                </head>
                <body>
                    {node}
                </body>
            </html>""".format(node=TARGET_NODE)
        QUERY = ".cible#bob"

        res = mincer.utils.extract_content_from_html(
            QUERY, CONTENT_TO_MATCH, PAGE)

        assert is_div(res)
        assert CONTENT_TO_MATCH in res

    def test_fail_on_not_matching_content(self):
        CONTENT_TO_MATCH = "ca va matcher"
        FAILING_MATCH = "ou pas"
        TARGET_NODE = '<div class="cible" id="bob">{content}</div>'.format(
            content=CONTENT_TO_MATCH)
        PAGE = """<!DOCTYPE html>
            <html lang="fr">
                <head>
                    <meta charset="utf-8">
                    <title>test page</title>
                </head>
                <body>
                    {node}
                </body>
            </html>""".format(node=TARGET_NODE)
        QUERY = ".cible#bob"

        with pytest.raises(mincer.utils.NoMatchError):
            mincer.utils.extract_content_from_html(QUERY, FAILING_MATCH, PAGE)

    def test_detect_multimatch_for_query_and_single_match_for_content(self):
        CONTENT_TO_MATCH = "oui"
        FAILING_MATCH = "non"
        TARGET_MATCH = '<div class="cible" id="bob">{content}</div>'.format(
            content=CONTENT_TO_MATCH)
        TARGET_NO_MATCH = '<div class="cible" id="bob">{content}</div>'.format(
            content=FAILING_MATCH)
        PAGE = """<!DOCTYPE html>
            <html lang="fr">
                <head>
                    <meta charset="utf-8">
                    <title>test page</title>
                </head>
                <body>
                    {target_1}
                    {target_2}
                </body>
            </html>""".format(target_1=TARGET_MATCH, target_2=TARGET_NO_MATCH)
        QUERY = ".cible#bob"

        res = mincer.utils.extract_content_from_html(QUERY, CONTENT_TO_MATCH, PAGE)

        assert is_div(res)
        assert CONTENT_TO_MATCH in res

    def test_fail_on_multimatch_for_query_and_multimatch_for_content(self):
        CONTENT_TO_MATCH = "rien a faire"
        TARGET = '<div class="cible" id="bob">{content}</div>'.format(
            content=CONTENT_TO_MATCH)
        PAGE = """<!DOCTYPE html>
            <html lang="fr">
                <head>
                    <meta charset="utf-8">
                    <title>test page</title>
                </head>
                <body>
                    {target_1}
                    {target_2}
                </body>
            </html>""".format(target_1=TARGET, target_2=TARGET)
        QUERY = ".cible#bob"

        with pytest.raises(mincer.utils.MultipleMatchError):
            mincer.utils.extract_content_from_html(QUERY, CONTENT_TO_MATCH, PAGE)


class TestExtractNodeFromHtml(object):
    def test_should_succced_from_simple_page(self):
        TARGET = '<div class="cible" id="bob">du contenu</div>'
        PAGE = """<!DOCTYPE html>
            <html lang="fr">
                <head>
                    <meta charset="utf-8">
                    <title>test page</title>
                </head>
                <body>
                    {target}
                </body>
            </html>""".format(target=TARGET)
        QUERY = ".cible#bob"

        res = mincer.utils.extract_node_from_html(QUERY, PAGE)

        assert res == TARGET

    def test_should_fail_from_page_with_multimatch(self):
        TARGET_1 = '<div class="cible" id="bob">du contenu</div>'
        TARGET_2 = '<div class="cible" id="bob">et encore du contenu</div>'
        PAGE = """<!DOCTYPE html>
            <html lang="fr">
                <head>
                    <meta charset="utf-8">
                    <title>test page</title>
                </head>
                <body>
                    {target_1}
                    {target_2}
                </body>
            </html>""".format(target_1=TARGET_1, target_2=TARGET_2)
        QUERY = ".cible#bob"

        # The function should fail if trying to extract a not unique div
        with pytest.raises(mincer.utils.MultipleMatchError):
            mincer.utils.extract_node_from_html(QUERY, PAGE)

    def test_should_fail_from_page_without_match(self):
        NOT_TARGET = '<div class="pas-cible" id="bob">du contenu</div>'
        PAGE = """<!DOCTYPE html>
            <html lang="fr">
                <head>
                    <meta charset="utf-8">
                    <title>test page</title>
                </head>
                <body>
                    {target}
                </body>
            </html>""".format(target=NOT_TARGET)
        QUERY = ".cible#bob"

        # The function should fail if trying to extract a not unique div
        with pytest.raises(mincer.utils.NoMatchError):
            mincer.utils.extract_node_from_html(QUERY, PAGE)
