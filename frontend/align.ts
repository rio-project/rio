import { buildWidget } from "./app";
import { JsonAlign } from "./models";

export class AlignWidget {
    static build(data: JsonAlign): HTMLElement {
        let element = document.createElement('div');
        element.appendChild(buildWidget(data.child));
        return element;
    }

    static update(element: HTMLElement, state: JsonAlign): void {
        if (state.align_x !== undefined) {
            if (state.align_x === null) {
                element.style.justifyContent = 'unset';
            } else {
                element.style.justifyContent = state.align_x * 100 + '%';
            }
        }

        if (state.align_y !== undefined) {
            if (state.align_y === null) {
                element.style.alignItems = 'unset';
            } else {
                element.style.alignItems = state.align_y * 100 + '%';
            }
        }
    }
}