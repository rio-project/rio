import { pixelsPerEm } from './app';
import {
    getChildIds,
    getElementByComponentId,
    getInstanceByElement,
} from './componentManagement';
import { ComponentBase } from './components/componentBase';
import { ComponentId } from './models';

export class LayoutContext {
    idToElement: { [id: string]: HTMLElement } = {};
    idToInstance: { [id: string]: ComponentBase } = {};

    elem(id: ComponentId): HTMLElement {
        let result = this.idToElement[id];

        if (result === undefined) {
            result = getElementByComponentId(id);
            this.idToElement[id] = result;
        }

        return result;
    }

    inst(id: ComponentId): ComponentBase {
        let result = this.idToInstance[id];

        if (result === undefined) {
            result = getInstanceByElement(this.elem(id));
            this.idToInstance[id] = result;
        }

        return result;
    }

    directChildren(component: ComponentBase): ComponentBase[] {
        return getChildIds(component.state).map(this.inst.bind(this));
    }

    private updateRequestedWidthRecursive(component: ComponentBase) {
        if (!component.layoutDirty) return;

        for (let child of this.directChildren(component)) {
            this.updateRequestedWidthRecursive(child);
            child.requestedWidth = Math.max(
                child.requestedWidth,
                child.state._size_[0]
            );
        }

        component.updateRequestedWidth(this);
    }

    private updateAllocatedWidthRecursive(component: ComponentBase) {
        if (!component.layoutDirty) return;

        let children = component.getDirectChildren();
        let childAllocatedWidths = children.map(
            (child) => child.allocatedWidth
        );

        component.updateAllocatedWidth(this);

        for (let i = 0; i < children.length; i++) {
            let child = children[i];

            if (child.allocatedWidth !== childAllocatedWidths[i]) {
                child.layoutDirty = true;
            }

            if (child.layoutDirty) {
                this.updateAllocatedWidthRecursive(child);
            }

            let element = child.element();
            element.style.width = `${child.allocatedWidth}px`;
        }
    }

    private updateRequestedHeightRecursive(component: ComponentBase) {
        if (!component.layoutDirty) return;

        for (let child of this.directChildren(component)) {
            this.updateRequestedHeightRecursive(child);
            child.requestedHeight = Math.max(
                child.requestedHeight,
                child.state._size_[1]
            );
        }

        component.updateRequestedHeight(this);
    }

    private updateAllocatedHeightRecursive(component: ComponentBase) {
        if (!component.layoutDirty) return;

        let children = this.directChildren(component);
        let childAllocatedHeights = children.map(
            (child) => child.allocatedHeight
        );

        component.updateAllocatedHeight(this);

        for (let i = 0; i < children.length; i++) {
            let child = children[i];

            if (child.allocatedHeight !== childAllocatedHeights[i]) {
                child.layoutDirty = true;
            }

            if (child.layoutDirty) {
                this.updateAllocatedHeightRecursive(child);
            }

            child.layoutDirty = false;

            let element = child.element();
            element.style.height = `${child.allocatedHeight}px`;
        }
    }

    public updateLayout() {
        let rootElement = document.body.firstElementChild as HTMLElement;
        let rootInstance = getInstanceByElement(rootElement);

        // Provide functions to quickly lookup elements & instances by component id.
        // These functions are lazy and store their results in a map for future use.
        let idToElement: { [id: string]: HTMLElement } = {};
        let idToInstance: { [id: string]: ComponentBase } = {};

        function elem(id: ComponentId): HTMLElement {
            let result = idToElement[id];

            if (result === undefined) {
                result = getElementByComponentId(id);
                idToElement[id] = result;
            }

            return result;
        }

        function inst(id: ComponentId): ComponentBase {
            let result = idToInstance[id];

            if (result === undefined) {
                result = getInstanceByElement(elem(id));
                idToInstance[id] = result;
            }

            return result;
        }

        // Find out how large all components would like to be
        this.updateRequestedWidthRecursive(rootInstance);

        // Allocate all available space to the root component, but at least as
        // much as it requested. If this is more than the window it will scroll.
        rootInstance.allocatedWidth = Math.max(
            window.innerWidth,
            rootInstance.requestedWidth * pixelsPerEm
        );

        // Distribute the just received width to all children
        this.updateAllocatedWidthRecursive(rootInstance);

        // Now that all components have their width set, find out their height.
        // This is done later on, so that text can request height based on its
        // width.
        this.updateRequestedHeightRecursive(rootInstance);

        // Once again, allocate all available space to the root component.
        rootInstance.allocatedHeight = Math.max(
            window.innerHeight,
            rootInstance.requestedHeight * pixelsPerEm
        );

        // Distribute the just received height to all children
        this.updateAllocatedHeightRecursive(rootInstance);
    }
}

export function updateLayout() {
    let context = new LayoutContext();
    context.updateLayout();
}
