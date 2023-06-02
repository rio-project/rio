import { colorToCss } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type ProgressCircleState = WidgetState & {
    _type_: 'progressCircle';
    color?: [number, number, number, number];
    progress?: number | null;
};

export class ProgressCircleWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: ProgressCircleState): void {
        if (deltaState._size_ !== undefined) {
            let size = deltaState._size_[0];
            element.style.setProperty('--size', size + 'em');
        }

        if (deltaState.color !== undefined) {
            element.style.setProperty('--color', colorToCss(deltaState.color));
        }

        if (deltaState.progress === undefined) {
        } else if (deltaState.progress === null) {
            element.classList.add('reflex-progress-circle-no-progress');
        } else {
            console.log('TODO: implement progress spinner');
        }
    }
}
