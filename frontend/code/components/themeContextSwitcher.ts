import { applyColorSet } from '../designApplication';
import { ColorSet, ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { SingleContainer } from './singleContainer';

export type ThemeContextSwitcherState = ComponentState & {
    _type_: 'ThemeContextSwitcher-builtin';
    child?: ComponentId;
    color?: ColorSet;
};

export class ThemeContextSwitcherComponent extends SingleContainer {
    state: Required<ThemeContextSwitcherState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        return element;
    }

    updateElement(
        deltaState: ThemeContextSwitcherState,
        latentComponents: Set<ComponentBase>
    ): void {
        // Update the child
        this.replaceOnlyChild(latentComponents, deltaState.child);

        // Colorize
        if (deltaState.color !== undefined) {
            applyColorSet(this.element, deltaState.color);
        }
    }
}
