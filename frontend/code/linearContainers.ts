import { getInstanceByWidgetId, replaceChildren } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type LinearContainerState = WidgetState & {
    _type_: 'row' | 'column';
    children?: (number | string)[];
    spacing?: number;
};

class LinearContainer extends WidgetBase {
    state: Required<LinearContainerState>;

    protected childContainer: HTMLElement;
    private grower1: HTMLElement;
    private grower2: HTMLElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');

        this.grower1 = document.createElement('div');
        this.grower1.classList.add('rio-undefined-space');

        this.childContainer = document.createElement('div');

        this.grower2 = document.createElement('div');
        this.grower2.classList.add('rio-undefined-space');

        // The growers are placed in a a separate container so that they don't
        // caus additional spacing at the start and end of the
        // `LinearContainer`.
        element.append(this.grower1);
        element.append(this.childContainer);
        element.append(this.grower2);

        return element;
    }

    updateElement(
        element: HTMLElement,
        deltaState: LinearContainerState
    ): void {
        // Update the children
        replaceChildren(this.childContainer, deltaState.children);

        // Spacing
        if (deltaState.spacing !== undefined) {
            this.childContainer.style.gap = `${deltaState.spacing}rem`;
        }
    }

    updateChildLayouts_(size_index: number): void {
        let anyGrowers = false;

        // Update everyone's `flex-grow` property.
        for (let childId of this.state['children']) {
            let child = getInstanceByWidgetId(childId);
            anyGrowers = anyGrowers || child.state['_grow_'][size_index];
            child.replaceLayoutCssProperties({
                'flex-grow': child.state['_grow_'][size_index] ? '1' : '0',
            });
        }

        // If there aren't any growers highlight the undefined space
        this.grower1.style.flexGrow = anyGrowers ? '0' : '1';
        this.grower2.style.flexGrow = anyGrowers ? '0' : '1';
        this.childContainer.style.flexGrow = anyGrowers ? '1' : '0';
    }
}

export class ColumnWidget extends LinearContainer {
    createElement(): HTMLElement {
        let element = super.createElement();
        element.classList.add('rio-column');

        return element;
    }

    updateChildLayouts(): void {
        this.updateChildLayouts_(1);
    }
}

export class RowWidget extends LinearContainer {
    createElement(): HTMLElement {
        let element = super.createElement();
        element.classList.add('rio-row');

        return element;
    }

    updateChildLayouts(): void {
        this.updateChildLayouts_(0);
    }
}
