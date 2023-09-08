import { getInstanceByWidgetId, replaceChildren } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type StackState = WidgetState & {
    _type_: 'stack';
    children?: number[];
};

export class StackWidget extends WidgetBase {
    state: Required<StackState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-stack');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: StackState): void {
        replaceChildren(element, deltaState.children);
    }

    updateChildLayouts(): void {
        let zIndex = 0;
        for (let childId of this.state.children) {
            let child = getInstanceByWidgetId(childId);
            
            child.replaceLayoutCssProperties({zIndex: `${zIndex}`});
            zIndex += 1;
        }
    }
}
