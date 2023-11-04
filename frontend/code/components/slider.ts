import { ComponentBase, ComponentState } from './componentBase';
import { MDCSlider } from '@material/slider';

export type SliderState = ComponentState & {
    min?: number;
    max?: number;
    value?: number;
    discrete?: boolean;
    is_sensitive?: boolean;
};

export class SliderComponent extends ComponentBase {
    state: Required<SliderState>;
    private mdcSlider: MDCSlider;

    _createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('rio-slider', 'mdc-slider');

        return element;
    }

    private createMdcSlider(element: HTMLElement): void {
        // Initialize the material design component
        this.mdcSlider = new MDCSlider(element);

        // Subscribe to changes
        this.mdcSlider.listen(
            'MDCSlider:change',
            this.onSliderChange.bind(this)
        );
    }

    private onSliderChange(): void {
        let value = this.mdcSlider.getValue();

        if (!this.state.discrete) {
            let min = this.state.min;
            let max = this.state.max;

            value = min + (value / 1000) * (max - min);
        }

        this.setStateAndNotifyBackend({
            value: value,
        });
    }

    _updateElement(element: HTMLElement, deltaState: SliderState): void {
        if (deltaState.min !== undefined || deltaState.max !== undefined) {
            let min = deltaState.min ?? this.state.min;
            let max = deltaState.max ?? this.state.max;
            let value = deltaState.value ?? this.state.value;

            element.innerHTML = `
            <input class="mdc-slider__input" type="range" min="${min}" max="${max}" value="${value}">
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

            this.createMdcSlider(element);
        }

        if (deltaState.value !== undefined) {
            let value = deltaState.value;

            if (!(deltaState.discrete ?? this.state.discrete)) {
                // Convert between the component's units and the backend's.
                let min =
                    deltaState.min === undefined
                        ? this.state['min']
                        : deltaState.min;

                let max =
                    deltaState.max === undefined
                        ? this.state['max']
                        : deltaState.max;

                value = ((value - min) / (max - min)) * 1000;
            }

            this.mdcSlider.setValue(value);
        }

        if (deltaState.is_sensitive !== undefined) {
            this.mdcSlider.setDisabled(!deltaState.is_sensitive);
        }

        // The slider stores the coordinates of its rectangle. Since rio
        // likes to resize and move around components, the rectangle must be
        // updated appropriately.
        //
        // Really, this should be done when the component is resized or moved, but
        // there is no hook for that. Update seems to work fine for now.
        requestAnimationFrame(() => {
            this.mdcSlider.layout();
        });
    }
}
