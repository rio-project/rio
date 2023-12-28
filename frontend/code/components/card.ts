import { applyColorSet } from '../designApplication';
import { ColorSet, ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { componentsById } from '../componentManagement';
import { LayoutContext } from '../layouting';

export type CardState = ComponentState & {
    _type_: 'Card-builtin';
    child?: ComponentId;
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

    innerMarginIfEnabled: number = 0;
    effectiveInnerMargin: number = 0;

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

    updateElement(deltaState: CardState): void {
        let element = this.element;

        // Update the child
        this.replaceOnlyChild(deltaState.child);

        // Update the corner radius & inner margin
        if (deltaState.corner_radius !== undefined) {
            if (deltaState.corner_radius === null) {
                this.innerMarginIfEnabled = 1.5;
                element.style.borderRadius = '1.5rem';
            } else if (typeof deltaState.corner_radius === 'number') {
                this.innerMarginIfEnabled = deltaState.corner_radius;
                element.style.borderRadius = `${deltaState.corner_radius}rem`;
            } else {
                this.innerMarginIfEnabled = Math.max(
                    deltaState.corner_radius[0],
                    deltaState.corner_radius[1],
                    deltaState.corner_radius[2],
                    deltaState.corner_radius[3]
                );
                element.style.borderRadius = `${deltaState.corner_radius[0]}rem ${deltaState.corner_radius[1]}rem ${deltaState.corner_radius[2]}rem ${deltaState.corner_radius[3]}rem`;
            }

            this.makeLayoutDirty();
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

        // Inner margin
        if (deltaState.inner_margin === true) {
            this.effectiveInnerMargin = this.innerMarginIfEnabled;
            this.makeLayoutDirty();
        } else if (deltaState.inner_margin === false) {
            this.effectiveInnerMargin = 0;
            this.makeLayoutDirty();
        }

        // Style
        if (deltaState.color !== undefined) {
            applyColorSet(element, deltaState.color);
        }
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        if (this.state.child === null) {
            this.naturalWidth = 0;
        } else {
            this.naturalWidth =
                componentsById[this.state.child]!.requestedWidth;
        }

        this.naturalWidth += this.effectiveInnerMargin * 2;
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        if (this.state.child !== null) {
            componentsById[this.state.child]!.allocatedWidth =
                this.allocatedWidth - this.effectiveInnerMargin * 2;
        }
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        if (this.state.child === null) {
            this.naturalHeight = 0;
        } else {
            this.naturalHeight =
                componentsById[this.state.child]!.requestedHeight;
        }

        this.naturalHeight += this.effectiveInnerMargin * 2;
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        if (this.state.child === null) {
            return;
        }

        let child = componentsById[this.state.child]!;
        child.allocatedHeight =
            this.allocatedHeight - this.effectiveInnerMargin * 2;

        let element = child.element;
        element.style.left = `${this.effectiveInnerMargin}rem`;
        element.style.top = `${this.effectiveInnerMargin}rem`;
    }
}
