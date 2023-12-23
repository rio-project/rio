import {
    getInstanceByComponentId,
    getRootInstance,
    tryGetInstanceByElement,
} from '../componentManagement';
import { applyIcon } from '../designApplication';
import { ComponentBase, ComponentState } from './componentBase';

export type ComponentTreeState = ComponentState & {
    _type_: 'ComponentTree-builtin';
};

var selectedElementId: string | null = null;

export class ComponentTreeComponent extends ComponentBase {
    state: Required<ComponentTreeState>;

    createElement(): HTMLElement {
        // Spawn the HTML
        let element = document.createElement('div');
        element.classList.add('.rio-debugger-tree-component-tree');

        // Populate. This needs to lookup the root component, which isn't in the
        // tree yet.
        requestAnimationFrame(() => {
            this.buildTree();
        });

        return element;
    }

    updateElement(element: HTMLElement, deltaState: ComponentState): void {}

    /// Returns the currently selected component. This will impute a sensible
    /// default if the selected component no longer exists.
    getSelectedComponent(): ComponentBase {
        // Does the previously selected component still exist?
        let element: HTMLElement | null = null;
        if (selectedElementId !== null) {
            element = document.getElementById(selectedElementId);
        }

        let selectedComponent: ComponentBase | null = null;
        if (element !== null) {
            selectedComponent = tryGetInstanceByElement(element);
        }

        if (selectedComponent !== null) {
            return selectedComponent;
        }

        // Default to the root
        let result = this.getDisplayedRootComponent();
        this.setSelectedComponent(result);
        return result;
    }

    /// Stores the currently selected component, without updating any UI
    setSelectedComponent(component: ComponentBase) {
        selectedElementId = component.elementId;
    }

    /// Many of the spawned components are internal to Rio and shouldn't be
    /// displayed to the user. This function makes that determination.
    shouldDisplayComponent(comp: ComponentBase): boolean {
        // Root components
        // TODO: Are these needed?
        // if (comp.state._python_type_ === 'HighLevelRootComponent') {
        //     return false;
        // }

        //     if (comp instanceof FundamentalRootComponent) {
        //         return false;
        // }

        // Use the component's annotation
        return !comp.state._rio_internal_;
    }

    _drillDown(comp: ComponentBase): ComponentBase[] {
        // Is this component displayable?
        if (this.shouldDisplayComponent(comp)) {
            return [comp];
        }

        // No, drill down
        let result: ComponentBase[] = [];

        for (let child of comp.getDirectChildren()) {
            result.push(...this._drillDown(child));
        }

        return result;
    }

    /// Given a component, return all of its children which should be displayed
    /// in the tree.
    getDisplayableChildren(comp: ComponentBase): ComponentBase[] {
        let allChildren = comp.getDirectChildren();
        let result: ComponentBase[] = [];

        // Keep drilling down until a component which should be displayed
        // is encountered
        for (let child of allChildren) {
            result.push(...this._drillDown(child));
        }

        return result;
    }

    /// Return the root component, but take care to discard any rio internal
    /// components.
    getDisplayedRootComponent(): ComponentBase {
        let actualRoot = getRootInstance();
        let userRoot = getInstanceByComponentId(actualRoot.state.child);
        return userRoot;
    }

    buildTree() {
        // Get the rootmost displayed component
        let rootComponent = this.getDisplayedRootComponent();

        // Clear the tree
        let element = this.element();
        element.innerHTML = '';

        // Build a fresh one
        this.buildNode(element, rootComponent, 0);

        // Attempting to immediately access the just spawned items fails,
        // apparently because the browser needs to get control first. Any
        // further actions will happen with a delay.

        setTimeout(() => {
            // Don't start off with a fully collapsed tree
            if (!this.getNodeExpanded(rootComponent)) {
                this.setNodeExpanded(rootComponent, true);
            }

            // Highlight the selected component
            this.highlightSelectedComponent();
        }, 0);
    }

