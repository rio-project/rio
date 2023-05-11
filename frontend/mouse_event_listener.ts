import { JsonMouseEventListener } from './models';
import { buildWidget, pixelsPerEm, sendEvent } from './app';


export class MouseEventListener {
    static build(data: JsonMouseEventListener): HTMLElement {
        let element = document.createElement('div');
        element.appendChild(buildWidget(data.child));
        return element;
    }

    static update(
        element: HTMLElement,
        deltaState: JsonMouseEventListener
    ): void {
        if (deltaState.reportMouseDown) {
            element.onmousedown = (e) => {
                sendEvent(element, 'mouseDownEvent', {
                    x: e.clientX / pixelsPerEm,
                    y: e.clientY / pixelsPerEm,
                });
            };
        } else {
            element.onmousedown = null;
        }

        if (deltaState.reportMouseUp) {
            element.onmouseup = (e) => {
                sendEvent(element, 'mouseUpEvent', {
                    x: e.clientX / pixelsPerEm,
                    y: e.clientY / pixelsPerEm,
                });
            };
        } else {
            element.onmouseup = null;
        }

        // TODO
    }
}
