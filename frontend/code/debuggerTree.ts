import { pixelsPerEm } from './app';
import {
    getInstanceByComponentId,
    tryGetInstanceByElement,
} from './componentManagement';
import { ComponentBase } from './components/componentBase';
import { FundamentalRootComponent } from './components/fundamental_root_component';
import { PlaceholderComponent } from './components/placeholder';
import { textStyleToCss } from './cssUtils';
import { applyIcon } from './designApplication';
import { ComponentId } from './models';

export class DebuggerTreeDriver {
    public rootElement: HTMLElement;

    private treeElement: HTMLElement;
    private componentNameElement: HTMLElement;
    private componentKeyContainerElement: HTMLElement;
    private componentKeyTextElement: HTMLElement;
    private componentDetailsElement: HTMLElement;
    private docsLinkElement: HTMLElement;

    constructor() {
        // Set up the HTML
        this.rootElement = document.createElement('div');
        this.rootElement.classList.add('rio-debugger-tree-view');

        this.rootElement.innerHTML = `
            <div class="rio-debugger-header">
                Component Tree
            </div>

            <div class="rio-debugger-tree-component-tree">
                <div></div>
            </div>

            <div class="rio-debugger-tree-component-details-heading">
                <div>Component Name</div>
                <div style="flex-grow: 1"></div>
                <div class="rio-debugger-tree-component-details-key-container">
                    <div>KeyIcon</div>
                    <div>Key</div>
                </div>
            </div>
            <div class="rio-debugger-tree-component-details"></div>
            <a class="rio-debugger-tree-component-docs-link rio-link">
                <div></div> Documentation
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

        this.treeElement = treeOuter.firstElementChild as HTMLElement;
        this.buildTree();

        // Add a section to display details about the selected component
        let detailsHeading = this.rootElement.querySelector(
            '.rio-debugger-tree-component-details-heading'
        ) as HTMLElement;

        this.componentNameElement =
            detailsHeading.firstElementChild as HTMLElement;
        this.componentKeyContainerElement = detailsHeading.querySelector(
            '.rio-debugger-tree-component-details-key-container'
        ) as HTMLElement;
        let keyIconElement = this.componentKeyContainerElement
            .firstElementChild as HTMLElement;
        this.componentKeyTextElement = this.componentKeyContainerElement
            .lastElementChild as HTMLElement;

        Object.assign(
            this.componentNameElement.style,
            textStyleToCss('heading3')
        );
        Object.assign(
            this.componentKeyContainerElement.style,
            textStyleToCss('dim')
        );
        applyIcon(keyIconElement, 'key', 'currentColor');

        this.componentDetailsElement = this.rootElement.querySelector(
            '.rio-debugger-tree-component-details'
        ) as HTMLElement;

        this.docsLinkElement = this.rootElement.querySelector(
            '.rio-debugger-tree-component-docs-link'
        ) as HTMLElement;

        this.buildDetails();

        applyIcon(
            this.docsLinkElement.firstElementChild as HTMLElement,
            'library-books',
            'currentColor'
        );
    }

    /// Returns the currently selected component. This will impute a sensible
    /// default if the selected component no longer exists.
    getSelectedComponent(): ComponentBase {
        // Get the previously selected component id from session storage
        let selectedElementId = sessionStorage.getItem(
            'rio-debugger-tree-selected-element-id'
        );

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

    /// Stores the currently selected component in session storage
    setSelectedComponent(component: ComponentBase) {
        sessionStorage.setItem(
            'rio-debugger-tree-selected-element-id',
            component.elementId
        );
    }

    /// Many of the spawned components are internal to Rio and shouldn't be
    /// displayed to the user. This function makes that determination.
    shouldDisplayComponent(comp: ComponentBase): boolean {
        // Root components
        if (comp.state._python_type_ === 'HighLevelRootComponent') {
            return false;
        }

        if (comp instanceof FundamentalRootComponent) {
            return false;
        }

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
        // TODO: Use a better method once the layouting rework is merged
        let actualRoot = getInstanceByComponentId(0);

        // Drill down until a displayable component is found
        let children = this.getDisplayableChildren(actualRoot);

        // There should be exactly two - the user's app, as well as the
        // connection lost popup.
        if (children.length !== 2) {
            throw new Error(
                `Expected exactly two root components, got ${children.length}`
            );
        }

        return children[0];
    }

    buildTree() {
        // Get the rootmost displayed component
        let rootComponent = this.getDisplayedRootComponent();

        // Clear the tree
        this.treeElement.innerHTML = '';

        // Build a fresh one
        this.buildNode(this.treeElement, rootComponent, 0);

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

            // Update the selected component details
            this.buildDetails();

            // Highlight the tree item
            this.highlightSelectedComponent();

            // Expand / collapse the node's children
            let expanded = this.getNodeExpanded(instance);
            this.setNodeExpanded(instance, !expanded);

            // Scroll to the element
            let componentElement = instance.element();
            componentElement.scrollIntoView({
                behavior: 'smooth',
                block: 'center',
                inline: 'center',
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

    buildDetails() {
        // A component must be selected
        let selectedComponent = this.getSelectedComponent();

        // Update the heading
        this.componentNameElement.textContent =
            selectedComponent.state._python_type_;

        // Update the key
        if (selectedComponent.state._key_ === null) {
            this.componentKeyContainerElement.style.display = 'none';
        } else {
            this.componentKeyContainerElement.style.removeProperty('display');
            this.componentKeyTextElement.textContent =
                selectedComponent.state._key_;
        }

        // Fill in the details
        this.componentDetailsElement.innerHTML = '';
        let rowIndex = 1;

        let makeCell = (
            column: number,
            width: number,
            content: string | HTMLElement,
            style: string | null = null
        ) => {
            // Create the cell element
            let cell;
            if (typeof content === 'string') {
                cell = document.createElement('div');
                cell.innerHTML = content;
            } else {
                cell = content;
            }

            // Apply the style
            if (style !== null) {
                cell.style.cssText = style;
            }

            // Set its grid position
            cell.style.gridColumn = column.toString();
            cell.style.gridRow = rowIndex.toString();
            cell.style.gridColumnEnd = `span ${width}`;

            // Append the cell to the grid
            this.componentDetailsElement.appendChild(cell);

            return cell;
        };

        const labelStyle = 'opacity: 0.5; text-align: right';
        const valueStyle = 'font-weight: bold';

        // TODO: Get more details, including those specific to this component
        // type
        // - spacing for Rows / Columns
        // - text style for Text
        // - ...
        // - Arbitrary state (repr it right in Python)
        // - Which file/line number the component was created at

        // Size
        rowIndex++;
        let size = selectedComponent.state._size_;
        let grow = selectedComponent.state._grow_;

        let width = grow[0]
            ? 'grow'
            : size[0] === null
              ? 'natural'
              : size[0].toString();
        let height = grow[1]
            ? 'grow'
            : size[1] === null
              ? 'natural'
              : size[1].toString();

        makeCell(1, 1, 'width', labelStyle);
        makeCell(2, 1, width, valueStyle);

        makeCell(3, 1, 'height', labelStyle);
        makeCell(4, 1, height, valueStyle);

        // Margin
        rowIndex++;
        let margins = selectedComponent.state._margin_;
        let singleX = margins[0] === margins[2];
        let singleY = margins[1] === margins[3];

        if (singleX && singleY) {
            makeCell(1, 1, 'margin', labelStyle);
            makeCell(2, 1, margins[0].toString(), valueStyle);
        } else {
            if (singleX) {
                makeCell(1, 1, 'margin_x', labelStyle);
                makeCell(2, 1, margins[0].toString(), valueStyle);
            } else {
                makeCell(1, 1, 'margin_left', labelStyle);
                makeCell(2, 1, margins[0].toString(), valueStyle);

                makeCell(3, 1, 'margin_right', labelStyle);
                makeCell(4, 1, margins[2].toString(), valueStyle);
            }

            rowIndex++;

            if (singleY) {
                makeCell(1, 1, 'margin_y', labelStyle);
                makeCell(2, 1, margins[1].toString(), valueStyle);
            } else {
                makeCell(1, 1, 'margin_top', labelStyle);
                makeCell(2, 1, margins[1].toString(), valueStyle);

                makeCell(3, 1, 'margin_bottom', labelStyle);
                makeCell(4, 1, margins[3].toString(), valueStyle);
            }
        }

        // Align
        rowIndex++;
        let align_x =
            selectedComponent.state._align_[0] === null
                ? 'None'
                : selectedComponent.state._align_[0].toString();

        let align_y =
            selectedComponent.state._align_[1] === null
                ? 'None'
                : selectedComponent.state._align_[1].toString();

        makeCell(1, 1, 'align_x', labelStyle);
        makeCell(2, 1, align_x, valueStyle);

        makeCell(3, 1, 'align_y', labelStyle);
        makeCell(4, 1, align_y, valueStyle);

        // Link to documentation
        // TODO: Properly determine whether this is a Rio component or not
        let isRioComponent = selectedComponent.state._type_ !== 'Placeholder';

        if (isRioComponent) {
            let docUrl = `https://rio.dev/documentation/${selectedComponent.state._python_type_.toLowerCase()}`;

            this.docsLinkElement.style.removeProperty('display');
            this.docsLinkElement.setAttribute('href', docUrl);
        } else {
            this.docsLinkElement.style.display = 'none';
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

        // The widget tree has been modified. Browsers struggle to retrieve
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
