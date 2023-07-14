from __future__ import annotations

from .. import session
from . import widget_base

__all__ = [
    "MarkdownView",
]


class MarkdownView(widget_base.HtmlWidget):
    text: str

    @classmethod
    def build_javascript_source(cls, sess: session.Session) -> str:
        return """

function loadShowdown(callback) {
    if (typeof showdown === 'undefined') {
        console.log('Fetching showdown.js');
        let script = document.createElement('script');
        script.src = '%s/reflex/asset/showdown.min.js';
        script.onload = callback;
        document.head.appendChild(script);
    } else {
        callback();
    }
}

class MarkdownView extends WidgetBase  {
    createElement(){
        const element = document.createElement('div');
        return element;
    }

    updateElement(element, deltaState) {
        if (deltaState.text !== undefined) {
            loadShowdown(function() {
                const converter = new showdown.Converter();
                const html = converter.makeHtml(deltaState.text);
                element.innerHTML = html;
            });
        }
    }
}
    """ % (
            sess.app_server.external_url
        )
