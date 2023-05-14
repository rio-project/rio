import { buildWidget } from './app';
import { JsonMargin } from './models';

export class MarginWidget {
    static build(widget: JsonMargin): HTMLElement {
        let element = document.createElement('div');
        element.appendChild(buildWidget(widget.child));
        return element;
    }

    static update(element: HTMLElement, state: JsonMargin): void {
        if (state.margin_left !== undefined) {
            element.style.marginLeft = `${state.margin_left}em`;
        }

        if (state.margin_top !== undefined) {
            element.style.marginTop = `${state.margin_top}em`;
        }

        if (state.margin_right !== undefined) {
            element.style.marginRight = `${state.margin_right}em`;
        }

        if (state.margin_bottom !== undefined) {
            element.style.marginBottom = `${state.margin_bottom}em`;
        }
    }
}
