from enum import Enum
from htmlnode import *
from textnode import *
import re


class BlockType(Enum):
    paragraph = "paragraph"
    heading = "heading"
    code = "code"
    quote = "quote"
    unordered_list = "unordered_list"
    ordered_list = "ordered_list"


def text_to_children(text):
    """
    Converts text with inline markdown to a list of HTMLNode objects
    """
    # First create a single text node with the entire text
    nodes = [TextNode(text, TextType.TEXT)]

    # Then split nodes by different delimiters in sequence
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)  # For bold text
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)  # For italic text
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)  # For inline code
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    # Convert each TextNode to an HTMLNode
    html_nodes = []
    for node in nodes:
        html_node = text_node_to_html_node(node)
        html_nodes.append(html_node)

    return html_nodes


def handle_code_block(block):
    # Preserve the original block to check for a trailing newline later
    original_block = block
    # Carefully handle the opening and closing lines
    lines = block.splitlines(keepends=True)
    if lines[0].strip() == "```":  # Match opening backticks specifically
        lines = lines[1:]
    if lines[-1].strip() == "```":  # Match closing backticks specifically
        lines = lines[:-1]

    # Then join the remaining lines without altering their internal formatting
    code_content = "".join(lines)
    # print(f"Code block content before TextNode creation: {repr(code_content)}")
    # Add a trailing newline if the original block ended with one
    if original_block.endswith("\n"):
        code_content += "\n"

    # Create text node with the raw content
    text_node = TextNode(code_content, TextType.TEXT)
    html_text_node = text_node_to_html_node(text_node)

    # Create code and pre nodes
    code_node = HTMLNode("code", None, [html_text_node], None)
    pre_node = HTMLNode("pre", None, [code_node], None)

    return pre_node


def handle_unordered(block):
    # Split the block into lines (list items)
    items = block.split("\n")

    # Create list item nodes
    list_items = []
    for item in items:
        # Remove the list marker and leading space
        if item.startswith("- "):
            content = item[2:]
        elif item.startswith("* "):
            content = item[2:]
        else:
            content = item  # Fallback

        # Create a list item node with proper children
        li_node = HTMLNode("li", None, text_to_children(content), {})
        list_items.append(li_node)

    # Create the unordered list node with list items as children
    return HTMLNode("ul", None, list_items, {})


def handle_ordered(block):
    # Split the block into list items
    items = block.split("\n")

    # Create list item nodes
    list_items = []
    for item in items:
        # Check for the ordered list pattern: number followed by period and space
        if item and (
            len(item) >= 2
            and item[0].isdigit()
            and item[1] == "."
            and (len(item) == 2 or item[2] == " ")
        ):
            # Find the position after the number and period
            pos = 2
            # Skip any additional space
            if len(item) > pos and item[pos] == " ":
                pos += 1

            # Extract the content after the list marker
            content = item[pos:]
        else:
            content = item  # Fallback case

        # Create a list item node with proper children
        li_node = HTMLNode("li", None, text_to_children(content), {})
        list_items.append(li_node)

    # Create the ordered list node with list items as children
    return HTMLNode("ol", None, list_items, {})


def handle_quote(block):
    lines = block.split("\n")
    content = "\n".join(
        [
            (
                line[2:]
                if line.startswith("> ")
                else line[:1] if line.startswith(">") else line
            )
            for line in lines
        ]
    )

    children = text_to_children(content)

    return HTMLNode("blockquote", None, children, {})


def handle_paragraph(block):
    text = " ".join([line.strip() for line in block.split("\n")])
    children = text_to_children(text)
    return HTMLNode("p", None, children, None)


