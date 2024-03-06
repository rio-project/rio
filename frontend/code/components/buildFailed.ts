import { applyIcon } from '../designApplication';
import { ComponentBase, ComponentState } from './componentBase';

export type BuildFailedState = ComponentState & {
    _type_: 'BuildFailed-builtin';
};

export class BuildFailedComponent extends ComponentBase {
    state: Required<BuildFailedState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-build-failed');

        if (globalThis.RIO_DEBUG_MODE) {
            element.title = "This component's build function threw an error";
        }

        applyIcon(
            element,
            'material/error:fill',
            'var(--rio-global-danger-fg)'
        );

        return element;
    }

    updateElement(
        deltaState: BuildFailedState,
        latentComponents: Set<ComponentBase>
    ): void {
        this.naturalWidth = this.naturalHeight = 1;
    }
}
