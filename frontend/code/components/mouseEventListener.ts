import { pixelsPerEm } from '../app';
import {
    getInstanceByComponentId,
    replaceOnlyChild,
} from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

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

export class MouseEventListenerComponent extends ComponentBase {
    state: Required<MouseEventListenerState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-single-container');
        return element;
    }

    updateElement(
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

    updateChildLayouts(): void {
        getInstanceByComponentId(
            this.state['child']
        ).replaceLayoutCssProperties({});
    }
}
