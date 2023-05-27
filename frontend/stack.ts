import { replaceChildren } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type StackState = WidgetState & {
    _type_: 'stack';
    children?: number[];
};

export class StackWidget extends WidgetBase  {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-stack');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: StackState): void {
        if (deltaState.children !== undefined) {
            replaceChildren(element, deltaState.children);

            let zIndex = 0;
            for (let child of element.children) {
                (child as HTMLElement).style.zIndex = `${zIndex}`;
                zIndex += 1;
            }
        }
    }
}
