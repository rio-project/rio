import {
    getInstanceByComponentId,
    replaceOnlyChildAndResetCssProperties,
} from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type AlignState = ComponentState & {
    _type_: 'Align-builtin';
    child?: number | string;
    align_x?: number | null;
    align_y?: number | null;
};

export class AlignComponent extends ComponentBase {
    state: Required<AlignState>;

    _createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-align');
        return element;
    }

    _updateElement(element: HTMLElement, deltaState: AlignState): void {
        replaceOnlyChildAndResetCssProperties(
            element.id,
            element,
            deltaState.child
        );
    }

    updateChildLayouts(): void {
        // Prepare the list of CSS properties to apply to the child
        let align_x: number = this.state['align_x']!;
        let align_y: number = this.state['align_y']!;

        let cssProperties = {};

        let transform_x: number;
        if (align_x === null) {
            cssProperties['width'] = '100%';
            transform_x = 0;
        } else {
            cssProperties['width'] = 'fit-content';
            cssProperties['left'] = `${align_x * 100}%`;
            transform_x = align_x * -100;
        }

        let transform_y: number;
        if (align_y === null) {
            cssProperties['height'] = '100%';
            transform_y = 0;
        } else {
            cssProperties['height'] = 'fit-content';
            cssProperties['top'] = `${align_y * 100}%`;
            transform_y = align_y * -100;
        }

        if (transform_x !== 0 || transform_y !== 0) {
            cssProperties[
                'transform'
            ] = `translate(${transform_x}%, ${transform_y}%)`;
        }

        // Apply the CSS properties to the child
        let child = getInstanceByComponentId(this.state['child']);
        child.replaceLayoutCssProperties(cssProperties);
    }
}
