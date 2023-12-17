import { MDCRipple } from '@material/ripple';
import { getInstanceByComponentId } from './componentManagement';
import { ComponentBase } from './components/componentBase';
import { FundamentalRootComponent } from './components/fundamental_root_component';
import { PlaceholderComponent } from './components/placeholder';
import { textStyleToCss } from './cssUtils';
import { applyIcon } from './designApplication';
import { Debugger } from './debugger';

export class DebuggerTree {
    public rootElement: HTMLElement;

    constructor(foo: Debugger) {
        this.rootElement = document.createElement('div');
        this.rootElement.classList.add('rio-debugger-tree-view');

        this.rootElement.innerHTML = `
            <div class="rio-debugger-header">
                Component Tree
            </div>

            <div class="rio-debugger-tree-component-tree">
                <div></div>
            </div>

            <div class="rio-debugger-tree-component-details-heading">Component Details</div>
            <div class="rio-debugger-tree-component-details"></div>
            <a class="rio-debugger-tree-component-docs-link">
                <div></div> View Documentation
            </a>
        `;

        // Header
        let header = this.rootElement.querySelector(
            '.rio-debugger-header'
        ) as HTMLElement;
        Object.assign(header.style, textStyleToCss('heading2'));

        // The tree itself
        //
        // This has a helper element to make the tree scrollable
        let treeOuter = this.rootElement.querySelector(
            '.rio-debugger-tree-component-tree'
        ) as HTMLElement;

        let treeInner = treeOuter.firstElementChild as HTMLElement;

        // Add a section to display details about the selected component
        let detailsHeading = this.rootElement.querySelector(
            '.rio-debugger-tree-component-details-heading'
        ) as HTMLElement;
        Object.assign(detailsHeading.style, textStyleToCss('heading3'));

        let details = this.rootElement.querySelector(
            '.rio-debugger-tree-component-details'
        ) as HTMLElement;
        details.textContent = 'TODO: Details';

        // Documentation link
        let docsLink = this.rootElement.querySelector(
            '.rio-debugger-tree-component-docs-link'
        ) as HTMLElement;

        applyIcon(
            docsLink.firstElementChild as HTMLElement,
            'library-books',
            'currentColor'
        );

        // Get the rootmost element. However, take care to skip the elements
        // internal to Rio.
        let highLevelRootComponent = getInstanceByComponentId(
            0
        ) as PlaceholderComponent; // TODO: Use a better method once the layouting rework is merged
        let fundamentalRootComponent = getInstanceByComponentId(
            highLevelRootComponent.state._child_
        ) as FundamentalRootComponent;
        let userRootComponent = getInstanceByComponentId(
            fundamentalRootComponent.state.child
        );

        // Build the tree
        this.makeTreeNode(treeInner, userRootComponent, 0);
    }

    highlightTreeItemAndParents(instance: ComponentBase) {
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

        // Find all tree items
        let treeItems: HTMLElement[] = [];

        let cur: HTMLElement | null = document.getElementById(
            `rio-debugger-component-tree-item-${instance.elementId}`
        ) as HTMLElement;

        console.log(
            `rio-debugger-component-tree-item-${instance.elementId}`,
            cur,
            cur.classList.contains('rio-debugger-component-tree-item')
        );

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

    makeTreeNode(
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
        let children = instance.getDirectChildren();
        let childElement = document.createElement('div');
        childElement.classList.add('rio-debugger-component-tree-item-children');
        childElement.style.marginLeft = '0.7rem';
        childElement.style.display = 'none';
        element.appendChild(childElement);

        for (let childInfo of children) {
            this.makeTreeNode(childElement, childInfo, level + 1);
        }

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

        // Toggle the children when the element is clicked
        header.addEventListener('click', (event) => {
            childElement.style.display =
                childElement.style.display === 'none' ? 'flex' : 'none';
            event.stopPropagation();
        });

        // Allow the user to select an item
        header.addEventListener('click', (event) => {
            // Highlight the tree item
            this.highlightTreeItemAndParents(instance);

            // Scroll to the element
            let componentElement = instance.element();
            componentElement.scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'center',
            });

            event.stopPropagation();
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
}
