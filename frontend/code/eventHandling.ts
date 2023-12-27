export abstract class EventHandler {
    // TODO: Should `disconnect` also remove the handler from `ComponentBase._eventHandlers`?
    abstract disconnect(): void;
}

function _no_op(): boolean {
    return true;
}

export class DragHandler extends EventHandler {
    private element: HTMLElement;
    private onStart: (event: MouseEvent) => boolean;
    private onMove: (event: MouseEvent) => void;
    private onEnd: (event: MouseEvent) => void;

    private onMouseDown = this._onMouseDown.bind(this);
    private onMouseMove = this._onMouseMove.bind(this);
    private onMouseUp = this._onMouseUp.bind(this);
    private onClick = this._onClick.bind(this);

    constructor(
        element: HTMLElement,
        onStart: null | ((event: MouseEvent) => boolean) = null,
        onMove: null | ((event: MouseEvent) => void) = null,
        onEnd: null | ((event: MouseEvent) => void) = null
    ) {
        super();

        this.element = element;

        this.onStart = onStart ?? _no_op;
        this.onMove = onMove ?? _no_op;
        this.onEnd = onEnd ?? _no_op;

        element.addEventListener('mousedown', this.onMouseDown, true);
    }

    private _onMouseDown(event: MouseEvent): void {
        let onStartResult = this.onStart(event);

        // It's easy to forget to return a boolean. Make sure to catch this
        // mistake.
        if (onStartResult !== true && onStartResult !== false) {
            throw new Error(
                `Drag event onStart must return a boolean, but it returned ${onStartResult}`
            );
        }

        // Don't continue if the handler isn't interested in the event.
        if (!onStartResult) {
            return;
        }

        event.stopPropagation();

        window.addEventListener('mousemove', this.onMouseMove, true);
        window.addEventListener('mouseup', this.onMouseUp, true);
        window.addEventListener('click', this.onClick, true);
    }

    private _onMouseMove(event: MouseEvent): void {
        event.stopPropagation();
        this.onMove(event);
    }

    private _onMouseUp(event: MouseEvent): void {
        event.stopPropagation();
        this._disconnectDragListeners();
        this.onEnd(event);
    }

    private _onClick(event: MouseEvent): void {
        // This event isn't using by the drag event handler, but it should
        // nonetheless be stopped to prevent the click from being handled by
        // other handlers.
        event.stopPropagation();
        event.stopImmediatePropagation();
        event.preventDefault();
    }

    private _disconnectDragListeners(): void {
        window.removeEventListener('mousemove', this.onMouseMove, true);
        window.removeEventListener('mouseup', this.onMouseUp, true);
        window.removeEventListener('click', this.onClick, true);
    }

    override disconnect(): void {
        this.element.removeEventListener('mousedown', this.onMouseDown, true);
        this._disconnectDragListeners();
    }
}
