import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_with_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "container"})
        self.assertEqual(
            parent_node.to_html(), '<div class="container"><span>child</span></div>'
        )

    def test_to_html_with_multiple_children(self):
        child1 = LeafNode("span", "first")
        child2 = LeafNode("span", "second")
        parent_node = ParentNode("div", [child1, child2])
        self.assertEqual(
            parent_node.to_html(), "<div><span>first</span><span>second</span></div>"
        )

    def test_to_html_no_tag(self):
        node = ParentNode(None, [LeafNode("span", "child")])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_no_children(self):
        node = ParentNode("div", None)
        # Check that to_html() returns an empty node when children are empty
        self.assertEqual(node.to_html(), "<div></div>")

    def test_to_html_empty_children_list(self):
        node = ParentNode("div", [])
        self.assertEqual(node.to_html(), "<div></div>")

    def test_to_html_mixed(self):
        leaf1 = LeafNode("b", "Bold text")
        leaf2 = LeafNode("i", "Italic text")
        leaf3 = LeafNode(None, "Plain text")

        inner_parent = ParentNode("p", [leaf1, leaf2])

        mixed_parent = ParentNode(
            "div",
            [LeafNode("h1", "Heading"), inner_parent, leaf3],
            {"class": "container"},
        )

        expected_html = '<div class="container"><h1>Heading</h1><p><b>Bold text</b><i>Italic text</i></p>Plain text</div>'

        self.assertEqual(mixed_parent.to_html(), expected_html)


class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_url(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            node.to_html(), '<a href="https://www.google.com">Click me!</a>'
        )

    def test_leaf_tag_none(self):
        node = LeafNode(None, "I have tag None!")
        self.assertEqual(node.to_html(), "I have tag None!")

    def test_leaf_value_none(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None).to_html()

    def test_leaf_multiple_attributes(self):
        node = LeafNode(
            "div", "Content", {"id": "main", "class": "container", "data-test": "value"}
        )
        self.assertEqual(
            node.to_html(),
            '<div id="main" class="container" data-test="value">Content</div>',
        )

    def test_leaf_constructor_value_none(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None)

    def test_leaf_other_tags(self):
        img_node = LeafNode("img", "alt text", {"src": "image.jpg"})
        self.assertEqual(img_node.to_html(), '<img src="image.jpg">alt text</img>')

        span_node = LeafNode("span", "Span content", {"class": "highlight"})
        self.assertEqual(
            span_node.to_html(), '<span class="highlight">Span content</span>'
        )


class TestHTMLNode(unittest.TestCase):
    def test_multiple_props(self):
        node = HTMLNode(props={"href": "https://www.google.com", "target": "_blank"})
        assert node.props_to_html() == ' href="https://www.google.com" target="_blank"'

    def test_single_prop(self):
        node = HTMLNode(props={"class": "btn"})
        assert node.props_to_html() == ' class="btn"'

    def test_no_props(self):
        node = HTMLNode(props=None)  # or simply HTMLNode()
        assert node.props_to_html() == ""

    def test_empty_props(self):
        node = HTMLNode(props={})
        assert node.props_to_html() == ""


if __name__ == "__main__":
    unittest.main()
