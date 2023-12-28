import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';
import { ComponentId } from '../models';

export type ClassContainerState = ComponentState & {
    _type_: 'ClassContainer-builtin';
    child?: ComponentId | null;
    classes?: string[];
};

export class ClassContainerComponent extends SingleContainer {
    state: Required<ClassContainerState>;

    createElement(): HTMLElement {
        return document.createElement('div');
    }

    updateElement(deltaState: ClassContainerState): void {
        this.replaceOnlyChild(deltaState.child);

        if (deltaState.classes !== undefined) {
            // Remove all old values
            this.element.className = '';

            // Add all new values
            this.element.classList.add(...deltaState.classes);
        }
    }
}
