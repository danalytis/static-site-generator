import os
import shutil
from markdown import markdown_to_html_node
from textnode import TextNode


def extract_title(markdown):
    """Pulls h1 header from markdown file and returns it.
    strips # and removes any leading/trailing whitespace.
    If there is no h1 header raises an exception.
    """
    lines = markdown.strip().splitlines()
    title = None
    for line in lines:
        if line.startswith("# "):
            title = line.lstrip("#").strip()
            return title
    raise Exception("no h1 title found")


def generate_page(from_path, template_path, dest_path):
    """ """

    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path) as md_fd:
        md = md_fd.read()
    with open(template_path) as template_fd:
        template = template_fd.read()

    content = markdown_to_html_node(md).to_html()
    title = extract_title(md)

    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", content)

    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(dest_path, "w") as output_fd:
        output_fd.write(template)


def copytree(source, destination):
    """recursive function that copies all contents from source directory to destination"""

    if os.path.exists(destination):
        shutil.rmtree(destination)

    os.makedirs(destination)

    for item in os.listdir(source):
        source_item = os.path.join(source, item)
        destination_item = os.path.join(destination, item)

        if os.path.isfile(source_item):
            print(f"Copying file: {source_item} to {destination_item}")
            shutil.copy2(source_item, destination_item)
        else:
            copytree(source_item, destination_item)


def main():
    # paths
    current_dir = os.getcwd()
    public_dir = os.path.join(current_dir, "public")
    static_dir = os.path.join(current_dir, "static")
    content_dir = os.path.join(current_dir, "content")
    content_path = os.path.join(current_dir, "content/index.md")
    template_path = os.path.join(current_dir, "template.html")
    dest_path = os.path.join(public_dir, "index.html")

    if os.path.exists(public_dir):
        shutil.rmtree(public_dir)
    os.makedirs(public_dir)

    copytree(static_dir, public_dir)
    for root, dirs, files in os.walk(content_dir):
        for file in files:
            if file.endswith(".md"):
                # Get the content file path
                content_path = os.path.join(root, file)

                # Calculate the relative path from content_dir
                rel_path = os.path.relpath(content_path, content_dir)

                # Calculate the destination path in public
                # Replace .md with .html and maintain directory structure
                if file == "index.md":
                    # For index.md files, keep the name as index.html
                    rel_html_path = os.path.join(
                        os.path.dirname(rel_path), "index.html"
                    )
                else:
                    # For other md files, change extension to html
                    rel_html_path = rel_path.replace(".md", ".html")

                dest_path = os.path.join(public_dir, rel_html_path)

                # Ensure the destination directory exists
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                # Generate the HTML page
                generate_page(content_path, template_path, dest_path)


if __name__ == "__main__":
    main()
