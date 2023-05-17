import { buildWidget } from './app';
import { JsonAlign } from './models';

export class AlignWidget {
    static build(data: JsonAlign): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('reflex-align');
        element.appendChild(buildWidget(data.child));
        return element;
    }

    static update(element: HTMLElement, state: JsonAlign): void {
        let transform_x;
        if (state.align_x !== undefined) {
            if (state.align_x === null) {
                element.style.left = 'unset';
                transform_x = '0%';
            } else {
                element.style.left = `${state.align_x * 100}%`;
                transform_x = `${state.align_x * -100}%`;
            }
        }

        let transform_y;
        if (state.align_y !== undefined) {
            if (state.align_y === null) {
                element.style.top = 'unset';
                transform_y = '0%';
            } else {
                element.style.top = `${state.align_y * 100}%`;
                transform_y = `${state.align_y * -100}%`;
            }
        }

        element.style.transform = `translate(${transform_x}, ${transform_y})`;
    }
}
