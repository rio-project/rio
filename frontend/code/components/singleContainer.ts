import { ComponentId } from "../models";
import { getInstanceByComponentId, replaceOnlyChildAndResetCssProperties } from "../componentManagement";
import { ComponentBase, ComponentState } from "./componentBase";


/// Base class for components that only have a single child.
/// It automatically:
/// 1. Adds the `rio-single-container` CSS class to the element
/// 2. Calls `replaceOnlyChild` in `updateElement` (You can override
///    `_updateElement` if you also need to do anything else.)
/// 3. Implements `updateChildLayouts`
///
/// This class automatically knows in which attribute the child is stored thanks
/// to `globalThis.childAttributeNames`.
export abstract class SingleContainer extends ComponentBase {
    constructor(elementId: string, state: Required<ComponentState>) {
        super(elementId, state);

        this._minSizeComponentImpl[0] = 'fit-content';
    }

    createElement(): HTMLElement {
        let element = super.createElement();

        element.classList.add('rio-single-container');

        return element;
    }

    updateElement(element: HTMLElement, deltaState: ComponentState): void {
        super.updateElement(element, deltaState);

        let childId: ComponentId | null | undefined = deltaState[this.childAttributeName()];
        if (childId !== undefined && childId !== null) {
            replaceOnlyChildAndResetCssProperties(element, childId);

            let child = getInstanceByComponentId(childId);
            child.replaceLayoutCssProperties({});
        }
    }

    _updateElement(element: HTMLElement, deltaState: ComponentState): void { }

    protected getChildId(): ComponentId | null {
        return this.state[this.childAttributeName()];
    }

    childAttributeName(): string {
        let childAttributeNames = globalThis.childAttributeNames[this.state['_type_']];

        if (childAttributeNames === undefined) {
            throw new Error(`Unknown childAttributeNames for component type ${this.state['_type_']}`);
        }

        return childAttributeNames[0];
    }
}
