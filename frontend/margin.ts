import { buildWidget } from "./app";
import { JsonMargin } from "./models";

export class MarginWidget {

    static build(widget: JsonMargin): HTMLElement {
        let element = document.createElement('div');
        element.appendChild(buildWidget(widget.child));
        return element;
    }

    static update(element: HTMLElement, state: JsonMargin): void {
        if (state.margin !== undefined) {
            element.style.marginLeft   = `${state.margin[0]}em`;
            element.style.marginTop    = `${state.margin[1]}em`;
            element.style.marginRight  = `${state.margin[2]}em`;
            element.style.marginBottom = `${state.margin[3]}em`;
        }
    }
}