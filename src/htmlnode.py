class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children if children is not None else []
        self.props = props if props else {}

    def to_html(self):
        # Determine the opening tag, including attributes (props)
        if self.tag:
            # Add props to opening tag if they exist
            props = " ".join(
                f'{key}="{value}"' for key, value in (self.props or {}).items()
            )
            opening_tag = f"<{self.tag}" + (f" {props}" if props else "") + ">"
        else:
            opening_tag = ""

        # The content of the node (value or child nodes)
        value = self.value or ""
        children_html = "".join([child.to_html() for child in (self.children or [])])

        # Determine the closing tag
        closing_tag = f"</{self.tag}>" if self.tag else ""
        return f"{opening_tag}{value}{children_html}{closing_tag}"

    def props_to_html(self):
        results = ""
        if self.props:
            for key, value in self.props.items():
                results = results + f' {key}="{value}"'
        return results

    def __repr__(self):
        return f" {self.tag} : {self.value} , {self.children}, {self.props}"


class LeafNode(HTMLNode):
    def __init__(self, tag, value, attributes=None, children=None):
        super().__init__(tag, value, children, attributes)
        if value is None:
            raise ValueError
        self.attributes = attributes

    def to_html(self):
        if self.value is None:
            raise ValueError("LeafNode must have a value")
        if self.tag is None:
            return self.value

        attributes_str = ""
        if self.attributes:
            for key, value in self.attributes.items():
                attributes_str += f' {key}="{value}"'
        return f"<{self.tag}{attributes_str}>{self.value}</{self.tag}>"

    def text_node_to_html_node(self):
        pass


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self):
        if self.tag is None:
            raise ValueError("ParentNode must have a tag")
        if not hasattr(self, "children") or self.children is None:
            raise ValueError("ParentNode must have children")

        html = f"<{self.tag}"

        if self.props:
            for prop_name, prop_value in self.props.items():
                html += f' {prop_name}="{prop_value}"'

        html += ">"

        for child in self.children:
            html += child.to_html()

        html += f"</{self.tag}>"
        return html
