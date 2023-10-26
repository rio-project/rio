import inspect
from typing import *  # type: ignore

import rio

from . import article, articles

__all__ = [
    "DOCUMENTATION_STRUCTURE",
]


ArticleType: TypeAlias = Union[Tuple[str, str, Callable[[], article.Article]], Type]
SectionType: TypeAlias = Union[Tuple[str, Tuple[ArticleType, ...]], None]


# This acts as the source for anything that needs to know about the structure of
# the documentation. Other variables expose related information, but those
# variables derive from this one.
DOCUMENTATION_STRUCTURE: Tuple[SectionType, ...] = (
    # Introduction
    (
        "Getting Started",
        (
            (
                "Rio Setup",
                "tutorial-1-rio-setup",
                articles.tutorial_1_rio_setup.generate,
            ),
            (
                "Application Overview",
                "tutorial-2-application-overview",
                articles.tutorial_2_application_overview.generate,
            ),
            (
                "Setting-up your App",
                "tutorial-3-application-setup",
                articles.tutorial_3_app_setup.generate,
            ),
            (
                "First Components",
                "tutorial-4-first-components",
                articles.tutorial_4_first_components.generate,
            ),
        ),
    ),
    None,
    # API Docs
    (
        "Inputs",
        (
            rio.Button,
            rio.ColorPicker,
            rio.CustomButton,
            rio.Dropdown,
            rio.Icon,
            rio.Image,
            rio.KeyEventListener,
            rio.MouseEventListener,
            rio.NumberInput,
            rio.Slider,
            rio.Switch,
            rio.TextInput,
        ),
    ),
    (
        "Displays",
        (
            rio.Html,
            rio.Link,
            rio.MarkdownView,
            rio.MediaPlayer,
            rio.Banner,
            rio.Plot,
            rio.ProgressBar,
            rio.ProgressCircle,
            rio.Rectangle,
            rio.Slideshow,
            rio.Text,
        ),
    ),
    (
        "Layout",
        (
            rio.Card,
            rio.Column,
            rio.Container,
            rio.Drawer,
            rio.Grid,
            rio.Popup,
            rio.Revealer,
            rio.Row,
            rio.ScrollContainer,
            rio.Spacer,
            rio.Stack,
            rio.Overlay,
        ),
    ),
    (
        "Other",
        (
            rio.Component,
            rio.PageView,
            rio.ScrollTarget,
        ),
    ),
    (
        "Non-Components",
        (
            rio.App,
            rio.AssetError,
            rio.BoxStyle,
            rio.Color,
            rio.CursorStyle,
            rio.FileInfo,
            rio.Fill,
            rio.Font,
            rio.ImageFill,
            rio.LinearGradientFill,
            rio.NavigationFailed,
            rio.Page,
            rio.Session,
            rio.SolidFill,
            rio.TextStyle,
            rio.Theme,
            rio.URL,
            rio.UserSettings,
        ),
    ),
    (
        "Events",
        (
            rio.ColorChangeEvent,
            rio.DrawerOpenOrCloseEvent,
            rio.DropdownChangeEvent,
            rio.KeyDownEvent,
            rio.KeyPressEvent,
            rio.KeyUpEvent,
            rio.MouseDownEvent,
            rio.MouseEnterEvent,
            rio.MouseLeaveEvent,
            rio.MouseMoveEvent,
            rio.MouseUpEvent,
            rio.NumberInputChangeEvent,
            rio.NumberInputConfirmEvent,
            rio.PopupOpenOrCloseEvent,
            rio.RevealerChangeEvent,
            rio.TextInputChangeEvent,
            rio.TextInputConfirmEvent,
        ),
    ),
)


# Flattened view of `DOCUMENTATION_STRUCTURE`. This is a sequence of tuples:
#
# - URL Segment
# - Section Name
# - Article Name
# - Article generation function, or `Component` class
def _compute_linear() -> (
    Tuple[
        Tuple[str, str, str, Union[Callable[[], article.Article], Type[rio.Component]]],
        ...,
    ]
):
    result = []

    for section in DOCUMENTATION_STRUCTURE:
        # `None` is used to represent whitespace
        if section is None:
            continue

        # Otherwise, it's a tuple of (title, articles)
        section_title, arts = section

        # ... where each article is either a tuple of (name, url_segment,
        # article), or a rio `Component`
        for art in arts:
            if isinstance(art, tuple):
                for art in arts:
                    name, url_segment, generate_article = art  # type: ignore
                    result.append((url_segment, section_title, name, generate_article))

            else:
                assert inspect.isclass(art), art

                for art in arts:
                    name = art.__name__  # type: ignore
                    result.append((name, section_title, name, art))

    return tuple(result)


DOCUMENTATION_STRUCTURE_LINEAR = _compute_linear()


# Maps URL segments to the sections they're in
def _compute_url_segment_to_section() -> Dict[str, str]:
    result = {}

    for url_segment, section_name, _, __ in DOCUMENTATION_STRUCTURE_LINEAR:
        result[url_segment] = section_name

    return result


DOCUMENTATION_URL_SEGMENT_TO_SECTION = _compute_url_segment_to_section()
