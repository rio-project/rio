from __future__ import annotations

import enum
from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

from .. import inspection
from . import banner, component_base, number_input, switch, text

__all__ = ["AutoForm"]


def prettify_name(name: str) -> str:
    parts = name.split("_")
    return " ".join(p.title() for p in parts)


class AutoForm(component_base.Component):
    # Not yet ready for release - do not use.

    _: KW_ONLY
    spacing: float = 0.5
    label_width: float = 15.0
    error_message: Optional[str] = None
    submit_text: str = "Submit"

    # Internal
    _is_loading: bool = False

    def validate(self) -> Optional[str]:
        """
        Override this method to validate the form's values. If a string is
        returned it will be displayed to the user, and the form will not be
        submittable.
        """
        return None

    async def on_submit(self) -> None:
        """
        Called when the user clicks the submit button. Override this method to
        perform some action when the form is submitted.
        """
        pass

    async def _on_submit(self) -> None:
        # Display the loading indicator
        self._is_loading = True
        await self.force_refresh()

        # Delegate to the user's submit method
        try:
            await self.call_event_handler(self.on_submit)
        finally:
            self._is_loading = False

    def make_notification_bar(
        self,
        text: str,
        level: Literal["info", "warning", "error"],
    ) -> rio.Component:
        return banner.Banner(
            text=text,
            style=level,
        )

    def make_switch(self, is_on: bool) -> rio.Component:
        return switch.Switch(is_on=is_on)

    def make_button(
        self,
        *,
        text: str,
        on_press: rio.EventHandler[[]],
        is_sensitive: bool,
        is_loading: bool,
        is_major: bool,
    ) -> rio.Component:
        return rio.Button(
            text_or_child == text,
            style="major" if is_major else "minor",
            on_press=on_press,
            is_sensitive=is_sensitive,
            is_loading=is_loading,
        )

    def _build_input_field(
        self,
        field_name: str,
        field_type: type,
    ) -> rio.Component:
        # Get sensible type information
        origin = get_origin(field_type)
        field_args = get_args(field_type)
        field_type = field_type if origin is None else origin
        del origin

        # Grab the field instance
        field_instance = vars(type(self))[field_name]

        # `bool` -> `Switch`
        if field_type is bool:
            return self.make_switch(
                is_on=field_instance,
            )

        # `int` -> `NumberInput`
        if field_type is int:
            return number_input.NumberInput(
                value=field_instance,
                decimals=0,
            )

        # `float` -> `NumberInput`
        if field_type is float:
            return number_input.NumberInput(
                value=field_instance,
            )

        # `str` -> `TextInput`
        if field_type is str:
            return rio.TextInput(
                text=field_instance,
            )

        # `Literal` or `Enum` -> `Dropdown`
        if field_type is Literal or issubclass(field_type, enum.Enum):
            if field_type is Literal:
                mapping = {str(a): a for a in field_args}
            else:
                mapping = {prettify_name(f.name): f.value for f in field_type}

            return rio.Dropdown(
                mapping,
                selected_value=field_instance,
            )

        # Unsupported type
        raise TypeError(f"AutoForm does not support fields of type `{field_type}`")

    def build(self) -> rio.Component:
        rows: List[rio.Component] = []

        # Look for errors
        error_message = (
            self.validate() if self.error_message is None else self.error_message
        )

        # Display any errors
        if error_message is not None:
            rows.append(
                self.make_notification_bar(
                    text=error_message,
                    level="error",
                )
            )

        # One row per field
        for field_name, field_type in inspection.get_type_annotations(
            type(self)
        ).items():
            rows.append(
                rio.Row(
                    text.Text(
                        prettify_name(field_name),
                        width=self.label_width,
                    ),
                    self._build_input_field(field_name, field_type),
                    spacing=self.spacing,
                )
            )

        # Add a submit button
        rows.append(
            self.make_button(
                text=self.submit_text,
                on_press=self._on_submit,
                is_sensitive=not self._is_loading and error_message is None,
                is_loading=self._is_loading,
                is_major=True,
            )
        )

        # Wrap everything in one container
        return rio.Column(
            *rows,
            spacing=self.spacing,
        )
