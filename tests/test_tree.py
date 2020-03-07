import pytest
from bs4 import BeautifulSoup as BS4Soup

import unittest

from fast_soup import FastSoup, FastHTML5Soup

class TreeTest(unittest.TestCase):

    def soup(self, markup, **kwargs):
        """Build a Beautiful Soup object from markup."""
        return FastHTML5Soup(markup)

    def assertSelects(self, tags, should_match):
        """Make sure that the given tags have the correct text.

        This is used in tests that define a bunch of tags, each
        containing a single string, and then select certain strings by
        some mechanism.
        """
        self.assertEqual([tag.string for tag in tags], should_match)

    def assertSelectsIDs(self, tags, should_match):
        """Make sure that the given tags have the correct IDs.

        This is used in tests that define a bunch of tags, each
        containing a single string, and then select certain strings by
        some mechanism.
        """
        self.assertEqual([tag['id'] for tag in tags], should_match)


class TestFind(TreeTest):
    """Basic tests of the find() method.

    find() just calls find_all() with limit=1, so it's not tested all
    that thouroughly here.
    """

    def test_find_tag(self):
        soup = self.soup("<a>1</a><b>2</b><a>3</a><b>4</b>")
        self.assertEqual(soup.find("b").string, "2")

    def test_unicode_text_find(self):
        soup = self.soup(u'<h1>Räksmörgås</h1>')
        self.assertEqual(soup.find(string=u'Räksmörgås'), u'Räksmörgås')


    def test_unicode_attribute_find(self):
        soup = self.soup(u'<h1 id="Räksmörgås">here it is</h1>')
        self.assertEqual("here it is", soup.find(id=u'Räksmörgås').string)

    def test_find_everything(self):
        """Test an optimization that finds all tags."""
        soup = self.soup("<a>foo</a><b>bar</b>")
        self.assertEqual(5, len(soup.find_all()))

    def test_find_everything_with_name(self):
        """Test an optimization that finds all tags with a given name."""
        soup = self.soup("<a>foo</a><b>bar</b><a>baz</a>")
        self.assertEqual(2, len(soup.find_all('a')))


class TestFindAll(TreeTest):
    """Basic tests of the find_all() method."""

    def test_find_all_text_nodes(self):
        """You can search the tree for text nodes."""
        soup = self.soup("<html>Foo<b>bar</b>\xbb</html>")
        # Exact match.
        self.assertEqual(soup.find_all(string="bar"), [u"bar"])
        self.assertEqual(soup.find_all(text="bar"), [u"bar"])

    @pytest.mark.skip(reason='doesn\'t work with FastSoup yet')
    def test_find_all_text_nodes_multi_values(self):
        """You can search the tree for text nodes."""
        soup = self.soup("<html>Foo<b>bar</b>\xbb</html>")
        # Match any of a number of strings.
        self.assertEqual(
            soup.find_all(text=["Foo", "bar"]), [u"Foo", u"bar"])
        # Match a regular expression.
        self.assertEqual(soup.find_all(text=re.compile('.*')),
                         [u"Foo", u"bar", u'\xbb'])
        # Match anything.
        self.assertEqual(soup.find_all(text=True),
                         [u"Foo", u"bar", u'\xbb'])

    @pytest.mark.skip(reason='doesn\'t work with FastSoup yet')
    def test_find_all_limit(self):
        """You can limit the number of items returned by find_all."""
        soup = self.soup("<a>1</a><a>2</a><a>3</a><a>4</a><a>5</a>")
        self.assertSelects(soup.find_all('a', limit=3), ["1", "2", "3"])
        self.assertSelects(soup.find_all('a', limit=1), ["1"])
        self.assertSelects(
            soup.find_all('a', limit=10), ["1", "2", "3", "4", "5"])

        # A limit of 0 means no limit.
        self.assertSelects(
            soup.find_all('a', limit=0), ["1", "2", "3", "4", "5"])

    @pytest.mark.skip(reason='doesn\'t work with FastSoup yet')
    def test_calling_a_tag_is_calling_findall(self):
        soup = self.soup("<a>1</a><b>2<a id='foo'>3</a></b>")
        self.assertSelects(soup('a', limit=1), ["1"])
        self.assertSelects(soup.b(id="foo"), ["3"])

    @pytest.mark.skip(reason='doesn\'t work with FastSoup yet')
    def test_find_all_with_self_referential_data_structure_does_not_cause_infinite_recursion(self):
        soup = self.soup("<a></a>")
        # Create a self-referential list.
        l = []
        l.append(l)

        # Without special code in _normalize_search_value, this would cause infinite
        # recursion.
        self.assertEqual([], soup.find_all(l))

    @pytest.mark.skip(reason='doesn\'t work with FastSoup yet')
    def test_find_all_resultset(self):
        """All find_all calls return a ResultSet"""
        soup = self.soup("<a></a>")
        result = soup.find_all("a")
        self.assertTrue(hasattr(result, "source"))

        result = soup.find_all(True)
        self.assertTrue(hasattr(result, "source"))

        result = soup.find_all(text="foo")
        self.assertTrue(hasattr(result, "source"))
