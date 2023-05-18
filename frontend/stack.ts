import { replaceChildren } from './app';
import { JsonStack } from './models';

export class StackWidget {
    static build(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-stack');
        return element;
    }

    static update(element: HTMLElement, deltaState: JsonStack): void {
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
