import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { componentsById } from '../componentManagement';
import { LayoutContext } from '../layouting';
import { easeInOut } from '../easeFunctions';

const TRANSITION_TIME: number = 0.2;

export type SwitcherState = ComponentState & {
    _type_: 'Switcher-builtin';
    child?: ComponentId | null;
};

export class SwitcherComponent extends ComponentBase {
    state: Required<SwitcherState>;

    // If true, the current layout operation isn't meant for actually laying out
    // the UI, but rather for determining which size the child will receive once
    // the animation finishes.
    private isDeterminingLayout: boolean = true;

    // The width and height the switcher was at before starting the animation.
    private initialWidth: number;
    private initialHeight: number;

    // The width and height that the child will receive once the animation
    // finishes.
    private targetWidth: number;
    private targetHeight: number;

    // -1 if no animation is running
    private animationStartedAt: number = -1;

    private activeChildInstance: ComponentBase | null = null;
    private activeChildContainer: HTMLElement | null = null;

    private isInitialized: boolean = false;
    private hasBeenLaidOut: boolean = false;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-switcher');
        return element;
    }

    updateElement(
        deltaState: SwitcherState,
        latentComponents: Set<ComponentBase>
    ): void {
        // console.debug(`Switcher:`, deltaState);

        // Update the child
        if (
            !this.isInitialized ||
            (deltaState.child !== undefined &&
                deltaState.child !== this.state.child)
        ) {
            console.assert(deltaState.child !== undefined);

            // Out with the old
            if (this.activeChildContainer !== null) {
                // TODO: Animate
                this.replaceOnlyChild(
                    latentComponents,
                    null,
                    this.activeChildContainer
                );
                this.activeChildContainer = null;
                this.activeChildInstance = null;
            }

            // In with the new
            if (deltaState.child === null) {
                this.activeChildContainer = null;
                this.activeChildInstance = null;
            } else {
                // Add the child into a helper container
                this.activeChildContainer = document.createElement('div');
                this.activeChildContainer.style.left = '0';
                this.activeChildContainer.style.top = '0';
                this.element.appendChild(this.activeChildContainer);

                this.replaceOnlyChild(
                    latentComponents,
                    deltaState.child,
                    this.activeChildContainer
                );

                // TODO: Animate

                // Remember the child, as it is needed frequently
                this.activeChildInstance = componentsById[deltaState.child!]!;
            }

            // Start the layouting process
            if (this.isInitialized) {
                this.isDeterminingLayout = true;
            }
            this.makeLayoutDirty();

            // console.debug(
            //     `Switcher: ${this.state.child} -> ${deltaState.child}, ${this.isInitialized}`
            // );
        }

        // The component is now initialized
        this.isInitialized = true;
    }

    startAnimationIfNotRunning(): void {
        // Do nothing if the animation is already running
        if (this.animationStartedAt !== -1) {
            return;
        }

        this.animationStartedAt = Date.now();
        this.makeLayoutDirty();
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        // Case: Trying to determine the size the child will receive once the
        // animation finishes
        if (this.isDeterminingLayout) {
            this.initialWidth = this.allocatedWidth;
            this.initialHeight = this.allocatedHeight;

            this.naturalWidth =
                this.activeChildInstance === null
                    ? 0
                    : this.activeChildInstance.requestedWidth;
            return;
        }

        // Case: actual layouting
        let now = Date.now();
        let t = Math.min(
            1,
            (now - this.animationStartedAt) / 1000 / TRANSITION_TIME
        );
        let easedT = easeInOut(t);

        this.requestedWidth =
            this.initialWidth + easedT * (this.targetWidth - this.initialWidth);
        this.requestedHeight =
            this.initialHeight +
            easedT * (this.targetHeight - this.initialHeight);
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        // Case: Trying to determine the size the child will receive once the
        // animation finishes
        if (this.isDeterminingLayout) {
            if (this.activeChildInstance !== null) {
                this.activeChildInstance.allocatedWidth = this.allocatedWidth;
            }
            return;
        }

        // Case: actual layouting
        //
        // Nothing to do here
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        // Case: Trying to determine the size the child will receive once the
        // animation finishes
        if (this.isDeterminingLayout) {
            this.naturalHeight =
                this.activeChildInstance === null
                    ? 0
                    : this.activeChildInstance.requestedHeight;
            return;
        }

        // Case: actual layouting
        //
        // Already handled above
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Case: Trying to determine the size the child will receive once the
        // animation finishes
        if (this.isDeterminingLayout) {
            if (this.activeChildInstance !== null) {
                this.activeChildInstance.allocatedHeight = this.allocatedHeight;
            }

            this.isDeterminingLayout = false;

            this.targetWidth = this.allocatedWidth;
            this.targetHeight = this.allocatedHeight;

            if (this.hasBeenLaidOut) {
                this.startAnimationIfNotRunning();
            } else {
                this.hasBeenLaidOut = true;
            }
            return;
        }

        // Case: actual layouting
        //
        // Nothing to do here
    }
}
