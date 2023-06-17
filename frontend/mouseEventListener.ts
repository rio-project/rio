import { pixelsPerEm, replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

function eventMouseButtonToString(event: MouseEvent): object {
    return {
        button: ['left', 'middle', 'right'][event.button],
    };
}

function eventMousePositionToString(event: MouseEvent): object {
    return {
        x: event.clientX / pixelsPerEm,
        y: event.clientY / pixelsPerEm,
    };
}

export type MouseEventListenerState = WidgetState & {
    _type_: 'mouseEventListener';
    child?: number;
    reportMouseDown?: boolean;
    reportMouseUp?: boolean;
    reportMouseMove?: boolean;
    reportMouseEnter?: boolean;
    reportMouseLeave?: boolean;
};

export class MouseEventListenerWidget extends WidgetBase {
    createInnerElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-mouse-event-listener');
        return element;
    }

    updateInnerElement(
        element: HTMLElement,
        deltaState: MouseEventListenerState
    ): void {
        replaceOnlyChild(element, deltaState.child);

        if (deltaState.reportMouseDown) {
            element.onmousedown = (e) => {
                this.sendMessageToBackend({
                    type: 'mouseDown',
                    ...eventMouseButtonToString(e),
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmousedown = null;
        }

        if (deltaState.reportMouseUp) {
            element.onmouseup = (e) => {
                this.sendMessageToBackend({
                    type: 'mouseUp',
                    ...eventMouseButtonToString(e),
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmouseup = null;
        }

        if (deltaState.reportMouseMove) {
            element.onmousemove = (e) => {
                this.sendMessageToBackend({
                    type: 'mouseMove',
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmousemove = null;
        }

        if (deltaState.reportMouseEnter) {
            element.onmouseenter = (e) => {
                this.sendMessageToBackend({
                    type: 'mouseEnter',
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmouseenter = null;
        }

        if (deltaState.reportMouseLeave) {
            element.onmouseleave = (e) => {
                this.sendMessageToBackend({
                    type: 'mouseLeave',
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmouseleave = null;
        }
    }
}
