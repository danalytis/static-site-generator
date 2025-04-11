import re
from enum import Enum
from htmlnode import LeafNode


def extract_markdown_images(text):
    results = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return results


def extract_markdown_links(text):
    results = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return results


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


def text_to_textnodes(text):
    """
    Converts raw markdown string to a list of TextNode objects
    """
    # Start with a list containing a single TextNode
    nodes = [TextNode(text, TextType.TEXT)]

    # Now apply each splitting function
    nodes = split_nodes_image(nodes)
    # print(
    #     "After image processing:",
    #     [(node.text, node.text_type, node.url) for node in nodes],
    # )
    nodes = split_nodes_link(nodes)
    # print(
    #     "After link processing:",
    #     [(node.text, node.text_type, node.url) for node in nodes],
    # )
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)

    return nodes


def split_nodes_image(old_nodes):
    """
    Split TextNode image link into its subcomponents.

    old_nodes -- List of TextNode objects to process
    """
    result = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            result.append(old_node)
            continue

        images = extract_markdown_images(old_node.text)
        # print(f"Extracted images: {images}")  # debug

        if not images:
            result.append(old_node)
            continue

        remaining_text = old_node.text

        for image_alt, image_url in images:
            image_markdown = f"![{image_alt}]({image_url})"
            parts = remaining_text.split(image_markdown, 1)

            if parts[0]:
                result.append(TextNode(parts[0], TextType.TEXT))

            # result.append(TextNode(image_alt, TextType.IMAGE, image_url))
            node = TextNode(image_alt, TextType.IMAGE, image_url)
            # print(f"Created image node: {node.text}, {node.text_type}, URL={node.url}")
            result.append(node)

            if len(parts) > 1:
                remaining_text = parts[1]
            else:
                remaining_text = ""

        if remaining_text:
            result.append(TextNode(remaining_text, TextType.TEXT))

    return result


def split_nodes_link(old_nodes):
    """
    Split TextNode link into its subcomponents.

    old_nodes -- List of TextNode objects to process.
    """
    result = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            result.append(old_node)
            continue

        links = extract_markdown_links(old_node.text)

        if not links:
            result.append(old_node)
            continue

        remaining_text = old_node.text

        for link_alt, link_url in links:
            link_markdown = f"[{link_alt}]({link_url})"
            parts = remaining_text.split(link_markdown, 1)

            if parts[0]:
                result.append(TextNode(parts[0], TextType.TEXT))
            result.append(TextNode(link_alt, TextType.LINK, link_url))

            if len(parts) > 1:
                remaining_text = parts[1]
            else:
                remaining_text = ""
        if remaining_text:
            result.append(TextNode(remaining_text, TextType.TEXT))
    return result


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Split TextNodes by a specified delimiter and assign the appropriate text type.

    old_nodes -- List of TextNode objects to process
    delimiter -- The delimiter string to split on (e.g., "`", "**", "_")
    text_type -- The TextType to assign to text between delimiters

    Returns a new list of TextNode objects with appropriate text types.
    Raises an exception if a matching closing delimiter
    """
    new_nodes = []

    for node in old_nodes:
        parts = node.text.split(delimiter)

        if len(parts) % 2 == 0:
            raise Exception("Unmatched delimiter found.")

        for i, part in enumerate(parts):
            if part:  # Avoid adding empty strings
                if i % 2 == 0:
                    new_nodes.append(
                        TextNode(part, node.text_type, node.url)
                    )  # Normal text
                else:
                    new_nodes.append(
                        TextNode(part, text_type, node.url)
                    )  # Delimited text

    return new_nodes


def text_node_to_html_node(text_node):
    """TODO describe function
    :param text_node:
    :returns:

    """
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            # print(f"Text content received in TextNode: {repr(text_node.text)}")
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
        case _:
            raise ValueError(f"Invalid TextType: {text_node.text_type}")


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return False
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type}, {self.url})"
