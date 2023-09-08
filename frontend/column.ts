import { getInstanceByWidgetId, replaceChildren } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

type ColumnState = WidgetState & {
    _type_: 'column';
    children?: (number | string)[];
    spacing?: number;
};

export class ColumnWidget extends WidgetBase {
    state: Required<ColumnState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-column');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: ColumnState): void {
        replaceChildren(element, deltaState.children);

        if (deltaState.spacing !== undefined) {
            element.style.gap = `${deltaState.spacing}em`;
        }
    }

    updateChildLayouts(): void {
        let children: WidgetBase[] = [];
        let anyGrowers = false;

        for (let childId of this.state['children']) {
            let child = getInstanceByWidgetId(childId);
            children.push(child);
            anyGrowers = anyGrowers || child.state['_grow_'][1];
        }

        for (let child of children) {
            child.replaceLayoutCssProperties({
                'flex-grow':
                    !anyGrowers || child.state['_grow_'][1] ? '1' : '0',
            });
        }
    }
}
