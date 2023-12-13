import { pixelsPerEm } from '../app';
import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';
import { DragHandler } from '../eventHandling';
import { ComponentId } from '../models';

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

function findComponentUnderMouse(event: MouseEvent): ComponentId {
    // The coordinates for `elementFromPoint` are relative to the viewport. This
    // matches `event.clientX` and `event.clientY`.
    let element = document.elementFromPoint(
        event.clientX,
        event.clientY
    ) as HTMLElement;

    // It could be an internal element. Go up the tree until we find a Component
    while (!element.id.startsWith('rio-id-')) {
        element = element.parentElement as HTMLElement;
    }

    // Make sure not to return any injected Align or Margin components
    while (element.id.endsWith('-align') || element.id.endsWith('-margin')) {
        element = element.parentElement as HTMLElement;
    }

    return parseInt(element.id.slice('rio-id-'.length));
}

export type MouseEventListenerState = ComponentState & {
    _type_: 'mouseEventListener';
    child?: number | string;
    reportMouseDown: boolean;
    reportMouseUp: boolean;
    reportMouseMove: boolean;
    reportMouseEnter: boolean;
    reportMouseLeave: boolean;
    reportMouseDrag: boolean;
};

export class MouseEventListenerComponent extends SingleContainer {
    state: Required<MouseEventListenerState>;

    private _dragHandler: DragHandler | null = null;
    private _dragStart: MouseEvent;
    private _dragStartComponent: ComponentId;

    createElement(): HTMLElement {
        return document.createElement('div');
    }

    updateElement(
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

        if (deltaState.reportMouseDrag) {
            this._dragHandler = this.addDragHandler(
                element,
                this._onDragStart.bind(this),
                null,
                this._onDragEnd.bind(this)
            );
        } else {
            if (this._dragHandler !== null) {
                this._dragHandler.disconnect();
                this._dragHandler = null;
            }
        }
    }

    private _onDragStart(event: MouseEvent): void {
        this._dragStart = event;
        this._dragStartComponent = findComponentUnderMouse(event);
    }

    private _onDragEnd(event: MouseEvent): void {
        this.sendMessageToBackend({
            type: 'mouseDrag',
            ...eventMouseButtonToString(this._dragStart),
            startX: this._dragStart.clientX / pixelsPerEm,
            startY: this._dragStart.clientY / pixelsPerEm,
            startComponent: this._dragStartComponent,
            endX: event.clientX / pixelsPerEm,
            endY: event.clientY / pixelsPerEm,
            endComponent: findComponentUnderMouse(event),
        });
    }
}
