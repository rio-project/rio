import json
from typing import *  # type: ignore

from stream_tui import *  # type: ignore

import reflex.debug.crawl_tree as ct

root_widget: ct.Widget
tree: ct.TreeDump


class UserError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

    @property
    def message(self) -> str:
        return self.args[0]


def get_widget_by_id(id: int) -> ct.Widget:
    for widget in tree.widgets:
        if widget.id == id:
            return widget

    raise KeyError(id)


def parse_path(cur_path: ct.Widget, path: str) -> Tuple[ct.Widget, Optional[str]]:
    # Special case: Nothing
    if path == "":
        return cur_path, None

    # Split the path
    segments = path.split(".")

    # Process all segments
    while segments:
        cur = segments.pop(0)

        # Special case: Parent
        if cur == "parent":
            if cur_path.parent is None:
                warning(f"Widget #{cur_path.id} has no parent. Staying put.")
            else:
                try:
                    cur_widget = get_widget_by_id(cur_path.parent)
                except KeyError:
                    raise UserError(f"There is no widget #{cur_path.parent}")

            continue

            #

            cur_path = cur_path.parent
            continue


def visualize_node(path: List[str], tree: ct.TreeDump) -> None:
    pass


def main():
    global tree, root_widget

    # Load the tree
    with ct.DUMP_PATH.open("r") as f:
        tree = ct.TreeDump.from_json(
            json.load(f),
        )

    # Find the root widget
    root: Optional[ct.Widget] = None

    for widget in tree.widgets:
        if widget.parent is None:
            assert root is None, (widget, root)
            root = widget

    assert root is not None, "No root widget found"
    root_widget = root

    # Initialize state
    cur_widget = root

    # REPL
    while True:
        # Get a path to visualize
        path: str = input(
            "vis",
            sep=" > ",
            parse=str,
        )  # type: ignore

        # Visualize the node
        visualize_node(path.split("."), tree)
