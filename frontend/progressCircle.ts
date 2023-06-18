import { colorToCss } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type ProgressCircleState = WidgetState & {
    _type_: 'progressCircle';
    color?: [number, number, number, number];
    background_color?: [number, number, number, number];
    progress?: number | null;
};

export class ProgressCircleWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.innerHTML = `
            <svg viewBox="25 25 50 50">
                <circle class="background" cx="50" cy="50" r="20"></circle>
                <circle class="progress" cx="50" cy="50" r="20"></circle>
            </svg>
        `;
        element.classList.add('reflex-progress-circle');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: ProgressCircleState): void {
        if (deltaState.color !== undefined) {
            element.style.stroke = colorToCss(deltaState.color);
        }

        if (deltaState.background_color !== undefined) {
            element.style.setProperty(
                '--background-color',
                colorToCss(deltaState.background_color)
            );
        }

        if (deltaState.progress !== undefined) {
            if (deltaState.progress === null) {
                element.classList.add('spinning');
            } else {
                element.classList.remove('spinning');

                let fullCircle = 40 * Math.PI;
                element.style.setProperty(
                    '--dasharray',
                    `${deltaState.progress * fullCircle}, ${
                        (1 - deltaState.progress) * fullCircle
                    }`
                );
            }
        }
    }
}
