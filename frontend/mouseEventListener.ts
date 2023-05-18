import { JsonMouseEventListener } from './models';
import { pixelsPerEm, replaceOnlyChild, sendEvent } from './app';

function eventMouseButtonToString(event: any): object {
    return {
        button: ['left', 'middle', 'right'][event.button],
    };
}

function eventMousePositionToString(event: any): object {
    return {
        x: event.clientX / pixelsPerEm,
        y: event.clientY / pixelsPerEm,
    };
}

export class MouseEventListener {
    static build(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-mouse-event-listener');
        return element;
    }

    static update(
        element: HTMLElement,
        deltaState: JsonMouseEventListener
    ): void {
        replaceOnlyChild(element, deltaState.child);

        if (deltaState.reportMouseDown) {
            element.onmousedown = (e) => {
                sendEvent(element, 'mouseDownEvent', {
                    ...eventMouseButtonToString(e),
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmousedown = null;
        }

        if (deltaState.reportMouseUp) {
            element.onmouseup = (e) => {
                sendEvent(element, 'mouseUpEvent', {
                    ...eventMouseButtonToString(e),
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            element.onmouseup = null;
        }

        // TODO
    }
}
