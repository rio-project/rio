export type WidgetState = {
    _type_: string;
    _python_type_: string;
    _key_?: string;
    _margin_?: [number, number, number, number];
    _size_?: [number | null, number | null];
    _align_?: [number | null, number | null];
};

export abstract class WidgetBase {
    elementId: string;
    state: object;

    constructor(elementId: string, state: WidgetState) {
        this.elementId = elementId;
        this.state = state;
    }

    get element() {
        let element = document.getElementById(this.elementId);

        if (element === null) {
            throw new Error(
                `Instance for element with id ${this.elementId} cannot find its element`
            );
        }

        return element;
    }

    abstract createElement(): HTMLElement;

    abstract updateElement(element: HTMLElement, deltaState: WidgetState): void;
}
