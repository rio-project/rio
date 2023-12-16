import { MDCRipple } from '@material/ripple';
import { getInstanceByComponentId } from './componentManagement';
import { ComponentBase } from './components/componentBase';
import { FundamentalRootComponent } from './components/fundamental_root_component';
import { PlaceholderComponent } from './components/placeholder';
import { textStyleToCss } from './cssUtils';
import { applyIcon } from './designApplication';

class Debugger {
    rootElement: HTMLElement;
    contentContainer: HTMLElement;

    constructor() {
        // Spawn the debugger's HTML
        this.rootElement = document.createElement('div');
        this.rootElement.classList.add('rio-debugger');
        this.rootElement.classList.add('rio-switcheroo-neutral');

        document.body.appendChild(this.rootElement);

        this.rootElement.innerHTML = `
            <div class="rio-debugger-content"></div>
            <div class="rio-debugger-navigation">
                <div class="rio-debugger-navigation-marker"></div>
                <div style="flex-grow: 1;"></div>
                <a href="https://rio.dev" target="_blank" class="rio-debugger-navigation-rio-logo">
                    <img src="/rio/asset/rio-logo.png">
                    <div>Rio</div>
                </a>
            </div>
        `;

        // Expose the elements
        this.contentContainer = this.rootElement.querySelector(
            '.rio-debugger-content'
        ) as HTMLElement;

        // Initialize the buttons, in reverse order
        this.makeNavButton('AI', 'chat-bubble:fill', 'aiChat');
        this.makeNavButton('Docs', 'library-books:fill', 'docs');
        this.makeNavButton('Stats', 'monitor-heart:fill', 'admin');
        this.makeNavButton('Tree', 'view-quilt:fill', 'componentTree');

        // For now, just show the tree view
        this.contentContainer.appendChild(this.makeTreeView());
    }

    makeNavButton(text: string, icon: string, navTarget: string) {
        // Create the element
        let navBar = this.rootElement.querySelector(
            '.rio-debugger-navigation'
        ) as HTMLElement;

        let element = document.createElement('div');
        element.classList.add('rio-debugger-navigation-button');
        navBar.insertBefore(element, navBar.firstElementChild);

        // Add the icon
        let iconElem = document.createElement('div');
        element.appendChild(iconElem);
        applyIcon(iconElem, icon, 'currentColor');

        // Add a label
        let label = document.createElement('div');
        label.textContent = text;
        element.appendChild(label);

        // MDC Ripple
        element.classList.add('mdc-ripple-surface');
        MDCRipple.attachTo(element);
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
        let childElement = document.createElement('div');
        childElement.classList.add('rio-debugger-component-tree-item-children');
        childElement.style.marginLeft = '0.7rem';
        childElement.style.display = 'none';
        element.appendChild(childElement);

        for (let childInfo of instance.getDirectChildren()) {
            this.makeTreeNode(childElement, childInfo, level + 1);
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

    makeTreeView(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-debugger-tree-view');

        element.innerHTML = `
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
        let header = element.querySelector(
            '.rio-debugger-header'
        ) as HTMLElement;
        Object.assign(header.style, textStyleToCss('heading2'));

        // The tree itself
        //
        // This has a helper element to make the tree scrollable
        let treeOuter = element.querySelector(
            '.rio-debugger-tree-component-tree'
        ) as HTMLElement;

        let treeInner = treeOuter.firstElementChild as HTMLElement;

        // Add a section to display details about the selected component
        let detailsHeading = element.querySelector(
            '.rio-debugger-tree-component-details-heading'
        ) as HTMLElement;
        Object.assign(detailsHeading.style, textStyleToCss('heading3'));

        let details = element.querySelector(
            '.rio-debugger-tree-component-details'
        ) as HTMLElement;
        details.textContent = 'TODO: Details';

        // Documentation link
        let docsLink = element.querySelector(
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

        return element;
    }
}

/// Load the debugger, display it, and expose it to the global scope
export function initializeDebugger() {
    // There mustn't be a debugger already
    if (globalThis.rioDebugger !== undefined) {
        throw new Error('The debugger was already initialized!');
    }

    // Create one
    globalThis.rioDebugger = new Debugger();
}
