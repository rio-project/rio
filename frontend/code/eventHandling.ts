export abstract class EventHandler {
    // TODO: Should `disconnect` also remove the handler from `ComponentBase._eventHandlers`?
    abstract disconnect(): void;
}

function _no_op(): void {}

export class DragHandler extends EventHandler {
    private element: HTMLElement;
    private onMove: (event: MouseEvent) => void;
    private onEnd: (event: MouseEvent) => void;
    private onStart: (event: MouseEvent) => void;

    private onMouseDown = this._onMouseDown.bind(this);
    private onMouseMove = this._onMouseMove.bind(this);
    private onMouseUp = this._onMouseUp.bind(this);

    constructor(
        element: HTMLElement,
        onStart: null | ((event: MouseEvent) => void) = null,
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
        this.onStart(event);
        window.addEventListener('mousemove', this.onMouseMove, true);
        window.addEventListener('mouseup', this.onMouseUp, true);
    }

    private _onMouseMove(event: MouseEvent): void {
        this.onMove(event);
    }

    private _onMouseUp(event: MouseEvent): void {
        this._disconnectDragListeners();
        this.onEnd(event);
    }

    private _disconnectDragListeners(): void {
        window.removeEventListener('mousemove', this.onMouseMove, true);
        window.removeEventListener('mouseup', this.onMouseUp, true);
    }

    override disconnect(): void {
        this.element.removeEventListener('mousedown', this.onMouseDown, true);
        this._disconnectDragListeners();
    }
}
