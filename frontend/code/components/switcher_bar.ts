import { createUnparsedSourceFile } from 'typescript';
import { ComponentBase, ComponentState } from './componentBase';
import { MDCRipple } from '@material/ripple';
import { ColorSet } from '../models';
import { applyColorSet } from '../designApplication';
import {
    commitCss,
    disableTransitions,
    enableTransitions,
    withoutTransitions,
} from '../utils';

export type SwitcherBarState = ComponentState & {
    _type_: 'SwitcherBar-builtin';
    names?: string[];
    icon_svg_sources?: (string | null)[];
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
        if (
            deltaState.names !== undefined ||
            deltaState.icon_svg_sources !== undefined
        ) {
            let names = deltaState.names ?? this.state.names;
            let iconSvgSources =
                deltaState.icon_svg_sources ?? this.state.icon_svg_sources;
            element.innerHTML = '';

            // Iterate over both
            for (let i = 0; i < names.length; i++) {
                let name = names[i];
                let iconSvg = iconSvgSources[i];

                let outerOptionElement = document.createElement('div');
                outerOptionElement.classList.add(
                    'rio-switcher-bar-option-outer',
                    'rio-single-container'
                );
                element.appendChild(outerOptionElement);

                let innerOptionElement = document.createElement('div');
                innerOptionElement.classList.add(
                    'rio-switcher-bar-option-inner'
                );
                outerOptionElement.appendChild(innerOptionElement);

                // Icon
                let iconElement;
                if (iconSvg === null) {
                    // iconElement = document.createElement('svg');
                    // optionElement.appendChild(iconElement);
                } else {
                    innerOptionElement.innerHTML = iconSvg;
                    iconElement = innerOptionElement.children[0] as HTMLElement;
                }

                // Text
                let textElement = document.createElement('div');
                innerOptionElement.appendChild(textElement);
                textElement.textContent = name;

                // Add a ripple effect
                MDCRipple.attachTo(outerOptionElement);

                // Detect clicks
                outerOptionElement.addEventListener('click', () => {
                    this.sendMessageToBackend({
                        name: name,
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
            deltaState.names !== undefined ||
            deltaState.icon_svg_sources !== undefined
        ) {
            // What's the currently selected option?
            let selectedName =
                deltaState.selectedName ?? this.state.selectedName;
            let names = deltaState.names ?? this.state.names;
            let selectedIndex = names.indexOf(selectedName);

            // Make sure the index is valid
            if (selectedIndex == -1) {
                throw `SwitcherBar: selected option \`${selectedName}\` not found`;
            }

            // Move the marker to the correct position
            let selectedChild = element.children[selectedIndex] as HTMLElement;
            selectedChild.appendChild(this.markerElement);
            let newPos = this.markerElement.getBoundingClientRect();

            // Move it to the same location it was before reparenting
            withoutTransitions(this.markerElement, () => {
                this.markerElement.style.left = `${
                    prevPos.left - newPos.left
                }px`;
                this.markerElement.style.top = `${prevPos.top - newPos.top}px`;
                this.markerElement.style.right = `${
                    newPos.right - prevPos.right
                }px`;
                this.markerElement.style.bottom = `${
                    newPos.bottom - prevPos.bottom
                }px`;
                commitCss(this.markerElement); // Not entirely sure why this is needed
            });

            // Move it to the correct location
            this.markerElement.style.left = '';
            this.markerElement.style.top = '';
            this.markerElement.style.right = '';
            this.markerElement.style.bottom = '';
        }
    }
}
