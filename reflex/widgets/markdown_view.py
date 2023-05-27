from __future__ import annotations

from . import widget_base

__all__ = [
    "MarkdownView",
]


class MarkdownView(widget_base.HtmlWidget):
    text: str

    javascript_source = """
class MarkdownView extends WidgetBase  {
    createElement(){
        let element = document.createElement('div');
        return element;
    }

    updateElement(element, deltaState) {
        if (deltaState.text !== undefined) {
            element.innerText = deltaState.text;
        }
    }
}
    """

    css_source = ""
