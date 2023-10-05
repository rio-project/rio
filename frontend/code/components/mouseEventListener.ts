import { pixelsPerEm } from '../app';
import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';

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

export type MouseEventListenerState = ComponentState & {
    _type_: 'mouseEventListener';
    child?: number | string;
    reportMouseDown: boolean;
    reportMouseUp: boolean;
    reportMouseMove: boolean;
    reportMouseEnter: boolean;
    reportMouseLeave: boolean;
};

export class MouseEventListenerComponent extends SingleContainer {
    state: Required<MouseEventListenerState>;

    _createElement(): HTMLElement {
        return document.createElement('div');
    }

    _updateElement(
        element: HTMLElement,
        deltaState: MouseEventListenerState
    ): void {
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
