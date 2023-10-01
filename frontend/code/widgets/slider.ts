import { WidgetBase, WidgetState } from './widgetBase';
import { MDCSlider } from '@material/slider';

export type SliderState = WidgetState & {
    min?: number;
    max?: number;
    value?: number;
    is_sensitive?: boolean;
};

export class SliderWidget extends WidgetBase {
    state: Required<SliderState>;
    private mdcSlider: MDCSlider;

    createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('rio-slider', 'mdc-slider');

        element.innerHTML = `
        <input class="mdc-slider__input" type="range" min="0" max="1000" value="250">
        <div class="mdc-slider__track">
            <div class="mdc-slider__track--inactive"></div>
            <div class="mdc-slider__track--active">
                <div class="mdc-slider__track--active_fill"></div>
            </div>
        </div>
        <div class="mdc-slider__thumb">
            <div class="mdc-slider__thumb-knob"></div>
        </div>
    `;

        // Initialize the material design component
        this.mdcSlider = new MDCSlider(element);

        // Subscribe to changes
        this.mdcSlider.listen('MDCSlider:change', () => {
            let min = this.state['min'];
            let max = this.state['max'];

            console.log(`NEW VALUE: ${this.mdcSlider.getValue()}`);

            this.setStateAndNotifyBackend({
                value: (this.mdcSlider.getValue() / 1000) * (max - min),
            });
        });

        return element;
    }

    updateElement(element: HTMLElement, deltaState: SliderState): void {
        // Convert between the widget's units and the backend's.
        let min =
            deltaState.min === undefined ? this.state['min'] : deltaState.min;

        let max =
            deltaState.max === undefined ? this.state['max'] : deltaState.max;

        if (deltaState.value !== undefined) {
            this.mdcSlider.setValue((deltaState.value / (max - min)) * 1000);
        }

        if (deltaState.is_sensitive !== undefined) {
            this.mdcSlider.setDisabled(!deltaState.is_sensitive);
        }

        // The slider stores the coordinates of its rectangle. Since rio
        // likes to resize and move around widgets, the rectangle must be
        // updated appropriately.
        //
        // Really, this should be done when the widget is resized or moved, but
        // there is no hook for that. Update seems to work fine.
        requestAnimationFrame(() => {
            this.mdcSlider.layout();
        });
    }
}
