import { pixelsPerEm } from '../app';
import { SingleContainer } from './singleContainer';
import { ComponentBase, ComponentState } from './componentBase';
import { DragHandler } from '../eventHandling';
import { tryGetComponentByElement } from '../componentManagement';
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
    let element = document.elementFromPoint(event.clientX, event.clientY)!;

    // It could be an internal element. Go up the tree until we find a Component
    let component: ComponentBase | null;
    while (true) {
        component = tryGetComponentByElement(element);

        if (component !== null) {
            break;
        }

        element = element.parentElement!;
    }

    // Make sure not to return any injected Align or Margin components
    while (component.isInjectedLayoutComponent()) {
        component = component.parent!;
    }

    return component.id;
}

export type MouseEventListenerState = ComponentState & {
    _type_: 'MouseEventListener-builtin';
    child?: ComponentId;
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
    private _dragStartComponentId: ComponentId;

    createElement(): HTMLElement {
        return document.createElement('div');
    }

    updateElement(
        deltaState: MouseEventListenerState,
        latentComponents: Set<ComponentBase>
    ): void {
        this.replaceOnlyChild(latentComponents, deltaState.child);

        if (deltaState.reportMouseDown) {
            this.element.onmousedown = (e) => {
                this.sendMessageToBackend({
                    type: 'mouseDown',
                    ...eventMouseButtonToString(e),
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            this.element.onmousedown = null;
        }

        if (deltaState.reportMouseUp) {
            this.element.onmouseup = (e) => {
                this.sendMessageToBackend({
                    type: 'mouseUp',
                    ...eventMouseButtonToString(e),
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            this.element.onmouseup = null;
        }

        if (deltaState.reportMouseMove) {
            this.element.onmousemove = (e) => {
                this.sendMessageToBackend({
                    type: 'mouseMove',
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            this.element.onmousemove = null;
        }

        if (deltaState.reportMouseEnter) {
            this.element.onmouseenter = (e) => {
                this.sendMessageToBackend({
                    type: 'mouseEnter',
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            this.element.onmouseenter = null;
        }

        if (deltaState.reportMouseLeave) {
            this.element.onmouseleave = (e) => {
                this.sendMessageToBackend({
                    type: 'mouseLeave',
                    ...eventMousePositionToString(e),
                });
            };
        } else {
            this.element.onmouseleave = null;
        }

        if (deltaState.reportMouseDrag) {
            this._dragHandler = this.addDragHandler(
                this.element,
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

    private _onDragStart(event: MouseEvent): boolean {
        this._dragStart = event;
        this._dragStartComponentId = findComponentUnderMouse(event);
        return true;
    }

    private _onDragEnd(event: MouseEvent): void {
        this.sendMessageToBackend({
            type: 'mouseDrag',
            ...eventMouseButtonToString(this._dragStart),
            startX: this._dragStart.clientX / pixelsPerEm,
            startY: this._dragStart.clientY / pixelsPerEm,
            startComponent: this._dragStartComponentId,
            endX: event.clientX / pixelsPerEm,
            endY: event.clientY / pixelsPerEm,
            endComponent: findComponentUnderMouse(event),
        });
    }
}
