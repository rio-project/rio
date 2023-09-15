import { replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type ClassContainerState = WidgetState & {
    _type_: 'ClassContainer-builtin';
    child?: null | number | string;
    classes?: string[];
};

export class ClassContainerWidget extends WidgetBase {
    state: Required<ClassContainerState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: ClassContainerState): void {
        replaceOnlyChild(element, deltaState.child);

        if (deltaState.classes !== undefined) {
            // Remove all old values
            element.classList.forEach((className) => {
                element.classList.remove(className);
            });

            // Add all new values
            element.classList.add('reflex-single-container');
            deltaState.classes.forEach((className) => {
                element.classList.add(className);
            });
        }
    }
}
