import os
import shutil
from textnode import TextNode


def copytree(source, destination=None):
    """recursive function that copies all contents from source directory to destination"""

    current_path = os.getcwd()

    public_path = os.path.join(current_path, "public")

    if os.path.exists(public_path):
        shutil.rmtree(public_path)

    os.mkdir(public_path)

    if destination is None:
        public_path = os.path.join(current_path, "public")

        if os.path.exists(public_path):
            shutil.rmtree(public_path)

        os.mkdir(public_path)
        destination = public_path

    for item in os.listdir(source):
        source_item = os.path.join(source, item)
        destination_item = os.path.join(destination, item)
        if not os.path.exists(destination_item):
            os.makedirs(destination_item)
        if os.path.isfile(source_item):
            print(f"Copying file: {source_item} to {destination_item}")
            shutil.copy(source_item, destination_item)
        else:
            if not os.path.exists(destination_item):
                os.mkdir(destination_item)
            copytree(source_item, destination_item)


def main():
    new_textnode = TextNode("im a textnode", "bold")
    print(new_textnode)
    static_path = os.path.join(os.getcwd(), "static")
    copytree(static_path)


if __name__ == "__main__":
    main()
