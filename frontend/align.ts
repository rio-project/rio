import { getInstanceByWidgetId, replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type AlignState = WidgetState & {
    _type_: 'Align-builtin';
    child?: number | string;
    align_x?: number | null;
    align_y?: number | null;
};

export class AlignWidget extends WidgetBase {
    state: Required<AlignState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-align');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: AlignState): void {
        replaceOnlyChild(element, deltaState.child);
    }

    updateChildLayouts(): void {
        // Prepare the list of CSS properties to apply to the child
        let align_x: number = this.state['align_x']!;
        let align_y: number = this.state['align_y']!;

        let cssProperties = {};

        let transform_x;
        if (align_x === null) {
            cssProperties['width'] = '100%';
            transform_x = 0;
        } else {
            cssProperties['width'] = 'min-content';
            cssProperties['left'] = `${align_x * 100}%`;
            transform_x = align_x * -100;
        }

        let transform_y;
        if (align_y === null) {
            cssProperties['height'] = '100%';
            transform_y = 0;
        } else {
            cssProperties['height'] = 'min-content';
            cssProperties['top'] = `${align_y * 100}%`;
            transform_y = align_y * -100;
        }

        if (transform_x !== 0 || transform_y !== 0) {
            cssProperties[
                'transform'
            ] = `translate(${transform_x}%, ${transform_y}%)`;
        }

        // Apply the CSS properties to the child
        getInstanceByWidgetId(this.state['child']).replaceLayoutCssProperties(
            cssProperties
        );
    }
}
