import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { getInstanceByElement, replaceOnlyChild } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { easeInOut } from '../easeFunctions';

const TRANSITION_TIME: number = 0.2;

export type SwitcherState = ComponentState & {
    _type_: 'Switcher-builtin';
    child?: ComponentId;
};

export class SwitcherComponent extends ComponentBase {
    state: Required<SwitcherState>;

    private animationStartedAt: number;
    private animationInitialWidth: number;
    private animationInitialHeight: number;
    private animationIsRunning: boolean = false;

    private isInitialized: boolean = false;

    private childInstance: ComponentBase;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-switcher');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: SwitcherState): void {
        // Update the child & assign its position
        if (deltaState.child !== this.state.child) {
            // Add the child into a helper container
            let childContainer = document.createElement('div');
            element.appendChild(childContainer);

            replaceOnlyChild(element.id, childContainer, deltaState.child);

            // Position it
            let childElement = childContainer.firstElementChild as HTMLElement;
            childElement.style.left = '0';
            childElement.style.top = '0';

            // Remember the child, as it is needed frequently
            this.childInstance = getInstanceByElement(childElement);

            // Start the animation. This will also update the layout
            if (this.isInitialized) {
                this.startAnimationIfNotRunning();
            } else {
                this.makeLayoutDirty();
            }
        }
    }

    startAnimationIfNotRunning(): void {
        if (this.animationIsRunning) {
            return;
        }

        this.animationStartedAt = Date.now();
        this.animationInitialWidth = this.allocatedWidth;
        this.animationInitialHeight = this.allocatedHeight;
        this.animationIsRunning = true;

        requestAnimationFrame(this.animationWorker.bind(this));
    }

    animationWorker(): void {
        // How far into the animation is it?
        let now = Date.now();
        let elapsed = (now - this.animationStartedAt) / 1000;
        let linearT = Math.min(1, elapsed / TRANSITION_TIME);
        let easedT = easeInOut(linearT);

        // Update the layout
        this.naturalWidth =
            this.animationInitialWidth +
            (this.childInstance.requestedWidth - this.animationInitialWidth) *
                easedT;
        this.naturalHeight =
            this.animationInitialHeight +
            (this.childInstance.requestedHeight - this.animationInitialHeight) *
                easedT;
        this.makeLayoutDirty();

        // Keep going?
        if (linearT === 1) {
            this.animationIsRunning = false;
        } else {
            requestAnimationFrame(this.animationWorker.bind(this));
        }
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        // Updated by the animation
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        ctx.inst(this.state.child).allocatedWidth = this.allocatedWidth;
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        // Updated by the animation
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        ctx.inst(this.state.child).allocatedHeight = this.allocatedHeight;
    }
}
