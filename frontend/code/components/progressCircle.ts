import { applyColorSet } from '../designApplication';
import { ColorSet } from '../models';
import { ComponentBase, ComponentState } from './componentBase';

export type ProgressCircleState = ComponentState & {
    _type_: 'progressCircle';
    color: ColorSet;
    progress?: number | null;
};

export class ProgressCircleComponent extends ComponentBase {
    state: Required<ProgressCircleState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');

        element.innerHTML = `
            <svg viewBox="25 25 50 50">
                <circle class="progress" cx="50" cy="50" r="20"></circle>
            </svg>
        `;
        element.classList.add(
            'rio-progress-circle',
            'rio-zero-size-request-container'
        );
        return element;
    }

    updateElement(element: HTMLElement, deltaState: ProgressCircleState): void {
        // Apply the progress
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

        // Apply the color
        if (deltaState.color !== undefined) {
            applyColorSet(
                element,
                deltaState.color === 'keep'
                    ? 'accent-to-plain'
                    : deltaState.color
            );
        }
    }
}
