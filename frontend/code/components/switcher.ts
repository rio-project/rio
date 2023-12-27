import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { componentsById, replaceOnlyChild } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { easeInOut } from '../easeFunctions';

const TRANSITION_TIME: number = 0.2;

export type SwitcherState = ComponentState & {
    _type_: 'Switcher-builtin';
    child?: ComponentId | null;
};

export class SwitcherComponent extends ComponentBase {
    state: Required<SwitcherState>;

    private animationStartedAt: number;
    private animationInitialWidth: number;
    private animationInitialHeight: number;
    private animationIsRunning: boolean = false;

    private activeChildInstance: ComponentBase | null = null;
    private activeChildContainer: HTMLElement | null = null;

    private isInitialized: boolean = false;
    private hasBeenLaidOut: boolean = false;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-switcher');
        return element;
    }

    updateElement(deltaState: SwitcherState): void {
        console.debug(
            'SwitcherComponent.updateElement',
            deltaState,
            deltaState.child,
            this.state.child
        );

        // Update the child & assign its position
        if (!this.isInitialized && deltaState.child !== null) {
            console.assert(deltaState.child !== undefined);

            this.activeChildContainer = document.createElement('div');
            this.activeChildContainer.style.left = '0';
            this.activeChildContainer.style.top = '0';
            this.element.appendChild(this.activeChildContainer);

            replaceOnlyChild(
                this.element.id,
                this.activeChildContainer,
                deltaState.child
            );

            this.activeChildInstance =
                componentsById[
                    // @ts-ignore
                    deltaState.child
                ]!;
        } else if (
            deltaState.child !== undefined &&
            deltaState.child !== this.state.child
        ) {
            console.debug('SwitcherComponent.updateElement: child changed');

            // Out with the old
            if (this.activeChildContainer !== null) {
                console.debug(
                    'SwitcherComponent.updateElement: removing old child'
                );

                // TODO: Animate
                replaceOnlyChild(
                    this.element.id,
                    this.activeChildContainer,
                    null
                );
                this.activeChildContainer = null;
                this.activeChildInstance = null;
            }

            // In with the new
            if (deltaState.child !== null) {
                console.debug('SwitcherComponent.updateElement: adding child');

                // Add the child into a helper container
                this.activeChildContainer = document.createElement('div');
                this.activeChildContainer.style.left = '0';
                this.activeChildContainer.style.top = '0';
                this.element.appendChild(this.activeChildContainer);

                replaceOnlyChild(
                    this.element.id,
                    this.activeChildContainer,
                    deltaState.child
                );

                // TODO: Animate

                // Remember the child, as it is needed frequently
                this.activeChildInstance = componentsById[deltaState.child]!;
            }

            // Start the animation. This will also update the layout
            this.startAnimationIfNotRunning();
            console.debug('starting animation from update');
        }

        // The component is now initialized
        this.isInitialized = true;
    }

    startAnimationIfNotRunning(): void {
        if (this.animationIsRunning) {
            console.debug(
                'rejecting startAnimationIfNotRunning because animationIsRunning'
            );
            return;
        }

        console.debug('starting animation from startAnimationIfNotRunning');

        this.animationStartedAt = Date.now();
        this.animationInitialWidth = this.allocatedWidth;
        this.animationInitialHeight = this.allocatedHeight;
        this.animationIsRunning = true;

        requestAnimationFrame(this.animationWorker.bind(this));
    }

    animationWorker(): void {
        console.debug('animation worker');
        // How far into the animation is it?
        let now = Date.now();
        let elapsed = (now - this.animationStartedAt) / 1000;
        let linearT = Math.min(1, elapsed / TRANSITION_TIME);
        let easedT = easeInOut(linearT);

        // Update the layout
        let targetWidth, targetHeight;
        if (this.activeChildInstance === null) {
            targetWidth = 0;
            targetHeight = 0;
        } else {
            targetWidth = this.activeChildInstance.requestedWidth;
            targetHeight = this.activeChildInstance.requestedHeight;
        }

        console.debug(
            `T: ${linearT} / ${easedT} from (${this.animationInitialWidth}, ${this.animationInitialHeight}) to (${targetWidth}, ${targetHeight})`
        );

        this.naturalWidth =
            this.animationInitialWidth +
            easedT * (targetWidth - this.animationInitialWidth);
        this.naturalHeight =
            this.animationInitialHeight +
            easedT * (targetHeight - this.animationInitialHeight);

        this.makeLayoutDirty();

        // Keep going?
        if (linearT === 1) {
            this.animationIsRunning = false;
        } else {
            requestAnimationFrame(this.animationWorker.bind(this));
        }
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        // If this is the first layout, copy the child's size
        if (!this.hasBeenLaidOut) {
            if (this.state.child === null) {
                this.naturalWidth = 0;
            } else {
                let child = componentsById[this.state.child]!;
                this.naturalWidth = child.requestedWidth;
            }
        }

        // Otherwise let the animation handle it
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        if (this.state.child !== null) {
            componentsById[this.state.child]!.allocatedWidth =
                this.allocatedWidth;
        }
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        // If this is the first layout, copy the child's size
        if (!this.hasBeenLaidOut) {
            if (this.state.child === null) {
                this.naturalHeight = 0;
            } else {
                let child = componentsById[this.state.child]!;
                this.naturalHeight = child.requestedHeight;
            }
        }

        // Otherwise let the animation handle it
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        if (this.state.child === null) {
            return;
        }

        let child = componentsById[this.state.child]!;
        child.allocatedHeight = this.allocatedHeight;

        // This component is now laid out
        this.hasBeenLaidOut = true;
    }
}
