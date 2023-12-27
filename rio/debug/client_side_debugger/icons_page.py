import dataclasses
import functools
import re
from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio
import rio.icon_registry

ITEMS_PER_ROW = 5

# Replace all sequences non-alphanumeric characters with a single dot
NORMALIZATION_PATTERN = re.compile(r"[^a-zA-Z0-9]+")

# Cache for all icons known to Rio. Finding the icons requires file system
# access and is slow - this caches them.
#
# The entires are (icon_set, icon_name, {variant_name}) tuples. The variant name
# is a set of all variants that exist for this icon.
ALL_AVAILABLE_ICONS: Optional[List[Tuple[str, str, Tuple[Optional[str], ...]]]] = None


def normalize_for_search(text: str) -> str:
    """
    Normalize a string for search, making search more forgiving.
    """
    text = NORMALIZATION_PATTERN.sub(".", text)
    text = text.strip(".")
    text = text.lower()
    return text


def get_available_icons() -> List[Tuple[str, str, Tuple[Optional[str], ...]]]:
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
                variants = {variant_name}
                result_dict[key] = (icon_set, icon_name, variants)
            else:
                variants.add(variant_name)

    # Drop the dict
    as_list: List[Any] = list(result_dict.values())

    # Sort the result
    as_list.sort(key=lambda x: x[1])

    for ii, (icon_set, icon_name, variants) in enumerate(as_list):
        variants = tuple(sorted(variants, key=lambda x: "" if x is None else x))
        as_list[ii] = (icon_set, icon_name, variants)

    # Cache and return
    ALL_AVAILABLE_ICONS = as_list  # type: ignore
    return ALL_AVAILABLE_ICONS  # type: ignore


class IconsPage(rio.Component):
    _: KW_ONLY
    search_text: str = ""
    matches: List[Tuple[str, str, Tuple[Optional[str], ...]]] = dataclasses.field(
        default_factory=list
    )

    selected_icon: Optional[str] = None
    selected_icon_available_variants: Tuple[Optional[str], ...] = dataclasses.field(
        default_factory=tuple
    )
    selected_variant: Optional[str] = None
    selected_fill: Literal[
        "primary",
        "secondary",
        "success",
        "warning",
        "danger",
        "keep",
        "dim",
    ] = "keep"

    def _on_search_text_change(self, _: rio.TextInputChangeEvent) -> None:
        # No search -> no matches
        self.matches = []
        normalized_search_text = self.search_text.strip()

        if not normalized_search_text:
            return

        # TODO: Add a proper search
        normalized_search_text = normalize_for_search(normalized_search_text)

        for icon_set, icon_name, variants in get_available_icons():
            if normalized_search_text not in normalize_for_search(icon_name):
                continue

            self.matches.append((icon_set, icon_name, variants))

    def _on_select_icon(
        self,
        icon_set: str,
        icon_name: str,
        available_variants: Tuple[Optional[str], ...],
    ) -> None:
        self.selected_icon = icon_set + "/" + icon_name
        self.selected_variant = available_variants[0]
        self.selected_icon_available_variants = available_variants

    def _on_select_variant(self, variant: Optional[str]) -> None:
        self.selected_variant = variant

    def build_details(self) -> rio.Component:
        assert self.selected_icon is not None
        children = []

        # Heading
        children.append(rio.Text("Configure", style="heading3", align_x=0))

        # Fill
        children.append(
            rio.Dropdown(
                label="Fill",
                options=[
                    "primary",
                    "secondary",
                    "success",
                    "warning",
                    "danger",
                    "keep",
                    "dim",
                ],
                selected_value=IconsPage.selected_fill,
            )
        )

        # If there is variations of this icon allow the user to select one
        # if len(self.selected_icon_available_variants) > 1:
        if True:
            variant_buttons = []

            for variant in self.selected_icon_available_variants:
                full_name = (
                    f"{self.selected_icon}:{variant}" if variant else self.selected_icon
                )

                variant_buttons.append(
                    rio.Container(
                        rio.IconButton(
                            full_name,
                            style="minor"
                            if variant == self.selected_variant
                            else "plain",
                            on_press=functools.partial(
                                self._on_select_variant, variant
                            ),
                        ),
                        width="grow",
                        align_y=0.5,
                    )
                )

            children.append(rio.Row(*variant_buttons, width="grow"))

        # Which parameters should be passed?
        params_dict = {
            "width": "2.5",
            "height": "2.5",
        }

        if self.selected_fill != "keep":
            params_dict["fill"] = repr(self.selected_fill)

        # Prepare the source code
        selected_icon_full_name = self.selected_icon + (
            "" if self.selected_variant is None else ":" + self.selected_variant
        )

        params_list = [repr(selected_icon_full_name)] + [
            f"{key}={value}" for key, value in params_dict.items()
        ]

        params_str = ",\n    ".join(params_list)
        python_source = f"rio.Icon(\n    {params_str},\n)"

        # Code sample
        children.append(
            rio.Text(
                "Example Code",
                style="heading3",
                align_x=0,
                margin_top=1,
            )
        )

        children.append(
            rio.MarkdownView(
                f"""
Use the `rio.Icon` component like this:

```python
{python_source}
```
"""
            )
        )

        # Combine everything
        return rio.Column(*children, spacing=0.8)

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
            results = []

            for icon_set, icon_name, icon_variants in self.matches[:50]:
                is_selected = self.selected_icon == f"{icon_set}/{icon_name}"

                results.append(
                    rio.IconButton(
                        icon_name,
                        style="minor" if is_selected else "plain",
                        on_press=functools.partial(
                            self._on_select_icon, icon_set, icon_name, icon_variants
                        ),
                        key=f"{icon_set}/{icon_name}",
                    ),
                )

            children.append(rio.FlowContainer(*results, height="grow"))

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

        # Absorb additional space
        children.append(rio.Spacer())

        # If an icon is selected, show its details
        if self.selected_icon is not None:
            children.append(self.build_details())

        # Combine everything
        return rio.Column(
            *children,
            spacing=1,
            margin=1,
            width=30,  # Just for testing the switcher
        )
