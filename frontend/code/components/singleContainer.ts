import { ComponentBase } from './componentBase';

export abstract class SingleContainer extends ComponentBase {
    updateRequestedWidth(): void {
        this.requestedWidth = 0;

        for (let child of this.getDirectChildren()) {
            this.requestedWidth = Math.max(
                this.requestedWidth,
                child.requestedWidth
            );
        }
    }

    updateAllocatedWidth(): void {
        for (let child of this.getDirectChildren()) {
            child.allocatedWidth = this.allocatedWidth;
        }
    }

    updateRequestedHeight(): void {
        this.requestedHeight = 0;

        for (let child of this.getDirectChildren()) {
            this.requestedHeight = Math.max(
                this.requestedHeight,
                child.requestedHeight
            );
        }
    }

    updateAllocatedHeight(): void {
        for (let child of this.getDirectChildren()) {
            child.allocatedHeight = this.allocatedHeight;
        }
    }
}
