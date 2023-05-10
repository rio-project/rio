import { buildWidget } from "./app";
import { JsonColumn } from "./models";

export class ColumnWidget {
    static build(data: JsonColumn): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('pygui-column');

        for (const child of data.children) {
            element.appendChild(buildWidget(child));
        }

        return element;
    }

    static update(element: HTMLElement, deltaState: JsonColumn): void { }
}
