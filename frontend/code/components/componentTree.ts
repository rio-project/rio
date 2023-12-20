import { ComponentBase, ComponentState } from './componentBase';

export type ComponentTreeState = ComponentState & {
    componenttree?: string;
};

export class ComponentTreeComponent extends ComponentBase {
    state: Required<ComponentTreeState>;

    private inner: HTMLElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-component-tree');

        element.textContent = 'TODO: Component Tree';

        return element;
    }

    updateElement(element: HTMLElement, deltaState: ComponentTreeState): void {}
}
