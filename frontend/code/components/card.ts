import { applyColorSet } from '../designApplication';
import { ColorSet, ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { replaceOnlyChild } from '../componentManagement';

// TODO

export type CardState = ComponentState & {
    _type_: 'Card-builtin';
    child?: ComponentId | null;
    corner_radius?: number | [number, number, number, number] | null;
    reportPress?: boolean;
    elevate_on_hover?: boolean;
    colorize_on_hover?: boolean;
    inner_margin?: boolean;
    color?: ColorSet;
};

export class CardComponent extends ComponentBase {
    state: Required<CardState>;
    marginCss: string;

    createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('rio-card');

        // Detect presses
        element.onmouseup = (e) => {
            // Is the backend interested in presses?
            if (!this.state.reportPress) {
                return;
            }

            // Otherwise notify the backend
            this.sendMessageToBackend({});
        };

        return element;
    }

    updateElement(element: HTMLElement, deltaState: CardState): void {
        // Update the child
        replaceOnlyChild(element.id, element, deltaState.child);

        // Update the corner radius & inner margin
        if (deltaState.corner_radius !== undefined) {
            if (deltaState.corner_radius === null) {
                element.style.borderRadius =
                    'var(--rio-global-corner-radius-medium)';
                this.marginCss = 'var(--rio-global-corner-radius-medium)';
            } else if (typeof deltaState.corner_radius === 'number') {
                element.style.borderRadius = `${deltaState.corner_radius}rem`;
                this.marginCss = `${deltaState.corner_radius}rem`;
            } else {
                element.style.borderRadius = `${deltaState.corner_radius[0]}em ${deltaState.corner_radius[1]}em ${deltaState.corner_radius[2]}em ${deltaState.corner_radius[3]}em`;

                let maxRadius = Math.max(
                    deltaState.corner_radius[0],
                    deltaState.corner_radius[1],
                    deltaState.corner_radius[2],
                    deltaState.corner_radius[3]
                );
                this.marginCss = `${maxRadius}rem`;
            }
        }

        // Update the inner margin
        if (deltaState.inner_margin === true) {
            element.style.padding = this.marginCss;
        } else {
            element.style.removeProperty('padding');
        }

        // Report presses?
        if (deltaState.reportPress === true) {
            element.style.cursor = 'pointer';
        } else if (deltaState.reportPress === false) {
            element.style.cursor = 'default';
        }

        // Elevate
        if (deltaState.elevate_on_hover === true) {
            element.classList.add('rio-card-elevate-on-hover');
        } else if (deltaState.elevate_on_hover === false) {
            element.classList.remove('rio-card-elevate-on-hover');
        }

        // Colorize
        if (deltaState.colorize_on_hover === true) {
            element.classList.add('rio-card-colorize-on-hover');
        } else if (deltaState.colorize_on_hover === false) {
            element.classList.remove('rio-card-colorize-on-hover');
        }

        // Style
        if (deltaState.color !== undefined) {
            applyColorSet(element, deltaState.color);
        }
    }
}
