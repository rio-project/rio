import { replaceOnlyChild } from '../componentManagement';
import { applyIcon } from '../designApplication';
import { easeInOut } from '../easeFunctions';
import { getTextDimensions } from '../layoutHelpers';
import { LayoutContext, updateLayout } from '../layouting';
import { ComponentBase, ComponentState } from './componentBase';

// Height of the revealer's header in rem
const HEADER_HEIGHT = 2.6;
const CHILD_PADDING = 0.8;

export type RevealerState = ComponentState & {
    _type_: 'Revealer-builtin';
    header?: string | null;
    content?: number | string;
    is_open: boolean;
};

export class RevealerComponent extends ComponentBase {
    state: Required<RevealerState>;

    // Tracks the progress of the animation. Zero means fully collapsed, one
    // means fully expanded.
    private animationIsRunning: boolean = false;
    private lastAnimationTick: number;
    private openFractionBeforeEase: number = -1; // Initialized on first state update

    private headerElement: HTMLElement;
    private labelElement: HTMLElement;
    private arrowElement: HTMLElement;
    private contentInnerElement: HTMLElement;
    private contentOuterElement: HTMLElement;

    createElement(): HTMLElement {
        // Create the HTML
        let element = document.createElement('div');
        element.classList.add('rio-revealer');

        element.innerHTML = `
            <div class="rio-revealer-header">
                <div class="rio-revealer-label"></div>
                <div class="rio-revealer-arrow"></div>
            </div>
            <div class="rio-revealer-content-outer">
                <div class="rio-revealer-content-inner"></div>
            </div>
`;

        // Expose the elements
        this.headerElement = element.querySelector(
            '.rio-revealer-header'
        ) as HTMLElement;

        this.labelElement = this.headerElement.querySelector(
            '.rio-revealer-label'
        ) as HTMLElement;

        this.arrowElement = this.headerElement.querySelector(
            '.rio-revealer-arrow'
        ) as HTMLElement;

        this.contentInnerElement = element.querySelector(
            '.rio-revealer-content-inner'
        ) as HTMLElement;

        this.contentOuterElement = element.querySelector(
            '.rio-revealer-content-outer'
        ) as HTMLElement;

        // Initialize them
        this.headerElement.style.height = `${HEADER_HEIGHT}rem`;

        applyIcon(
            this.arrowElement,
            'expand-more',
            'var(--rio-local-text-color)'
        );

        this.contentInnerElement.style.padding = `${CHILD_PADDING}rem`;

        // Listen for presses
        this.headerElement.onmouseup = (e) => {
            // Toggle the open state
            this.state.is_open = !this.state.is_open;

            // Notify the backend
            this.setStateAndNotifyBackend({
                is_open: this.state.is_open,
            });

            // Update the UI
            this.startAnimationIfNotRunning();
        };

        return element;
    }

    updateElement(element: HTMLElement, deltaState: RevealerState): void {
        // Update the header
        if (deltaState.header === null) {
            this.headerElement.style.display = 'none';
        } else if (deltaState.header !== undefined) {
            this.headerElement.style.removeProperty('display');
            this.labelElement.textContent = deltaState.header;
        }

        // Update the child
        replaceOnlyChild(
            element.id,
            this.contentInnerElement,
            deltaState.content
        );

        // Expand / collapse
        if (deltaState.is_open !== undefined) {
            // If this is the first state update, initialize the open fraction
            if (this.openFractionBeforeEase === -1) {
                this.openFractionBeforeEase = deltaState.is_open ? 1 : 0;
                // this.arrowElement.style.transform = `rotate(${
                //     this.state.is_open ? 0 : 90
                // }deg)`;
            }
            // Otherwise animate
            else {
                this.state.is_open = deltaState.is_open;
                this.startAnimationIfNotRunning();
            }

            // Update the CSS
            if (this.state.is_open) {
                element.classList.add('rio-revealer-open');
            } else {
                element.classList.remove('rio-revealer-open');
            }
        }

        // Re-layout
        this.makeLayoutDirty();
    }

    /// If the animation is not yet running, start it. Does nothing otherwise.
    /// This does not modify the state in any way.
    startAnimationIfNotRunning() {
        // If the animation is already running, do nothing.
        if (this.animationIsRunning) {
            return;
        }

        // Start the animation
        this.animationIsRunning = true;
        this.lastAnimationTick = Date.now();
        requestAnimationFrame(() => this.animationWorker());
    }

    animationWorker() {
        // Update state
        let now = Date.now();
        let timePassed = now - this.lastAnimationTick;
        this.lastAnimationTick = now;

        let direction = this.state.is_open ? 1 : -1;
        this.openFractionBeforeEase =
            this.openFractionBeforeEase + (direction * timePassed) / 200;

        // Clamp the open fraction
        this.openFractionBeforeEase = Math.max(
            0,
            Math.min(1, this.openFractionBeforeEase)
        );

        // // Rotate the arrow
        // let t = easeInOut(this.openFractionBeforeEase);
        // let oneMinusT = 1 - t;
        // let angle = oneMinusT * 90;
        // this.arrowElement.style.transform = `rotate(${angle}deg)`;

        // // Move the content
        // this.contentInnerElement.style.transform = `translateY(${
        //     -oneMinusT * 30
        // }%)`;
        // this.contentInnerElement.style.opacity = t.toString();

        // Re-layout
        this.makeLayoutDirty();
        updateLayout();

        // If the animation is not yet finished, continue it.
        if (
            this.openFractionBeforeEase === 0 ||
            this.openFractionBeforeEase === 1
        ) {
            this.animationIsRunning = false;
        } else {
            requestAnimationFrame(() => this.animationWorker());
        }
    }

    updateRequestedWidth(ctx: LayoutContext): void {
        // Account for the content
        this.requestedWidth =
            ctx.inst(this.state.content).requestedWidth + 2 * CHILD_PADDING;

        // If a header is present, consider that as well
        if (this.state.header !== null) {
            let headerWidth =
                getTextDimensions(this.state.header, 'text')[0] + 3;

            this.requestedWidth = Math.max(this.requestedWidth, headerWidth);
        }
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        // Pass on space to the child, but only if the revealer is open. If not,
        // avoid forcing a re-layout of the child.
        if (this.state.is_open) {
            ctx.inst(this.state.content).allocatedWidth =
                this.allocatedWidth - 2 * CHILD_PADDING;
        }
    }

    updateRequestedHeight(ctx: LayoutContext): void {
        this.requestedHeight = 0;

        // Account for the header, if present
        if (this.state.header !== null) {
            this.requestedHeight += HEADER_HEIGHT;
        }

        // Account for the content
        if (this.openFractionBeforeEase > 0) {
            let t = easeInOut(this.openFractionBeforeEase);
            let innerHeight =
                ctx.inst(this.state.content).requestedHeight +
                2 * CHILD_PADDING;

            this.requestedHeight += t * innerHeight;
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Avoid forcing a re-layout of the child if the revealer is closed.
        if (this.openFractionBeforeEase === 0) {
            return;
        }

        // Pass on space to the child
        let headerHeight = this.state.header === null ? 0 : HEADER_HEIGHT;

        ctx.inst(this.state.content).allocatedHeight = Math.max(
            this.allocatedHeight - headerHeight - 2 * CHILD_PADDING,
            ctx.inst(this.state.content).requestedHeight
        );

        // Position the child
        let element = ctx.elem(this.state.content);
        element.style.left = '0';
        element.style.top = '0';
    }
}
