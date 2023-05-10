import { buildWidget } from "./app";
import { JsonMargin } from "./models";

export class MarginWidget {

    static build(widget: JsonMargin): HTMLElement {
        let element = document.createElement('div');
        element.appendChild(buildWidget(widget.child));
        return element;
    }

    static update(element: HTMLElement, state: JsonMargin): void {

    }
}