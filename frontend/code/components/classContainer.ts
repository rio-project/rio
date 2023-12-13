import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';

export type ClassContainerState = ComponentState & {
    _type_: 'ClassContainer-builtin';
    child?: null | number | string;
    classes?: string[];
};

export class ClassContainerComponent extends SingleContainer {
    state: Required<ClassContainerState>;

    createElement(): HTMLElement {
        return document.createElement('div');
    }

    updateElement(element: HTMLElement, deltaState: ClassContainerState): void {
        if (deltaState.classes !== undefined) {
            // Remove all old values
            element.className = '';

            // Add all new values
            element.classList.add(
                'rio-single-container',
                ...deltaState.classes
            );
        }
    }
}