    buildNode(
        parentElement: HTMLElement,
        instance: ComponentBase,
        level: number
    ) {
        // Create the element for this item
        let element = document.createElement('div');
        element.id = `rio-debugger-component-tree-item-${instance.elementId}`;
        element.classList.add('rio-debugger-component-tree-item');
        parentElement.appendChild(element);

        // Create the header
        let header = document.createElement('div');
        header.classList.add('rio-debugger-component-tree-item-header');
        header.textContent = instance.state._python_type_;
        element.appendChild(header);

        // Add the children
        let children = this.getDisplayableChildren(instance);
        let childElement = document.createElement('div');
        childElement.classList.add('rio-debugger-component-tree-item-children');
        childElement.style.marginLeft = '0.7rem';
        element.appendChild(childElement);

        for (let childInfo of children) {
            this.buildNode(childElement, childInfo, level + 1);
        }

        // Expand the node, or not
        let expanded = this.getNodeExpanded(instance);
        childElement.style.display = expanded ? 'flex' : 'none';

        // Add icons to give additional information
        let icons: string[] = [];

        // Icon: Container
        if (children.length <= 1) {
        } else if (children.length > 9) {
            icons.push('filter-9-plus');
        } else {
            icons.push(`filter-${children.length}`);
        }

        // Icon: Key
        if (instance.state._key_ !== null) {
            icons.push('key');
        }

        let spacer = document.createElement('div');
        spacer.style.flexGrow = '1';
        header.appendChild(spacer);

        for (let icon of icons) {
            let iconElement = document.createElement('div');
            header.appendChild(iconElement);
            applyIcon(iconElement, icon, 'currentColor');
        }

        // Click...
        header.addEventListener('click', (event) => {
            event.stopPropagation();

            // Select the component
            this.setSelectedComponent(instance);

            // Highlight the tree item
            this.highlightSelectedComponent();

            // Expand / collapse the node's children
            let expanded = this.getNodeExpanded(instance);
            this.setNodeExpanded(instance, !expanded);

            // Scroll to the element
            let componentElement = instance.element();
            componentElement.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'nearest',
            });
        });

        // Highlight the actual component when the element is hovered
        header.addEventListener('mouseover', (event) => {
            // Get the element for this instance
            let componentElement = instance.element();
            let rect = componentElement.getBoundingClientRect();

            // Highlight the component
            let highlighter = document.createElement('div');
            highlighter.classList.add('rio-debugger-component-highlighter');
            highlighter.style.top = `${rect.top}px`;
            highlighter.style.left = `${rect.left}px`;
            highlighter.style.width = `${rect.width}px`;
            highlighter.style.height = `${rect.height}px`;
            document.body.appendChild(highlighter);

            event.stopPropagation();
        });

        // Remove any highlighters when the element is unhovered
        element.addEventListener('mouseout', (event) => {
            for (let highlighter of document.getElementsByClassName(
                'rio-debugger-component-highlighter'
            )) {
                highlighter.remove();
            }

            event.stopPropagation();
        });
    }

    getNodeExpanded(instance: ComponentBase): boolean {
        // This is monkey-patched directly in the instance to preserve it across
        // debugger rebuilds.

        // @ts-ignore
        return instance._rio_debugger_expanded_ === true;
    }

    setNodeExpanded(
        instance: ComponentBase,
        expanded: boolean,
        allowRecursion: boolean = true
    ) {
        // Monkey-patch the new value in the instance
        // @ts-ignore
        instance._rio_debugger_expanded_ = expanded;

        // Get the node element for this instance
        let element = document.getElementById(
            `rio-debugger-component-tree-item-${instance.elementId}`
        );

        // Expand / collapse its children.
        //
        // Only do so if there are children, as the additional empty spacing
        // looks dumb otherwise.
        let children = this.getDisplayableChildren(instance);

        if (element !== null) {
            let childrenElement = element.lastChild as HTMLElement;
            childrenElement.style.display =
                expanded && children.length > 0 ? 'flex' : 'none';
        }

        // If expanding, and the node only has a single child, expand that child
        // as well
        if (allowRecursion && expanded) {
            if (children.length === 1) {
                this.setNodeExpanded(children[0], true);
            }
        }
    }

    highlightSelectedComponent() {
        // Unhighlight all previously highlighted items
        for (let element of Array.from(
            document.querySelectorAll(
                '.rio-debugger-component-tree-item-header-weakly-selected, .rio-debugger-component-tree-item-header-strongly-selected'
            )
        )) {
            element.classList.remove(
                'rio-debugger-component-tree-item-header-weakly-selected',
                'rio-debugger-component-tree-item-header-strongly-selected'
            );
        }

        // Get the selected component
        let selectedInstance = this.getSelectedComponent();

        // Find all tree items
        let treeItems: HTMLElement[] = [];

        let cur: HTMLElement | null = document.getElementById(
            `rio-debugger-component-tree-item-${selectedInstance.elementId}`
        ) as HTMLElement;

        while (
            cur !== null &&
            cur.classList.contains('rio-debugger-component-tree-item')
        ) {
            treeItems.push(cur.firstElementChild as HTMLElement);
            cur = cur.parentElement!.parentElement;
        }

        // Strongly select the leafmost item
        treeItems[0].classList.add(
            'rio-debugger-component-tree-item-header-strongly-selected'
        );

        // Weakly select the rest
        for (let i = 1; i < treeItems.length; i++) {
            treeItems[i].classList.add(
                'rio-debugger-component-tree-item-header-weakly-selected'
            );
        }
    }

    public afterComponentStateChange(deltaStates: {
        [key: string]: { [key: string]: any };
    }) {
        // Some components have had their state changed. This may affect the
        // tree, as their children may have changed.
        //
        // Rebuild the tree
        this.buildTree();

        // The component tree has been modified. Browsers struggle to retrieve
        // the new elements immediately, so wait a bit.
        setTimeout(() => {
            // Flash all changed components
            for (let componentId in deltaStates) {
                // Get the element. Not everything will show up, since some
                // components aren't displayed in the tree (internals).
                let element = document.getElementById(
                    `rio-debugger-component-tree-item-rio-id-${componentId}`
                );

                if (element === null) {
                    continue;
                }

                let elementHeader = element.firstElementChild as HTMLElement;

                // Flash the font to indicate a change
                elementHeader.classList.add(
                    'rio-debugger-component-tree-flash'
                );

                setTimeout(() => {
                    elementHeader.classList.remove(
                        'rio-debugger-component-tree-flash'
                    );
                }, 5000);
            }
        }, 0);
    }
}
