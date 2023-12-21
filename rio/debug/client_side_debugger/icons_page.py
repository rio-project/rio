import dataclasses
from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio
import rio.icon_registry

ITEMS_PER_ROW = 4


# Cache for all icons known to Rio. Finding the icons requires file system
# access and is slow - this caches them.
#
# The entires are (icon_set, icon_name, {variant_name}) tuples. The variant name
# is a set of all variants that exist for this icon.
ALL_AVAILABLE_ICONS: Optional[List[Tuple[str, str, Set[Optional[str]]]]] = None


def get_available_icons() -> List[Tuple[str, str, Set[Optional[str]]]]:
    """
    Return a list of all available icons. The result is caches, so subsequent
    calls are fast.
    """
    global ALL_AVAILABLE_ICONS

    # Cached?
    if ALL_AVAILABLE_ICONS is not None:
        return ALL_AVAILABLE_ICONS

    # Nope, get to work. Iterate over all icons and variants and group them.
    registry = rio.icon_registry.IconRegistry.get_singleton()
    result_dict: Dict[str, Tuple[str, str, Set[Optional[str]]]] = {}

    for icon_set in registry.all_icon_sets():
        for icon_name, variant_name in registry.all_icons_in_set(icon_set):
            key = f"{icon_set}/{icon_name}"

            try:
                _, _, variants = result_dict[key]
            except KeyError:
                variants = set()
                result_dict[key] = (icon_set, icon_name, variants)
            else:
                variants.add(variant_name)

    # Drop the dict
    ALL_AVAILABLE_ICONS = list(result_dict.values())
    return ALL_AVAILABLE_ICONS


class IconsPage(rio.Component):
    _: KW_ONLY
    search_text: str = ""
    matches: List[str] = dataclasses.field(default_factory=list)

    selected_icon: Optional[str] = "archive"
    selected_size: float = 1.5
    selected_fill: str = "primary"

    def _on_search_text_change(self, _: rio.TextInputChangeEvent) -> None:
        # No search -> no matches
        self.matches = []
        if not self.search_text:
            return

        # TODO: Add a proper search
        for icon_set, icon_name, variants in get_available_icons():
            if self.search_text.lower() not in icon_name.lower():
                continue

            full_name = f"{icon_set}/{icon_name}"
            self.matches.append(full_name)

        self.matches.extend(("castle", "archive", "error"))

    def build_details(self) -> rio.Component:
        assert self.selected_icon is not None

        # Which parameters should be passed?
        params_dict = {}

        size = str(round(self.selected_size, 1))
        if size != "1.2":
            params_dict["width"] = size
            params_dict["height"] = size

        if self.selected_fill != "text":
            params_dict["fill"] = repr(self.selected_fill)

        # Prepare the source code
        params_list = [self.selected_icon] + [
            f"{key}={value}" for key, value in params_dict.items()
        ]

        if len(params_list) <= 2:
            python_source = f"rio.Icon({', '.join(params_list[0])})"
        else:
            params_str = ",\n    ".join(params_list[1:])
            python_source = f"rio.Icon(\n    {params_list[0]},\n    {params_str}\n)"

        # Combine everything
        return rio.Column(
            rio.Text("Code Sample", style="heading3"),
            rio.MarkdownView(
                f"""
To use this icon in your app, use the `rio.Icon` component:

```python
{python_source}
```
"""
            ),
            rio.Revealer(
                header="Fooo",
                content=rio.Text("Bar"),
                header_style="heading2",
            ),
            rio.Slider(
                minimum=0.5,
                maximum=3,
                # value=IconsPage.selected_size,
            ),
            rio.Dropdown(
                label="Fill",
                options=[
                    "primary",
                    "secondary",
                    "success",
                    "warning",
                    "danger",
                    "default",
                    "dim",
                ],
                selected_value=IconsPage.selected_fill,
            ),
        )

    def build(self) -> rio.Component:
        # Search field
        children: List[rio.Component] = [
            rio.TextInput(
                label="Search for an icon",
                text=IconsPage.search_text,
                on_change=self._on_search_text_change,
            ),
        ]

        # Display the top results in a grid
        if not self.search_text:
            children.append(
                rio.Text(
                    "Rio comes with a large array of icons out of the box. You can find them all here.",
                    multiline=True,
                    align_y=0.5,
                )
            )
        elif self.matches:
            results_grid = rio.Grid(row_spacing=0.5, column_spacing=0.5)
            children.append(results_grid)

            for ii, icon_name in enumerate(self.matches[:30]):
                results_grid.add_child(
                    rio.Icon(icon_name, width=2, height=2),
                    row=ii // ITEMS_PER_ROW,
                    column=ii % ITEMS_PER_ROW,
                )

            results_grid.add_child(rio.Text("foo"), 1, 1)

            children.append(rio.Spacer())
        else:
            children.append(
                rio.Container(
                    rio.Column(
                        rio.Icon(
                            "search",
                            width=4,
                            height=4,
                            fill="dim",
                            align_x=0.5,
                        ),
                        rio.Text(
                            "No results",
                            style="dim",
                        ),
                        spacing=1,
                        align_y=0.5,
                    ),
                    height="grow",
                )
            )

        # If an icon is selected, show its details
        if self.selected_icon is not None:
            children.append(self.build_details())

        # Combine everything
        return rio.Column(
            *children,
            rio.Spacer(),
            spacing=1,
            margin=1,
        )
