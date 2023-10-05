import {
    getInstanceByComponentId,
    replaceOnlyChild,
} from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type MarginState = ComponentState & {
    _type_: 'Margin-builtin';
    child?: number | string;
    margin_left?: number;
    margin_top?: number;
    margin_right?: number;
    margin_bottom?: number;
};

export class MarginComponent extends ComponentBase {
    state: Required<MarginState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-margin');
        element.classList.add('rio-single-container');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: MarginState): void {
        replaceOnlyChild(element, deltaState.child);

        if (deltaState.margin_left !== undefined) {
            element.style.paddingLeft = `${deltaState.margin_left}em`;
        }

        if (deltaState.margin_top !== undefined) {
            element.style.paddingTop = `${deltaState.margin_top}em`;
        }

        if (deltaState.margin_right !== undefined) {
            element.style.paddingRight = `${deltaState.margin_right}em`;
        }

        if (deltaState.margin_bottom !== undefined) {
            element.style.paddingBottom = `${deltaState.margin_bottom}em`;
        }
    }

    updateChildLayouts(): void {
        getInstanceByComponentId(
            this.state['child']
        ).replaceLayoutCssProperties({});
    }
}
