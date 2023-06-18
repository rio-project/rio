import { getInstanceByWidgetId, replaceChildren } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type RowState = WidgetState & {
    _type_: 'row';
    children?: (number | string)[];
    spacing?: number;
};

export class RowWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-row');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: RowState): void {
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
            anyGrowers = anyGrowers || child.state['_grow_'][0];
        }

        for (let child of children) {
            child.replaceLayoutCssProperties({
                'flex-grow':
                    !anyGrowers || child.state['_grow_'][0] ? '1' : '0',
            });
        }
    }
}
