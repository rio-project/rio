import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { componentsById } from '../componentManagement';
import { LayoutContext, updateLayout } from '../layouting';
import { easeInOut } from '../easeFunctions';

const TRANSITION_TIME: number = 0.35;

export type SwitcherState = ComponentState & {
    _type_: 'Switcher-builtin';
    content?: ComponentId | null;
};

export class SwitcherComponent extends ComponentBase {
    state: Required<SwitcherState>;

    // The width and height the child requested before the animation started.
    private previousChildRequestedWidth: number = 0;
    private previousChildRequestedHeight: number = 0;

    // If true, the current layout operation isn't meant for actually laying out
    // the UI, but rather for determining which size the child will receive once
    // the animation finishes.
    private isDeterminingLayout: boolean = true;

    // The width and height the switcher was at before starting the animation.
    private initialWidth: number;
    private initialHeight: number;

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
        // Update the child
        if (
            !this.isInitialized ||
            (deltaState.content !== undefined &&
                deltaState.content !== this.state.content)
        ) {
            console.assert(deltaState.content !== undefined);

            // Out with the old
            if (this.activeChildContainer !== null) {
                this.replaceFirstChild(
                    latentComponents,
                    null,
                    this.activeChildContainer
                );
                this.activeChildContainer.remove();

                this.activeChildContainer = null;
                this.activeChildInstance = null;
            }

            // In with the new
            if (deltaState.content === null) {
                this.activeChildContainer = null;
                this.activeChildInstance = null;
            } else {
                // Add the child into a helper container
                this.activeChildContainer = document.createElement('div');
                this.activeChildContainer.style.left = '0';
                this.activeChildContainer.style.top = '0';
                this.element.appendChild(this.activeChildContainer);

                this.replaceFirstChild(
                    latentComponents,
                    deltaState.content,
                    this.activeChildContainer
                );

                // Remember the child, as it is needed frequently
                this.activeChildInstance = componentsById[deltaState.content!]!;
            }

            // Start the layouting process
            this.isDeterminingLayout = true;
            this.makeLayoutDirty();
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

        requestAnimationFrame(() => {
            this.makeLayoutDirty();
            updateLayout();
        });
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        // If the child's requested size has changed, start the animation
        // if (
        //     this.activeChildInstance !== null &&
        //     (this.previousChildRequestedWidth !==
        //         this.activeChildInstance.requestedWidth ||
        //         this.previousChildRequestedHeight !==
        //             this.activeChildInstance.requestedHeight)
        // ) {
        //     this.isDeterminingLayout = true;

        //     this.previousChildRequestedWidth =
        //         this.activeChildInstance.requestedWidth;
        //     this.previousChildRequestedHeight =
        //         this.activeChildInstance.requestedHeight;
        // }

        // Case: Trying to determine the size the child will receive once the
        // animation finishes
        if (this.isDeterminingLayout) {
            this.initialWidth = this.naturalWidth;
            this.initialHeight = this.naturalHeight;

            this.naturalWidth =
                this.activeChildInstance === null
                    ? 0
                    : this.activeChildInstance.requestedWidth;
            return;
        }

        // Case: animated layouting
        let now = Date.now();
        let linearT = Math.min(
            1,
            (now - this.animationStartedAt) / 1000 / TRANSITION_TIME
        );
        let easedT = easeInOut(linearT);

        let childRequestedWidth =
            this.activeChildInstance === null
                ? 0
                : this.activeChildInstance.requestedWidth;

        let childRequestedHeight =
            this.activeChildInstance === null
                ? 0
                : this.activeChildInstance.requestedHeight;

        this.naturalWidth =
            this.initialWidth +
            easedT * (childRequestedWidth - this.initialWidth);

        this.naturalHeight =
            this.initialHeight +
            easedT * (childRequestedHeight - this.initialHeight);

        // Keep going?
        if (linearT < 1) {
            requestAnimationFrame(() => {
                this.makeLayoutDirty();
                updateLayout();
            });
        } else {
            this.animationStartedAt = -1;
            // this.isDeterminingLayout = true;
        }
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

        // Case: animated layouting
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

        // Case: animated layouting
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

            if (this.hasBeenLaidOut) {
                if (this.animationStartedAt === -1) {
                    this.animationStartedAt = Date.now();

                    ctx.requestImmediateReLayout(() => {
                        this.makeLayoutDirty();
                    });
                }
            } else {
                this.hasBeenLaidOut = true;
            }
            return;
        }

        // Case: animated layouting
        //
        // Nothing to do here
    }
}
