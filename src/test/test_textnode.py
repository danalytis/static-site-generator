import unittest

from textnode import (
    TextNode,
    TextType,
    text_node_to_html_node,
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
)


class TestExtractMarkdown(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_noteq(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertNotEqual([("image", "https://i.imgur.com/jcczJZK.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            matches,
        )

    def test_extract_markdown_links_noteq(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertNotEqual(
            [("boot dev", "www.boot.dev"), ("youtube", "www.youtube.com/@notbootdev")],
            matches,
        )

    def test_multiple_images(self):
        matches = extract_markdown_images(
            "Here are two images: ![first](https://example.com/1.png) and ![second](https://example.com/2.png)"
        )
        self.assertListEqual(
            [
                ("first", "https://example.com/1.png"),
                ("second", "https://example.com/2.png"),
            ],
            matches,
        )

    def test_extract_markdown_images_empty(self):
        text = "This is text with no images"
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)

    def test_extract_markdown_images_special_chars(self):
        text = "Image with special chars: ![image with spaces & symbols!](https://example.com/pic.jpg)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [("image with spaces & symbols!", "https://example.com/pic.jpg")], matches
        )

    def test_extract_markdown_links_special_chars(self):
        text = "Link with special chars: [link with spaces & symbols!](https://example.com/page)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [("link with spaces & symbols!", "https://example.com/page")], matches
        )

    def test_extract_markdown_links_complex_urls(self):
        text = "Link with query params: [complex link](https://example.com/search?q=python&sort=relevance#section1)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [
                (
                    "complex link",
                    "https://example.com/search?q=python&sort=relevance#section1",
                )
            ],
            matches,
        )

    def test_extract_markdown_images_ignores_links(self):
        text = "Here's an image ![cat](https://example.com/cat.jpg) and a [regular link](https://example.com/page)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("cat", "https://example.com/cat.jpg")], matches)

    def test_extract_markdown_links_ignores_images(self):
        text = "Here's an image ![cat](https://example.com/cat.jpg) and a [regular link](https://example.com/page)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("regular link", "https://example.com/page")], matches)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is another node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_url_none(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD, url=None)
        self.assertEqual(node, node2)

    def test_text_prop(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("This is bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is bold text")

    def test_italic(self):
        node = TextNode("This is italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is italic text")

    def test_code(self):
        node = TextNode("let x = 10;", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "let x = 10;")

    def test_link(self):
        node = TextNode("Click here", TextType.LINK, url="https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props["href"], "https://example.com")

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, url="image.jpg")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")

    def test_parameterized_split_nodes(self):
        test_cases = [
            {
                "desc": "Basic case with inline code block",
                "input": [TextNode("Here is `a code block` in text.", TextType.TEXT)],
                "delimiter": "`",
                "text_type": TextType.CODE,
                "expected": [
                    TextNode("Here is ", TextType.TEXT),
                    TextNode("a code block", TextType.CODE),
                    TextNode(" in text.", TextType.TEXT),
                ],
            },
            {
                "desc": "Bold text with ** delimiter",
                "input": [TextNode("This has **bold text** in it", TextType.TEXT)],
                "delimiter": "**",
                "text_type": TextType.BOLD,
                "expected": [
                    TextNode("This has ", TextType.TEXT),
                    TextNode("bold text", TextType.BOLD),
                    TextNode(" in it", TextType.TEXT),
                ],
            },
            {
                "desc": "Italic text with _ delimiter",
                "input": [TextNode("This has _italic text_ in it", TextType.TEXT)],
                "delimiter": "_",
                "text_type": TextType.ITALIC,
                "expected": [
                    TextNode("This has ", TextType.TEXT),
                    TextNode("italic text", TextType.ITALIC),
                    TextNode(" in it", TextType.TEXT),
                ],
            },
            {
                "desc": "Text starting with a delimiter",
                "input": [TextNode("`Code block` at the beginning", TextType.TEXT)],
                "delimiter": "`",
                "text_type": TextType.CODE,
                "expected": [
                    TextNode("Code block", TextType.CODE),
                    TextNode(" at the beginning", TextType.TEXT),
                ],
            },
            {
                "desc": "Text ending with a delimiter",
                "input": [TextNode("Code block at the `ending`", TextType.TEXT)],
                "delimiter": "`",
                "text_type": TextType.CODE,
                "expected": [
                    TextNode("Code block at the ", TextType.TEXT),
                    TextNode("ending", TextType.CODE),
                ],
            },
            {
                "desc": "Missing closing delimiter should raise an exception",
                "input": [TextNode("Oops, this `doesn't close", TextType.TEXT)],
                "delimiter": "`",
                "text_type": TextType.CODE,
                "expected": None,  # Expecting an exception
            },
            {
                "desc": "multiple delimiter pairs",
                "input": [
                    TextNode(
                        "Text with `code here` and `more code` in it.", TextType.TEXT
                    )
                ],
                "delimiter": "`",
                "text_type": TextType.CODE,
                "expected": [
                    TextNode("Text with ", TextType.TEXT),
                    TextNode("code here", TextType.CODE),
                    TextNode(" and ", TextType.TEXT),
                    TextNode("more code", TextType.CODE),
                    TextNode(" in it.", TextType.TEXT),
                ],
            },
        ]
        for case in test_cases:
            with self.subTest(msg=case["desc"]):
                try:
                    result = split_nodes_delimiter(
                        case["input"], case["delimiter"], case["text_type"]
                    )
                    # print(f"Test: {case['desc']}")
                    # print(f"Expected: {[str(n.text) for n in case['expected']]}")
                    # print(f"Got: {[str(n.text) for n in result]}")

                    self.assertEqual(result, case["expected"])
                except Exception as e:
                    if case["expected"] is None:
                        # print(f"Expected exception for: {case['desc']}")
                        self.assertTrue(True)  # Test passes if exception is expected
                    else:
                        # print(f"Unexpected failure for: {case['desc']}")
                        raise e  # Fail the test


if __name__ == "__main__":
    unittest.main()
