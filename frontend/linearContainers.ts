import { getInstanceByWidgetId, replaceChildren } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type LinearContainerState = WidgetState & {
    _type_: 'row' | 'colum';
    children?: (number | string)[];
    spacing?: number;
};

class LinearContainer extends WidgetBase {
    state: Required<LinearContainerState>;

    private grower1: HTMLElement;
    private grower2: HTMLElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');

        this.grower1 = document.createElement('div');
        this.grower1.classList.add('reflex-undefined-space');

        this.grower2 = document.createElement('div');
        this.grower2.classList.add('reflex-undefined-space');

        return element;
    }

    updateElement(
        element: HTMLElement,
        deltaState: LinearContainerState
    ): void {
        // Update the children. Take care to remove and later re-add any
        // growers, since it's not a child in the reflex sense.
        this.grower1.remove();
        this.grower2.remove();

        replaceChildren(element, deltaState.children);

        element.prepend(this.grower1);
        element.append(this.grower2);

        // Spacing
        if (deltaState.spacing !== undefined) {
            element.style.gap = `${deltaState.spacing}em`;
        }
    }

    updateChildLayouts(): void {
        let anyGrowers = false;

        // Update everyone's `flex-grow` property.
        for (let childId of this.state['children']) {
            let child = getInstanceByWidgetId(childId);
            anyGrowers = anyGrowers || child.state['_grow_'][0];
            child.replaceLayoutCssProperties({
                'flex-grow': child.state['_grow_'][0] ? '1' : '0',
            });
        }

        // If there aren't any growers highlight the undefined space
        this.grower1.style.flexGrow = anyGrowers ? '0' : '1';
        this.grower2.style.flexGrow = anyGrowers ? '0' : '1';
    }
}

export class ColumnWidget extends LinearContainer {
    createElement(): HTMLElement {
        let element = super.createElement();
        element.classList.add('reflex-column');
        return element;
    }
}

export class RowWidget extends LinearContainer {
    createElement(): HTMLElement {
        let element = super.createElement();
        element.classList.add('reflex-row');
        return element;
    }
}
