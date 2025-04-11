import unittest
import textwrap
from markdown import (
    markdown_to_blocks,
    block_to_block_type,
    BlockType,
    markdown_to_html_node,
    handle_quote,
    handle_unordered,
    handle_ordered,
)
from htmlnode import *
from textnode import *


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_paragraphs(self):
        md = textwrap.dedent(
            """
            This is **bolded** paragraph
            text in a p
            tag here

            This is another paragraph with _italic_ text and `code` here
        """
        )

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = textwrap.dedent(
            """
            ```
            This is text that _should_ remain
            the **same** even with inline stuff
            ```
        """
        )

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_paragraph(self):
        block = "This is a simple paragraph with no special formatting."
        self.assertEqual(block_to_block_type(block), BlockType.paragraph)

        block = "This paragraph\nhas multiple\nlines."
        self.assertEqual(block_to_block_type(block), BlockType.paragraph)

    def test_heading(self):
        block = "# This is a heading level 1"
        self.assertEqual(block_to_block_type(block), BlockType.heading)

        block = "## This is a heading level 2"
        self.assertEqual(block_to_block_type(block), BlockType.heading)

        block = "###### This is a heading level 6"
        self.assertEqual(block_to_block_type(block), BlockType.heading)

        # Not a heading - no space after #
        block = "#This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.paragraph)

    def test_code_block(self):
        block = "```\nprint('Hello, world!')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.code)

        block = "```python\ndef function():\n    return True\n```"
        self.assertEqual(block_to_block_type(block), BlockType.code)

        # Not a code block - missing closing backticks
        block = "```\nThis is not a complete code block"
        self.assertEqual(block_to_block_type(block), BlockType.paragraph)

    def test_quote(self):
        # Single line quote
        block = ">This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.quote)

        # Multi-line quote
        block = ">This is a quote\n>that spans\n>multiple lines"
        self.assertEqual(block_to_block_type(block), BlockType.quote)

        # Not a quote - missing > on second line
        block = ">This starts as a quote\nBut this line isn't quoted"
        self.assertEqual(block_to_block_type(block), BlockType.paragraph)

        # Empty quote lines are still quotes if they have >
        block = ">First line\n>\n>Third line"
        self.assertEqual(block_to_block_type(block), BlockType.quote)

    def test_unordered(self):
        # Single item unordered list
        block = "- This is an unordered item"
        self.assertEqual(block_to_block_type(block), BlockType.unordered_list)

        # Multi-line unordered list
        block = "- This is an unordered\n- List with multiple\n- items"
        self.assertEqual(block_to_block_type(block), BlockType.unordered_list)

        # Not an unordered list - missing space after hyphen
        block = "-This doesn't have a space after the hyphen"
        self.assertEqual(block_to_block_type(block), BlockType.paragraph)

        # Not an unordered list - one line doesn't start with "- "
        block = "- First item\nSecond item without hyphen\n- Third item"
        self.assertEqual(block_to_block_type(block), BlockType.paragraph)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
            This is **bolded** paragraph

            This is another paragraph with _italic_ text and `code` here
            This is the same paragraph on a new line

            - This is a list
            - with items
            """
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_basic_blocks(self):
        """Test basic block separation with different block types."""
        md = """# Heading

            Paragraph with **bold** text.

            - List item 1
            - List item 2
            """

        expected = [
            "# Heading",
            "Paragraph with **bold** text.",
            "- List item 1\n- List item 2",
        ]

        self.assertEqual(markdown_to_blocks(md), expected)

    def test_extra_whitespace(self):
        """Test handling of extra whitespace and blank lines."""
        md = """
            # Heading with space above

            Paragraph with space above and below

            - List with extra space
            - Indented item
            """

        expected = [
            "# Heading with space above",
            "Paragraph with space above and below",
            "- List with extra space\n- Indented item",
        ]

        self.assertEqual(markdown_to_blocks(md), expected)

    def test_inline_newlines(self):
        """Test preservation of newlines within a block."""
        md = """
                Paragraph with
                multiple lines
                but no blank lines.

                Another paragraph.
            """

        expected = [
            "Paragraph with\nmultiple lines\nbut no blank lines.",
            "Another paragraph.",
        ]

        self.assertEqual(markdown_to_blocks(md), expected)

    def test_code_blocks(self):
        """Test handling of code blocks with triple backticks."""
        md = textwrap.dedent(
            """
            # Code Example

            ```python
            def hello():
                print("Hello world!")
            ```

            Regular paragraph.
            """
        )
        expected = [
            "# Code Example",
            '```python\ndef hello():\n    print("Hello world!")\n```',
            "Regular paragraph.",
        ]

        self.assertEqual(markdown_to_blocks(md), expected)

    def test_quote_block(self):
        # Example of markdown quote block
        quote_block = (
            "> This is a quote\n> With multiple lines\n> And some **bold** text"
        )

        # Call your function (replace 'handle_quote_block' with your actual function name)
        result = handle_quote(quote_block)

        # The expected HTML output
        expected_html = "<blockquote>This is a quote\nWith multiple lines\nAnd some <b>bold</b> text</blockquote>"

        # Assert that the function produces the expected HTML
        assert (
            result.to_html() == expected_html
        ), f"Expected {expected_html}, but got {result.to_html()}"
        print("Quote block test passed!")

    def test_unordered_list(self):
        # Example of markdown unordered list
        unordered_list = (
            "- First item\n- Second item with **bold**\n- Third item with _italic_"
        )

        # Call your function (replace with your actual function name)
        result = handle_unordered(unordered_list)

        # The expected HTML output for an unordered list
        expected_html = "<ul><li>First item</li><li>Second item with <b>bold</b></li><li>Third item with <i>italic</i></li></ul>"

        # Assert that the function produces the expected HTML
        assert (
            result.to_html() == expected_html
        ), f"Expected {expected_html}, but got {result.to_html()}"
        print("Unordered list test passed!")

    def test_ordered_list(self):
        # Example of markdown ordered list
        ordered_list = "1. First ordered item\n2. Second item with **bold**\n3. Third item with _italic_"

        # Call your function
        result = handle_ordered(ordered_list)

        # The expected HTML output for an ordered list
        expected_html = "<ol><li>First ordered item</li><li>Second item with <b>bold</b></li><li>Third item with <i>italic</i></li></ol>"

        # Assert that the function produces the expected HTML
        assert (
            result.to_html() == expected_html
        ), f"Expected {expected_html}, but got {result.to_html()}"
        print("Ordered list test passed!")
