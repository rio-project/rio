import { Color } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { pixelsPerRem } from '../app';
import { LayoutContext } from '../layouting';
import { colorToCssString } from '../cssUtils';

export type SeparatorState = ComponentState & {
    _type_: 'Separator-builtin';
    orientation: 'horizontal' | 'vertical';
    color: Color;
};

export class SeparatorComponent extends ComponentBase {
    state: Required<SeparatorState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        return element;
    }

    updateElement(
        deltaState: SeparatorState,
        latentComponents: Set<ComponentBase>
    ): void {
        // Color
        if (deltaState.color === undefined) {
            // Nothing to do
        }
        // If nothing was specified, use a color from the theme
        else if (deltaState.color === null) {
            this.element.style.backgroundColor = 'var(--rio-local-text-color)';
            this.element.style.opacity = '0.3';
        }
        // Use the provided color
        else {
            this.element.style.backgroundColor = colorToCssString(
                deltaState.color
            );
            this.element.style.opacity = '1';
        }

        // Orientation
        if (deltaState.orientation !== undefined) {
            this.makeLayoutDirty();
        }
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        this.naturalWidth = 1 / pixelsPerRem;
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        this.naturalHeight = 1 / pixelsPerRem;
    }
}
