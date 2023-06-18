import { getInstanceByWidgetId, replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type MarginState = WidgetState & {
    _type_: 'Margin-builtin';
    child?: number | string;
    margin_left?: number;
    margin_top?: number;
    margin_right?: number;
    margin_bottom?: number;
};

export class MarginWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-margin');
        element.classList.add('reflex-single-container');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: MarginState): void {
        replaceOnlyChild(element, deltaState.child);

        if (deltaState.margin_left !== undefined) {
            element.style.paddingLeft = `${deltaState.margin_left}em`;
        }

        if (deltaState.margin_top !== undefined) {
            element.style.paddingTop = `${deltaState.margin_top}em`;
        }

        if (deltaState.margin_right !== undefined) {
            element.style.paddingRight = `${deltaState.margin_right}em`;
        }

        if (deltaState.margin_bottom !== undefined) {
            element.style.paddingBottom = `${deltaState.margin_bottom}em`;
        }
    }

    updateChildLayouts(): void {
        // let marginX = this.state['margin_left']! + this.state['margin_right']!;
        // let marginY = this.state['margin_top']! + this.state['margin_bottom']!;

        // getInstanceByWidgetId(this.state['child']).replaceLayoutCssProperties({
        //     'margin-left': `${this.state['margin_left']}em`,
        //     'margin-top': `${this.state['margin_top']}em`,
        //     'margin-right': `${this.state['margin_right']}em`,
        //     'margin-bottom': `${this.state['margin_bottom']}em`,
        //     width: `calc(100% - ${marginX}em)`,
        //     height: `calc(100% - ${marginY}em)`,
        // });
        getInstanceByWidgetId(this.state['child']).replaceLayoutCssProperties(
            {}
        );
    }
}
