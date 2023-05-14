import { JsonText } from "./models";
import { colorToCss } from "./app";

export class TextWidget {
    static build(data: JsonText): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('pygui-text');
        return element;
    }

    static update(element: HTMLElement, deltaState: JsonText): void {
        if (deltaState.text !== undefined) {
            element.innerText = deltaState.text;
        }

        if (deltaState.multiline !== undefined) {
            element.style.whiteSpace = deltaState.multiline ? 'normal' : 'nowrap';
        }

        if (deltaState.font !== undefined) {
            element.style.fontFamily = deltaState.font;
        }

        if (deltaState.font_color !== undefined) {
            element.style.color = colorToCss(deltaState.font_color);
        }

        if (deltaState.font_size !== undefined) {
            element.style.fontSize = deltaState.font_size + 'em';
        }

        if (deltaState.font_weight !== undefined) {
            element.style.fontWeight = deltaState.font_weight;
        }

        if (deltaState.italic !== undefined) {
            element.style.fontStyle = deltaState.italic ? 'italic' : 'normal';
        }

        if (deltaState.underlined !== undefined) {
            element.style.textDecoration = deltaState.underlined
                ? 'underline'
                : 'none';
        }
    }
}