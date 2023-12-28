import { pixelsPerEm } from './app';
import { getRootComponent } from './componentManagement';
import { ComponentBase } from './components/componentBase';

export class LayoutContext {
    private updateRequestedWidthRecursive(component: ComponentBase) {
        if (!component.isLayoutDirty) return;

        for (let child of component.children) {
            this.updateRequestedWidthRecursive(child);
        }

        component.updateNaturalWidth(this);
        component.requestedWidth = Math.max(
            component.naturalWidth,
            component.state._size_[0]
        );

        // TODO / REMOVEME For debugging
        component.element.setAttribute(
            'dbg-requested-width',
            `${component.requestedWidth}`
        );
    }

    private updateAllocatedWidthRecursive(component: ComponentBase) {
        if (!component.isLayoutDirty) return;

        let children = Array.from(component.children);
        let childAllocatedWidths = children.map(
            (child) => child.allocatedWidth
        );

        component.updateAllocatedWidth(this);

        for (let i = 0; i < children.length; i++) {
            let child = children[i];

            if (child.allocatedWidth !== childAllocatedWidths[i]) {
                child.isLayoutDirty = true;
            }

            if (child.isLayoutDirty) {
                this.updateAllocatedWidthRecursive(child);
            }

            let element = child.element;
            element.style.width = `${child.allocatedWidth * pixelsPerEm}px`;
        }
    }

    private updateRequestedHeightRecursive(component: ComponentBase) {
        if (!component.isLayoutDirty) return;

        for (let child of component.children) {
            this.updateRequestedHeightRecursive(child);
        }

        component.updateNaturalHeight(this);
        component.requestedHeight = Math.max(
            component.naturalHeight,
            component.state._size_[1]
        );

        // TODO / REMOVEME For debugging
        component.element.setAttribute(
            'dbg-requested-height',
            `${component.requestedHeight}`
        );
    }

    private updateAllocatedHeightRecursive(component: ComponentBase) {
        if (!component.isLayoutDirty) return;

        let children = Array.from(component.children);
        let childAllocatedHeights = children.map(
            (child) => child.allocatedHeight
        );

        component.updateAllocatedHeight(this);

        for (let i = 0; i < children.length; i++) {
            let child = children[i];

            if (child.allocatedHeight !== childAllocatedHeights[i]) {
                child.isLayoutDirty = true;
            }

            if (child.isLayoutDirty) {
                this.updateAllocatedHeightRecursive(child);
            }

            child.isLayoutDirty = false;

            let element = child.element;
            element.style.height = `${child.allocatedHeight * pixelsPerEm}px`;
        }
    }

    public updateLayout() {
        let rootComponent = getRootComponent();

        // Find out how large all components would like to be
        this.updateRequestedWidthRecursive(rootComponent);

        // Note: The FundamentalRootComponent is responsible for allocating the
        // available window space. There is no need to take care of anything
        // here.

        // Distribute the just received width to all children
        this.updateAllocatedWidthRecursive(rootComponent);

        // Now that all components have their width set, find out their height.
        // This is done later on, so that text can request height based on its
        // width.
        this.updateRequestedHeightRecursive(rootComponent);

        // Distribute the just received height to all children
        this.updateAllocatedHeightRecursive(rootComponent);
    }
}

export function updateLayout() {
    let context = new LayoutContext();
    context.updateLayout();
}
