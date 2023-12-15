import { LayoutContext } from '../layouting';
import { ComponentBase } from './componentBase';

export abstract class SingleContainer extends ComponentBase {
    updateRequestedWidth(ctx: LayoutContext): void {
        this.requestedWidth = 0;

        for (let child of ctx.directChildren(this)) {
            this.requestedWidth = Math.max(
                this.requestedWidth,
                child.requestedWidth
            );
        }
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        for (let child of ctx.directChildren(this)) {
            child.allocatedWidth = this.allocatedWidth;
        }
    }

    updateRequestedHeight(ctx: LayoutContext): void {
        this.requestedHeight = 0;

        for (let child of ctx.directChildren(this)) {
            this.requestedHeight = Math.max(
                this.requestedHeight,
                child.requestedHeight
            );
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        for (let child of ctx.directChildren(this)) {
            child.allocatedHeight = this.allocatedHeight;

            let element = child.element();
            element.style.left = '0';
            element.style.top = '0';
        }
    }
}
