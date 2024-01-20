import inspect
from typing import *  # type: ignore

import rio

from . import article_models, articles

__all__ = [
    "DOCUMENTATION_STRUCTURE",
]


ArticleType: TypeAlias = Union[
    tuple[str, str, Callable[[], article_models.BuiltArticle]], Type
]
SectionType: TypeAlias = (
    tuple[str, str, tuple[article_models.ArticleBuilder, ...]] | None
)


# This acts as the source for anything that needs to know about the structure of
# the documentation. Other variables expose related information, but those
# variables derive from this one.
DOCUMENTATION_STRUCTURE: tuple[SectionType, ...] = (
    # Introduction & How-To Guides
    (
        "Introduction",
        "tutorial-biography",
        (
            articles.tutorial_biography.tutorial_1_rio_setup.Builder(),
            articles.tutorial_biography.tutorial_2_application_overview.Builder(),
            articles.tutorial_biography.tutorial_3_app_setup.Builder(),
            articles.tutorial_biography.tutorial_4_first_components.Builder(),
            articles.tutorial_biography.tutorial_5_more_components.Builder(),
        ),
    ),
    (
        "How-To Guides",
        "how-to",
        (
            articles.howto.howto_app.Builder(),
            articles.howto.howto_events.Builder(),
            articles.howto.howto_multiple_pages.Builder(),
            articles.howto.howto_passing_values.Builder(),
            articles.howto.howto_theming.Builder(),
            articles.howto.howto_website.Builder(),
        ),
    ),
    None,
    # API Docs
    # (
    #     "Inputs",
    #     (
    #         rio.Button,
    #         rio.ColorPicker,
    #         rio.CustomButton,
    #         rio.Dropdown,
    #         rio.Icon,
    #         rio.Image,
    #         rio.KeyEventListener,
    #         rio.MouseEventListener,
    #         rio.NumberInput,
    #         rio.Slider,
    #         rio.Switch,
    #         rio.TextInput,
    #     ),
    # ),
    # (
    #     "Displays",
    #     (
    #         rio.Html,
    #         rio.Link,
    #         rio.MarkdownView,
    #         rio.MediaPlayer,
    #         rio.Banner,
    #         rio.Plot,
    #         rio.ProgressBar,
    #         rio.ProgressCircle,
    #         rio.Rectangle,
    #         rio.Slideshow,
    #         rio.Text,
    #     ),
    # ),
    # (
    #     "Layout",
    #     (
    #         rio.Card,
    #         rio.Column,
    #         rio.Container,
    #         rio.Drawer,
    #         rio.Grid,
    #         rio.Popup,
    #         rio.Revealer,
    #         rio.Row,
    #         rio.ScrollContainer,
    #         rio.Spacer,
    #         rio.Stack,
    #         rio.Overlay,
    #     ),
    # ),
    # (
    #     "Other",
    #     (
    #         rio.Component,
    #         rio.PageView,
    #         rio.ScrollTarget,
    #     ),
    # ),
    # (
    #     "Non-Components",
    #     (
    #         rio.App,
    #         rio.AssetError,
    #         rio.BoxStyle,
    #         rio.Color,
    #         rio.CursorStyle,
    #         rio.FileInfo,
    #         rio.Fill,
    #         rio.Font,
    #         rio.ImageFill,
    #         rio.LinearGradientFill,
    #         rio.NavigationFailed,
    #         rio.Page,
    #         rio.Session,
    #         rio.SolidFill,
    #         rio.TextStyle,
    #         rio.Theme,
    #         rio.URL,
    #         rio.UserSettings,
    #     ),
    # ),
    # (
    #     "Events",
    #     (
    #         rio.ColorChangeEvent,
    #         rio.DrawerOpenOrCloseEvent,
    #         rio.DropdownChangeEvent,
    #         rio.KeyDownEvent,
    #         rio.KeyPressEvent,
    #         rio.KeyUpEvent,
    #         rio.MouseDownEvent,
    #         rio.MouseEnterEvent,
    #         rio.MouseLeaveEvent,
    #         rio.MouseMoveEvent,
    #         rio.MouseUpEvent,
    #         rio.NumberInputChangeEvent,
    #         rio.NumberInputConfirmEvent,
    #         rio.PopupOpenOrCloseEvent,
    #         rio.RevealerChangeEvent,
    #         rio.TextInputChangeEvent,
    #         rio.TextInputConfirmEvent,
    #     ),
    # ),
)


# Flattened view of `DOCUMENTATION_STRUCTURE`. This is a sequence of tuples:
#
# - Section Name
# - section URL segment
# - `ArticleBuilder`
def _compute_linear() -> (
    tuple[
        tuple[
            str,
            str,
            Type[article_models.ArticleBuilder],
        ],
        ...,
    ]
):
    result = []

    for section in DOCUMENTATION_STRUCTURE:
        # `None` is used to represent whitespace
        if section is None:
            continue

        # Otherwise, it's a tuple
        section_title, section_url, builders = section

        for builder in builders:
            result.append((section_title, section_url, builder))

    return tuple(result)


DOCUMENTATION_STRUCTURE_LINEAR = _compute_linear()