def markdown_to_html_node(markdown):
    """
    Converts a markdown string into a single parent HTMLNode containing
    child nodes that represent the parsed markdown content.

    Args:
        markdown (str): A string containing markdown content

    Returns:
        HTMLNode: A div node containing all converted markdown as child nodes
    """

    blocks = markdown_to_blocks(markdown)
    div = HTMLNode("div", None, [])

    for block in blocks:
        block_type = block_to_block_type(block)
        match block_type:
            case BlockType.paragraph:
                # create a paragraph node and add to div children
                paragraph_node = handle_paragraph(block)
                div.children.append(paragraph_node)

            case BlockType.heading:
                # Extract the heading level (number of # symbols)
                level = 0
                for char in block:
                    if char == "#":
                        level += 1
                    else:
                        break

                # Ensure level is between 1 and 6
                level = min(level, 6)

                # Extract the heading text (removing the # symbols and leading space)
                heading_text = block[level:].strip()

                # Process inline markdown in the heading text
                children = text_to_children(heading_text)

                # Create heading node with appropriate tag (h1-h6)
                heading_node = HTMLNode(f"h{level}", None, children, None)

                # Add to div children
                div.children.append(heading_node)

            case BlockType.code:
                # Use your helper function for code blocks
                pre_node = handle_code_block(block)
                # Add the resulting <pre> node to the div's children
                div.children.append(pre_node)

            case BlockType.quote:
                # each line starts with >
                # quote blocks should be surrounded by <blockquote> tag
                quote_node = handle_quote(block)
                div.children.append(quote_node)
            case BlockType.unordered_list:
                # each line starts with -
                # unordered list blocks should be surrounded by <ul> tag and each item surrounded with <li> tag
                unordered_node = handle_unordered(block)
                div.children.append(unordered_node)
            case BlockType.ordered_list:
                # 1. item 2. item
                # ordered list should be surrounded by <ol> tag and each item surrounded with <li> tag
                ordered_node = handle_ordered(block)
                div.children.append(ordered_node)

    return div


def block_to_block_type(block):
    """
    Determines the type of a markdown block.

    Args:
        block (str): A string containing a block of markdown text

    Returns:
        BlockType: The identified type of the markdown block (heading, paragraph,
                  code block, quote, ordered list, or unordered list)
    """
    # Check for code blocks first (they have ```at start and end)
    if block.startswith("```") and block.endswith("```"):
        return BlockType.code

    # Split into lines for multi-line checks
    lines = block.split("\n")

    # Check for headings (starts with # and has a space after the #s)
    if block.startswith("#"):
        heading_match = re.match(r"^#{1,6} ", block)
        if heading_match:
            return BlockType.heading

    # For quotes, check if ALL lines start with >
    if all(line.startswith(">") for line in lines):
        return BlockType.quote

    # Check for unordered lists
    if all(line.startswith("- ") for line in lines):
        return BlockType.unordered_list

    # Check for ordered lists
    is_ordered_list = True
    for i, line in enumerate(lines):
        expected_start = f"{i+1}. "
        if not line.startswith(expected_start):
            is_ordered_list = False
            break

    if is_ordered_list and lines:  # Ensure there's at least one line
        return BlockType.ordered_list

    return BlockType.paragraph


def markdown_to_blocks(markdown):
    blocks = []
    lines = markdown.split("\n")
    current_block = []
    in_code_block = False

    for line in lines:
        # Check for code block markers
        if line.strip().startswith("```"):
            if not in_code_block:
                # Starting a code block
                if current_block:
                    # Add the previous block
                    blocks.append("\n".join(current_block))
                    current_block = []
                in_code_block = True
                current_block = [line]  # Start with the code marker - don't strip!
            else:
                # Ending a code block
                current_block.append(line)  # Don't strip closing code marker
                blocks.append("\n".join(current_block))
                current_block = []
                in_code_block = False
        elif in_code_block:
            # Inside a code block, preserve the line exactly as is
            current_block.append(line)  # Don't strip inside code blocks
        else:
            # Normal markdown processing
            if line.strip() == "":
                # Empty line marks end of block
                if current_block:
                    blocks.append("\n".join(current_block))
                    current_block = []
            else:
                # Add line to current block, still strip for normal text
                current_block.append(line.strip())

    # Don't forget the last block if there is one
    if current_block:
        blocks.append("\n".join(current_block))

    # Filter out empty blocks
    return [block for block in blocks if block.strip()]
