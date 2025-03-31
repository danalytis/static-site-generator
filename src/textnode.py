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
                    new_nodes.append(TextNode(part, node.text_type))  # Normal text
                else:
                    new_nodes.append(TextNode(part, text_type))  # Delimited text

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
