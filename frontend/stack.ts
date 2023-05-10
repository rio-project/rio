import { buildWidget } from "./app";
import { JsonStack } from "./models";

export class StackWidget {
    static build(data: JsonStack): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('pygui-stack');

        for (let ii = 0; ii < data.children.length; ii++) {
            const childElement = buildWidget(data.children[ii]);
            childElement.style.zIndex = `${ii + 1}`;
            element.appendChild(childElement);
        }

        return element;
    }

    static update(element: HTMLElement, deltaState: JsonStack): void { }

}