import { ComponentBase, ComponentState } from './componentBase';
import { MDCSlider } from '@material/slider';

export type SliderState = ComponentState & {
    minimum?: number;
    maximum?: number;
    value?: number;
    step_size?: number;
    is_sensitive?: boolean;
};

export class SliderComponent extends ComponentBase {
    state: Required<SliderState>;
    private mdcSlider: MDCSlider;

    createElement(): HTMLElement {
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

    private onSliderChange(event: Event): void {
        console.log(event);
        let value = this.mdcSlider.getValue();

        if (value !== this.state.value) {
            this.setStateAndNotifyBackend({
                value: value,
            });
        }
    }

    updateElement(element: HTMLElement, deltaState: SliderState): void {
        if (
            deltaState.minimum !== undefined ||
            deltaState.maximum !== undefined ||
            deltaState.step_size !== undefined
        ) {
            let min = deltaState.minimum ?? this.state.minimum;
            let max = deltaState.maximum ?? this.state.maximum;
            let step = deltaState.step_size ?? this.state.step_size;
            step = step == 0 ? 0.0001 : step;
            let value = deltaState.value ?? this.state.value;

            element.innerHTML = `
            <input class="mdc-slider__input" type="range" min="${min}" max="${max}" value="${value}" step="${step}">
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

            // The server can send invalid values due to reconciliation. Fix
            // them.
            value = Math.max(value, deltaState.minimum ?? this.state.minimum);
            value = Math.min(value, deltaState.maximum ?? this.state.maximum);

            let step = deltaState.step_size ?? this.state.step_size;
            step = step == 0 ? 0.0001 : step;
            value = Math.round(value / step) * step;
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
