from dataclasses import KW_ONLY
from typing import *  # type: ignore

import rio

__all__ = ["Bully"]


class Bully(rio.components.fundamental_component.FundamentalComponent):
    prefix: str
    suffix: str
    entries: list[str]
    _: KW_ONLY
    linger_time: float = 1.0
    font_size: float = 1.0

    @classmethod
    def build_javascript_source(cls, sess: rio.Session) -> str:
        return """

class Bully {
    currentIndex = 1;

    createElement() {
        // Create the HTML
        let element = document.createElement('div');
        element.classList.add('rio-bully')
        element.innerHTML = `
            <div>
                <div></div>
                <div>
                    <div></div>
                </div>
                <div></div>
            </div>
        `;


        // Expose the elements
        [this.prefixElement, this.centerContainer, this.suffixElement] = element.firstElementChild.children;

        let curChild = document.createElement("div");
        curChild.textContent = this.state().entries[0];
        this.centerContainer.appendChild(curChild);

        // Get to work
        requestAnimationFrame(this.worker.bind(this));

        return element;
    }

    updateElement(deltaState) {
        // Prefix
        if (deltaState.prefix !== undefined) {
            this.prefixElement.textContent = deltaState.prefix;
        }

        // Suffix
        if (deltaState.suffix !== undefined) {
            this.suffixElement.textContent = deltaState.suffix;
        }

        // Font size
        if (deltaState.font_size !== undefined) {
            this.element.style.fontSize = `${deltaState.font_size}rem`;
        }
    }

    worker() {
        // Remove the oldest item
        this.centerContainer.removeChild(this.centerContainer.children[0]);

        // Transition out the previous item
        let oldElement = this.centerContainer.children[0];
        oldElement.classList.add("rio-bully-outgoing");

        // Add the new item
        this.state();
        var newElement = document.createElement("div");
        newElement.textContent = this.state().entries[this.currentIndex];
        newElement.classList.add("rio-bully-incoming");
        this.centerContainer.appendChild(newElement);

        // Smoothly vary the width of the center container
        let newWidth = newElement.scrollWidth;
        this.centerContainer.style.width = `${newElement.scrollWidth}px`;

        // Commit the CSS
        this.centerContainer.offsetWidth;

        // Transition in the new item
        newElement.classList.remove("rio-bully-incoming");

        // Housekeeping
        this.currentIndex = (this.currentIndex + 1) % this.state().entries.length;

        // Go again?
        setTimeout(this.worker.bind(this), this.state().linger_time * 1000);
    }
}
"""

    @classmethod
    def build_css_source(cls, sess: rio.Session) -> str:
        return """
.rio-bully {
    display: flex;
    align-items: center;
    justify-content: center;

    white-space: pre;
}

.rio-bully > div {
    display: flex;
}

.rio-bully > div > *:nth-child(2) {
    position: relative;

    display: flex;
    justify-content: center;

    font-weight: bold;
    color: var(--rio-local-accent-bg);

    transition: width 0.4s ease-in-out;
}

.rio-bully > div > *:nth-child(2) > * {
    transition: all 0.4s ease-in-out;
}

.rio-bully-outgoing {
    position: absolute;
    opacity: 0;
    transform: translateY(-100%);
}

.rio-bully-incoming {
    opacity: 0;
    transform: translateY(100%);
}
"""
