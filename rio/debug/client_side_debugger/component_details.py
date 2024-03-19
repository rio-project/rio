from pathlib import Path
from typing import *  # type: ignore

import rio


class ComponentDetails(rio.Component):
    component_id: int

    def _get_component_details(self, target: rio.Component) -> Dict[str, Any]:
        """
        Given a component, return a set of keys/values of all the details which
        should be displayed to the user.
        """
        # Some components have a custom function which determines what to
        # display
        #
        # TODO: I don't believe any of these actually exist just yet
        try:
            return target._get_debug_details()  # type: ignore
        except AttributeError:
            pass

        # Otherwise fall back to using the state properties
        result = {}

        for prop in target._state_properties_:
            # Explicitly excluded properties
            if prop in (
                "align_x",
                "align_y",
                "height",
                "key",
                "margin_bottom",
                "margin_left",
                "margin_right",
                "margin_top",
                "margin_x",
                "margin_y",
                "margin",
                "width",
            ):
                continue

            # Properties starting with an underscore are private
            if prop.startswith("_"):
                continue

            # Keep it
            result[prop] = getattr(target, prop)

        return result

    def build(self) -> rio.Component:
        # Get the target component. For now just use a placeholder
        target = self.session._weak_components_by_id[self.component_id]

        # Create a grid with all the details
        result = rio.Grid(row_spacing=0.5, column_spacing=0.5)
        row_index = 0

        def add_cell(
            text: str,
            column_index: int,
            is_label: bool,
            *,
            width: int = 1,
        ) -> None:
            result.add_child(
                rio.Text(
                    text,
                    style="dim" if is_label else "text",
                    align_x=1 if is_label else 0,
                ),
                row_index,
                column_index,
                width=width,
            )

        # Key, if any. These are displayed right in the title
        key_children = []

        if target.key is not None:
            key_children = [
                rio.Icon("key", fill="dim"),
                rio.Text(
                    target.key,
                    style="dim",
                    align_x=0,
                ),
            ]

        # Title
        result.add_child(
            rio.Row(
                rio.Text(
                    type(target).__qualname__,
                    style="heading3",
                ),
                rio.Spacer(),
                *key_children,
                margin_bottom=0.2,
                spacing=0.5,
            ),
            row_index,
            0,
            width=4,
        )
        row_index += 1

        # Which file/line was this component instantiated from?
        if target._creator_stackframe_ is not None:
            file, line = target._creator_stackframe_
            file = file.relative_to(Path.cwd())

            result.add_child(
                rio.Text(
                    f"{file} line {line}",
                    style="dim",
                    align_x=0,
                ),
                row_index,
                0,
                width=4,
            )
            row_index += 1

        # Custom properties
        #
        # Make sure to skip any which already have custom tailored cells
        for prop_name, prop_value in self._get_component_details(target).items():
            value_limit = 30
            prop_str = repr(prop_value)

            if len(prop_str) > value_limit:
                prop_str = prop_str[: value_limit - 1] + "…"

            add_cell(prop_name, 0, True)
            add_cell(prop_str, 1, False, width=3)
            row_index += 1

        # Size
        add_cell("width", 0, True)
        add_cell(repr(target.width), 1, False)

        add_cell("height", 2, True)
        add_cell(repr(target.height), 3, False)
        row_index += 1

        # Margins
        single_x_margin = target.margin_left == target.margin_right
        single_y_margin = target.margin_top == target.margin_bottom

        if single_x_margin and single_y_margin:
            add_cell("margin", 0, True)
            add_cell(str(target.margin_left), 1, False)
            row_index += 1

        else:
            if single_x_margin:
                add_cell("margin_x", 0, True)
                add_cell(str(target.margin_left), 1, False)

            else:
                add_cell("margin_left", 0, True)
                add_cell(str(target.margin_left), 1, False)

                add_cell("margin_right", 2, True)
                add_cell(str(target.margin_right), 3, False)

            row_index += 1

            if single_y_margin:
                add_cell("margin_y", 0, True)
                add_cell(str(target.margin_top), 1, False)

            else:
                add_cell("margin_top", 0, True)
                add_cell(str(target.margin_top), 1, False)

                add_cell("margin_bottom", 2, True)
                add_cell(str(target.margin_bottom), 3, False)

            row_index += 1

        # # Alignment
        add_cell("align_x", 0, True)
        add_cell(str(target.align_x), 1, False)

        add_cell("align_y", 2, True)
        add_cell(str(target.align_y), 3, False)
        row_index += 1

        # Link to docs
        if type(target)._rio_builtin_:
            docs_url = f"https://rio.dev/docs/{type(target).__name__.lower()}"
            link_color = self.session.theme.secondary_color

            result.add_child(
                rio.Link(
                    rio.Row(
                        rio.Icon("library-books", fill=link_color),
                        rio.Text("Docs", style=rio.TextStyle(fill=link_color)),
                        spacing=0.5,
                        align_x=0,
                    ),
                    docs_url,
                    # TODO: Support icons in links
                    # new_tab=True,  # TODO: Support this
                    margin_top=0.2,
                ),
                row_index,
                0,
                width=2,
            )
            row_index += 1

        # Done
        return result
