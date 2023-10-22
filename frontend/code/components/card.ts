import { applyColorSet } from '../designApplication';
import { ColorSetOrNull, ComponentId } from '../models';
import { ComponentState } from './componentBase';
import { SingleContainer } from './singleContainer';
import { replaceOnlyChildAndResetCssProperties } from '../componentManagement';

export type CardState = ComponentState & {
    _type_: 'Card-builtin';
    child?: ComponentId | null;
    corner_radius?: number | [number, number, number, number] | null;
    reportPress?: boolean;
    elevate_on_hover?: boolean;
    colorize_on_hover?: boolean;
    style?: ColorSetOrNull;
};

export class CardComponent extends SingleContainer {
    state: Required<CardState>;

    _createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('rio-card', 'mdc-ripple-surface');

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

    _updateElement(element: HTMLElement, deltaState: CardState): void {
        // Update the child
        replaceOnlyChildAndResetCssProperties(element, deltaState.child);

        // Update the corner radius
        if (deltaState.corner_radius !== undefined) {
            if (deltaState.corner_radius === null) {
                element.style.borderRadius =
                    'var(--rio-global-corner-radius-medium)';
            } else if (typeof deltaState.corner_radius === 'number') {
                element.style.borderRadius = `${deltaState.corner_radius}rem`;
            } else {
                element.style.borderRadius = `${deltaState.corner_radius[0]}em ${deltaState.corner_radius[1]}em ${deltaState.corner_radius[2]}em ${deltaState.corner_radius[3]}em`;
            }
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
        if (deltaState.style !== undefined) {
            applyColorSet(element, deltaState.style);
        }
    }
}
