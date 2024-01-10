import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { SingleContainer } from './singleContainer';

export type TooltipState = ComponentState & {
    _type_: 'Tooltip-builtin';
    anchor?: ComponentId;
    label?: string;
    position?: 'left' | 'top' | 'right' | 'bottom';
};

export class TooltipComponent extends SingleContainer {
    state: Required<TooltipState>;

    private anchorContainer: HTMLElement;
    private labelElement: HTMLElement;

    createElement(): HTMLElement {
        // Set up the HTML
        let element = document.createElement('div');
        element.classList.add('rio-tooltip');

        element.innerHTML = `
            <div class="rio-tooltip-anchor"></div>
            <div class="rio-tooltip-label"></div>
        `;

        this.anchorContainer = element.querySelector(
            '.rio-tooltip-anchor'
        ) as HTMLElement;

        this.labelElement = element.querySelector(
            '.rio-tooltip-label'
        ) as HTMLElement;

        // Listen for events
        this.anchorContainer.addEventListener('mouseover', () => {
            this.labelElement.style.opacity = '0.8';
        });

        this.anchorContainer.addEventListener('mouseout', () => {
            this.labelElement.style.opacity = '0';
        });

        return element;
    }

    updateElement(
        deltaState: TooltipState,
        latentComponents: Set<ComponentBase>
    ): void {
        // Update the child
        if (deltaState.anchor !== undefined) {
            this.replaceOnlyChild(
                latentComponents,
                deltaState.anchor,
                this.anchorContainer
            );
        }

        // Update the label
        if (deltaState.label !== undefined) {
            this.labelElement.textContent = deltaState.label;
        }

        // Position
        if (deltaState.position !== undefined) {
            let left, top, right, bottom, transform;

            const theOne = 'calc(100% + 1rem)';

            if (deltaState.position === 'left') {
                left = 'unset';
                top = '50%';
                right = theOne;
                bottom = 'unset';
                transform = 'translateY(-50%)';
            } else if (deltaState.position === 'top') {
                left = '50%';
                top = 'unset';
                right = 'unset';
                bottom = theOne;
                transform = 'translateX(-50%)';
            } else if (deltaState.position === 'right') {
                left = theOne;
                top = '50%';
                right = 'unset';
                bottom = 'unset';
                transform = 'translateY(-50%)';
            } else {
                left = '50%';
                top = theOne;
                right = 'unset';
                bottom = 'unset';
                transform = 'translateX(-50%)';
            }

            this.labelElement.style.left = left;
            this.labelElement.style.top = top;
            this.labelElement.style.right = right;
            this.labelElement.style.bottom = bottom;
            this.labelElement.style.transform = transform;
        }
    }
}
