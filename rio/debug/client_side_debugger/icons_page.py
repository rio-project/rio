import dataclasses
import functools
import re
from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio
import rio.icon_registry

ITEMS_PER_ROW = 4

# Replace all sequences non-alphanumeric characters with a single dot
NORMALIZATION_PATTERN = re.compile(r"[^a-zA-Z0-9]+")

# Cache for all icons known to Rio. Finding the icons requires file system
# access and is slow - this caches them.
#
# The entires are (icon_set, icon_name, {variant_name}) tuples. The variant name
# is a set of all variants that exist for this icon.
ALL_AVAILABLE_ICONS: Optional[List[Tuple[str, str, Tuple[Optional[str], ...]]]] = None


ICON_BUTTON_BOX_STYLE = rio.BoxStyle(
    fill=rio.Color.TRANSPARENT,
    corner_radius=9999,
)


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
                variants = set()
                result_dict[key] = (icon_set, icon_name, variants)
            else:
                variants.add(variant_name)

    # Drop the dict
    as_list = list(result_dict.values())

    # Sort the result
    as_list.sort(key=lambda x: x[1])

    for _, _, variants in as_list:
        variants = sorted(variants, key=lambda x: "" if x is None else x)

    # Cache and return
    ALL_AVAILABLE_ICONS = as_list  # type: ignore
    return ALL_AVAILABLE_ICONS  # type: ignore


class IconButton(rio.Component):
    icon: str
    label: str
    _: KW_ONLY
    is_selected: bool = False
    on_press: rio.EventHandler[[]] = None

    async def _on_press(self, _: rio.MouseUpEvent) -> None:
        await self.call_event_handler(self.on_press)

    def build(self) -> rio.Component:
        if self.is_selected:
            text_style = self.session.theme.text_style.replace(
                fill=self.session.theme.secondary_color
            )
        else:
            text_style = "text"

        return rio.MouseEventListener(
            rio.Rectangle(
                child=rio.Column(
                    rio.Icon(
                        self.icon,
                        width=2,
                        height=2,
                        fill="secondary" if self.is_selected else "keep",
                    ),
                    rio.Text(
                        self.label,
                        style=text_style,
                    ),
                    spacing=0.3,
                    align_x=0.5,
                    align_y=0.5,
                ),
                style=ICON_BUTTON_BOX_STYLE,
                ripple=True,
                width=5,
                height=5,
                align_x=0.5,
                align_y=0.5,
            ),
            on_mouse_up=self._on_press,
        )


class IconsPage(rio.Component):
    _: KW_ONLY
    search_text: str = ""
    matches: List[Tuple[str, str, Tuple[Optional[str], ...]]] = dataclasses.field(
        default_factory=list
    )

    selected_icon: Optional[str] = "material/archive"
    selected_icon_available_variants: Tuple[Optional[str], ...] = dataclasses.field(
        default_factory=lambda: (None, "fill")
    )
    selected_variant: Optional[str] = None
    selected_size: float = 1.5
    selected_fill: str = "keep"

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

        self.matches.extend(
            (
                ("material", "castle", (None, "fill")),
                ("material", "archive", (None, "fill")),
                ("material", "error", (None, "fill")),
            )
        )

    def _on_select_icon(
        self,
        icon_set: str,
        icon_name: str,
        available_variants: Tuple[Optional[str], ...],
    ) -> None:
        self.selected_icon = icon_set + "/" + icon_name
        self.selected_icon_available_variants = available_variants

    def _on_select_variant(self, variant: Optional[str]) -> None:
        self.selected_variant = variant

    def build_details(self) -> rio.Component:
        assert self.selected_icon is not None
        children = []

        # Which parameters should be passed?
        params_dict = {}

        size = str(round(self.selected_size, 1))
        if size != "1.2":
            params_dict["width"] = size
            params_dict["height"] = size

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
        children.append(rio.Text("Code Sample", style="heading3", align_x=0))
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

        # Alow for easy configuration
        children.append(rio.Text("Configure", style="heading3", align_x=0))

        # If there is variations of this icon allow the user to select one
        if self.selected_icon_available_variants:
            variant_buttons = []

            for variant in self.selected_icon_available_variants:
                full_name = (
                    f"{self.selected_icon}:{variant}" if variant else self.selected_icon
                )

                variant_buttons.append(
                    IconButton(
                        full_name,
                        label="default" if variant is None else variant,
                        width="grow",
                        is_selected=variant == self.selected_variant,
                        on_press=functools.partial(self._on_select_variant, variant),
                    )
                )

            children.append(rio.Row(*variant_buttons, width="grow"))

        # Size slider
        children.append(
            rio.Slider(
                minimum=0.5,
                maximum=3,
                # value=IconsPage.selected_size,
            )
        )

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
                    "default",
                    "dim",
                ],
                selected_value=IconsPage.selected_fill,
            )
        )

        # Combine everything
        return rio.Column(*children, spacing=0.5)

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

            for ii, (icon_set, icon_name, icon_variants) in enumerate(
                self.matches[:30]
            ):
                results.append(
                    # rio.Text(icon_name),
                    IconButton(
                        icon_name,
                        label=icon_name.split("/")[-1],
                        # width="grow",
                        is_selected=icon_name == self.selected_icon,
                        on_press=functools.partial(
                            self._on_select_icon, icon_set, icon_name, icon_variants
                        ),
                    )
                )

            children.append(rio.FlowContainer(*results))
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
        )
