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

    // The component currently selected in the tree
    //
    // Components change, appear and disappear. The component referenced here
    // may not actually exist. So instead of using this directly, use
    // `getSelectedComponent()`, which will select something sensible if the
    // previously selected component no longer exists.
    private _selectedComponentElementId: str =
        '<placeholder-id-will-be-replaced-on-first-acccess>';

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

    /// Returns the currently selected component. This should be preferred over
    /// using the `_selectedComponent` member directly, as this function will
    /// impute a sensible component if the selected component no longer exists.
    getSelectedComponent(): ComponentBase {
        // Does the previously selected component still exist?
        let element = document.getElementById(this._selectedComponentElementId);
        let selectedComponent: ComponentBase | null = null;

        if (element !== null) {
            selectedComponent = tryGetInstanceByElement(element);
        }

        if (selectedComponent !== null) {
            return selectedComponent;
        }

        // Default to the root
        let result = this.getDisplayedRootComponent();
        this._selectedComponentElementId = result.elementId;
        return result;
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

        // Don't start off with a fully collapsed tree
        if (!this.getNodeExpanded(rootComponent)) {
            // this.setNodeExpanded(rootComponent, true);
        }

        // Highlight the selected component
        // this.highlightTreeItemAndParents(this.selectedComponent);
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
            this._selectedComponentElementId = instance.elementId;

            // Update the selected component details
            this.buildDetails();

            // Highlight the tree item
            this.highlightTreeItemAndParents(instance);

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
            //
            // Take into account the CSS' border width and padding
            const cssBorder = 0.4;
            const offset = -cssBorder * pixelsPerEm;

            let highlighter = document.createElement('div');
            highlighter.classList.add('rio-debugger-component-highlighter');
            highlighter.style.top = `${rect.top + offset}px`;
            highlighter.style.left = `${rect.left + offset}px`;
            highlighter.style.width = `${rect.width + offset}px`;
            highlighter.style.height = `${rect.height + offset}px`;
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
        const iconStyle =
            'width: 1.2rem; height: 1.2rem; opacity: 0.5; margin-left: auto';

        // Key
        // let keyIconElement = makeCell(1, 1, 'ki', iconStyle);
        // makeCell(
        //     2,
        //     1,
        //     this.selectedComponent.state._key_ === null
        //         ? 'None'
        //         : this.selectedComponent.state._key_,
        //     valueStyle
        // );

        // applyIcon(keyIconElement, 'key', 'currentColor');

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
        // TODO: Determine whether this is a Rio component or not
        let isRioComponent = Math.random() < 0.5;
        if (isRioComponent) {
            let docUrl = `https://rio.dev/documentation/${selectedComponent.state._python_type_.toLowerCase()}`;

            this.docsLinkElement.style.removeProperty('display');
            this.docsLinkElement.setAttribute('href', docUrl);
        } else {
            this.docsLinkElement.style.display = 'none';
        }
    }
}
