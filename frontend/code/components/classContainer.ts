import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';
import { replaceOnlyChild } from '../componentManagement';

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
        if (deltaState.child !== undefined) {
            replaceOnlyChild(element.id, element, deltaState.child);
            this.makeLayoutDirty();
        }

        if (deltaState.classes !== undefined) {
            // Remove all old values
            element.className = '';

            // Add all new values
            element.classList.add(...deltaState.classes);
        }
    }
}
