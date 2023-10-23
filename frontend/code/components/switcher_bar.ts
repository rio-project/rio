import { createUnparsedSourceFile } from 'typescript';
import { ComponentBase, ComponentState } from './componentBase';
import { MDCRipple } from '@material/ripple';
import { ColorSet } from '../models';
import { applyColorSet } from '../designApplication';

export type SwitcherBarState = ComponentState & {
    _type_: 'SwitcherBar-builtin';
    optionNames?: string[];
    color?: ColorSet;
    orientation?: 'horizontal' | 'vertical';
    spacing?: number;
    selectedName?: string;
};

export class SwitcherBarComponent extends ComponentBase {
    state: Required<SwitcherBarState>;

    private markerElement: HTMLElement;

    _createElement(): HTMLElement {
        // Create the elements
        let element = document.createElement('div');
        element.classList.add('rio-switcher-bar');

        this.markerElement = document.createElement('div');
        this.markerElement.classList.add('rio-switcher-bar-marker');

        return element;
    }

    _updateElement(element: HTMLElement, deltaState: SwitcherBarState): void {
        // Get the marker position before any changes to the dom
        let prevPos = this.markerElement.getBoundingClientRect();

        // Update the options
        if (deltaState.optionNames !== undefined) {
            element.innerHTML = '';

            for (let optionName of deltaState.optionNames) {
                let optionElement = document.createElement('div');
                optionElement.textContent = optionName;
                element.appendChild(optionElement);

                // Add a ripple effect
                MDCRipple.attachTo(optionElement);

                // Detect clicks
                optionElement.addEventListener('click', () => {
                    this.sendMessageToBackend({
                        name: optionName,
                    });
                });
            }
        }

        // Color
        if (deltaState.color !== undefined) {
            applyColorSet(
                element,
                deltaState.color === 'keep'
                    ? 'accent-to-plain'
                    : deltaState.color
            );
        }

        // Orientation
        if (deltaState.orientation !== undefined) {
            element.style.flexDirection =
                deltaState.orientation == 'vertical' ? 'column' : 'row';
        }

        // Spacing
        if (deltaState.spacing !== undefined) {
            element.style.gap = `${deltaState.spacing}rem`;
        }

        // Place the marker at the selected option
        if (
            deltaState.selectedName !== undefined ||
            deltaState.optionNames !== undefined
        ) {
            // What's the currently selected option?
            let selectedName =
                deltaState.selectedName ?? this.state.selectedName;
            let optionNames = deltaState.optionNames ?? this.state.optionNames;
            let selectedIndex = optionNames.indexOf(selectedName);

            // Make sure the index is valid
            if (selectedIndex == -1) {
                throw `SwitcherBar: selected option ${selectedName} not found`;
            }

            // Move the marker to the correct position
            let selectedChild = element.children[selectedIndex] as HTMLElement;
            selectedChild.appendChild(this.markerElement);
            let newPos = this.markerElement.getBoundingClientRect();

            // Disable transitions
            this.markerElement.style.transition = 'none';
            element.offsetHeight;

            // Move it to the same location it was before reparenting
            this.markerElement.style.left = `${prevPos.left - newPos.left}px`;
            this.markerElement.style.top = `${prevPos.top - newPos.top}px`;
            this.markerElement.style.right = `${
                newPos.right - prevPos.right
            }px`;
            this.markerElement.style.bottom = `${
                prevPos.bottom - newPos.bottom
            }px`;
            element.offsetHeight;

            // Enable transitions again
            this.markerElement.style.transition = '';
            element.offsetHeight;

            // Move it to the correct location
            this.markerElement.style.left = '';
            this.markerElement.style.top = '';
            this.markerElement.style.right = '';
            this.markerElement.style.bottom = '';
        }
    }
}
