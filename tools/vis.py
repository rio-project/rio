import json
from typing import *  # type: ignore

from revel import *  # type: ignore

import rio.debug.crawl_tree as ct

root_component: ct.Component
tree: ct.TreeDump


class UserError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

    @property
    def message(self) -> str:
        return self.args[0]


def get_component_by_id(id: int) -> ct.Component:
    for component in tree.components:
        if component.id == id:
            return component

    raise KeyError(id)


def parse_path(cur_path: ct.Component, path: str) -> Tuple[ct.Component, Optional[str]]:
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
                warning(f"Component #{cur_path.id} has no parent. Staying put.")
            else:
                try:
                    cur_component = get_component_by_id(cur_path.parent)
                except KeyError:
                    raise UserError(f"There is no component #{cur_path.parent}")

            continue

            #

            cur_path = cur_path.parent
            continue


def visualize_node(path: List[str], tree: ct.TreeDump) -> None:
    pass


def main():
    global tree, root_component

    # Load the tree
    with ct.DUMP_PATH.open("r") as f:
        tree = ct.TreeDump.from_json(
            json.load(f),
        )

    # Find the root component
    root: Optional[ct.Component] = None

    for component in tree.components:
        if component.parent is None:
            assert root is None, (component, root)
            root = component

    assert root is not None, "No root component found"
    root_component = root

    # Initialize state
    cur_component = root

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
