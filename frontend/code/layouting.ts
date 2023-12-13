import {
    getChildIds,
    getInstanceByComponentId,
    getInstanceByElement,
} from './componentManagement';
import { ComponentBase } from './components/componentBase';

function updateRequestedWidthRecursive(component: ComponentBase) {
    if (!component.layoutDirty) return;

    component.getDirectChildren().forEach(updateRequestedWidthRecursive);
    component.updateRequestedWidth();
}

function updateAllocatedWidthRecursive(component: ComponentBase) {
    if (!component.layoutDirty) return;

    let children = component.getDirectChildren();
    let childAllocatedWidths = children.map((child) => child.allocatedWidth);

    component.updateAllocatedWidth();

    for (let i = 0; i < children.length; i++) {
        let child = children[i];

        if (child.allocatedWidth !== childAllocatedWidths[i]) {
            child.layoutDirty = true;
        }

        if (child.layoutDirty) {
            updateAllocatedWidthRecursive(child);
        }

        let element = child.element();
        element.style.width = `${child.allocatedWidth}px`;
    }
}

function updateRequestedHeightRecursive(component: ComponentBase) {
    if (!component.layoutDirty) return;

    component.getDirectChildren().forEach(updateRequestedHeightRecursive);
    component.updateRequestedHeight();
}

function updateAllocatedHeightRecursive(component: ComponentBase) {
    if (!component.layoutDirty) return;

    let children = component.getDirectChildren();
    let childAllocatedHeights = children.map((child) => child.allocatedHeight);

    component.updateAllocatedHeight();

    for (let i = 0; i < children.length; i++) {
        let child = children[i];

        if (child.allocatedHeight !== childAllocatedHeights[i]) {
            child.layoutDirty = true;
        }

        if (child.layoutDirty) {
            updateAllocatedHeightRecursive(child);
        }

        child.layoutDirty = false;

        let element = child.element();
        element.style.height = `${child.allocatedHeight}px`;
    }
}

export function updateLayout() {
    let rootElement = document.body.firstElementChild as HTMLElement;
    let rootInstance = getInstanceByElement(rootElement);

    rootInstance.allocatedWidth = window.innerWidth;
    rootInstance.allocatedHeight = window.innerHeight;

    updateRequestedWidthRecursive(rootInstance);
    updateAllocatedWidthRecursive(rootInstance);

    updateRequestedHeightRecursive(rootInstance);
    updateAllocatedHeightRecursive(rootInstance);
}
