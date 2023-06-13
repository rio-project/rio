import { WidgetBase, WidgetState } from './widgetBase';

type PlotState = WidgetState & {
    _type_: 'plot';
    htmlSource?: string;
};

export class PlotWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: PlotState): void {
        if (deltaState.htmlSource !== undefined) {
            element.innerHTML = deltaState.htmlSource;
        }
    }
}
