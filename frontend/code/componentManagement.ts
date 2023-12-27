import { AlignComponent } from './components/align';
import { ButtonComponent } from './components/button';
import { CardComponent } from './components/card';
import { ClassContainerComponent } from './components/classContainer';
import { ColorPickerComponent } from './components/colorPicker';
import { ColumnComponent, RowComponent } from './components/linearContainers';
import { ComponentBase, ComponentState } from './components/componentBase';
import { ComponentId } from './models';
import { ComponentTreeComponent } from './components/componentTree';
import { CustomListItemComponent } from './components/customListItem';
import { DebuggerConnectorComponent } from './components/debuggerConnector';
import { DrawerComponent } from './components/drawer';
import { DropdownComponent } from './components/dropdown';
import { FlowComponent as FlowContainerComponent } from './components/flowContainer';
import { FundamentalRootComponent } from './components/fundamentalRootComponent';
import { GridComponent } from './components/grid';
import { HeadingListItemComponent } from './components/headingListItem';
import { HtmlComponent } from './components/html';
import { IconComponent } from './components/icon';
import { ImageComponent } from './components/image';
import { KeyEventListenerComponent } from './components/keyEventListener';
import { LinkComponent } from './components/link';
import { ListViewComponent } from './components/listView';
import { MarginComponent } from './components/margin';
import { MarkdownViewComponent } from './components/markdownView';
import { MediaPlayerComponent } from './components/mediaPlayer';
import { MouseEventListenerComponent } from './components/mouseEventListener';
import { OverlayComponent } from './components/overlay';
import { PlaceholderComponent } from './components/placeholder';
import { PlotComponent } from './components/plot';
import { PopupComponent } from './components/popup';
import { ProgressBarComponent } from './components/progressBar';
import { ProgressCircleComponent } from './components/progressCircle';
import { RectangleComponent } from './components/rectangle';
import { RevealerComponent } from './components/revealer';
import { ScrollContainerComponent } from './components/scrollContainer';
import { ScrollTargetComponent } from './components/scrollTarget';
import { SliderComponent } from './components/slider';
import { SlideshowComponent } from './components/slideshow';
import { StackComponent } from './components/stack';
import { SwitchComponent } from './components/switch';
import { SwitcherBarComponent } from './components/switcherBar';
import { TableComponent } from './components/table';
import { TextComponent } from './components/text';
import { TextInputComponent } from './components/textInput';
import { updateLayout } from './layouting';
import { SwitcherComponent } from './components/switcher';

const COMPONENT_CLASSES = {
    'Align-builtin': AlignComponent,
    'Button-builtin': ButtonComponent,
    'Card-builtin': CardComponent,
    'ClassContainer-builtin': ClassContainerComponent,
    'ColorPicker-builtin': ColorPickerComponent,
    'Column-builtin': ColumnComponent,
    'ComponentTree-builtin': ComponentTreeComponent,
    'CustomListItem-builtin': CustomListItemComponent,
    'DebuggerConnector-builtin': DebuggerConnectorComponent,
    'Drawer-builtin': DrawerComponent,
    'Dropdown-builtin': DropdownComponent,
    'FlowContainer-builtin': FlowContainerComponent,
    'FundamentalRootComponent-builtin': FundamentalRootComponent,
    'Grid-builtin': GridComponent,
    'HeadingListItem-builtin': HeadingListItemComponent,
    'Html-builtin': HtmlComponent,
    'Icon-builtin': IconComponent,
    'Image-builtin': ImageComponent,
    'KeyEventListener-builtin': KeyEventListenerComponent,
    'Link-builtin': LinkComponent,
    'ListView-builtin': ListViewComponent,
    'Margin-builtin': MarginComponent,
    'MarkdownView-builtin': MarkdownViewComponent,
    'MediaPlayer-builtin': MediaPlayerComponent,
    'MouseEventListener-builtin': MouseEventListenerComponent,
    'Overlay-builtin': OverlayComponent,
    'Plot-builtin': PlotComponent,
    'Popup-builtin': PopupComponent,
    'ProgressBar-builtin': ProgressBarComponent,
    'ProgressCircle-builtin': ProgressCircleComponent,
    'Rectangle-builtin': RectangleComponent,
    'Revealer-builtin': RevealerComponent,
    'Row-builtin': RowComponent,
    'ScrollContainer-builtin': ScrollContainerComponent,
    'ScrollTarget-builtin': ScrollTargetComponent,
    'Slider-builtin': SliderComponent,
    'Slideshow-builtin': SlideshowComponent,
    'Stack-builtin': StackComponent,
    'Switch-builtin': SwitchComponent,
    'Switcher-builtin': SwitcherComponent,
    'SwitcherBar-builtin': SwitcherBarComponent,
    'Table-builtin': TableComponent,
    'Text-builtin': TextComponent,
    'TextInput-builtin': TextInputComponent,
    Placeholder: PlaceholderComponent,
};

globalThis.COMPONENT_CLASSES = COMPONENT_CLASSES;

export const componentsById: { [id: ComponentId]: ComponentBase | undefined } =
    {};

export function getRootComponent(): FundamentalRootComponent {
    let element = document.body.firstElementChild as HTMLElement;
    return getComponentByElement(element) as FundamentalRootComponent;
}

export function getComponentByElement(element: HTMLElement): ComponentBase {
    let instance = tryGetComponentByElement(element);

    if (instance === null) {
        throw `This element does not correspond to a component`;
    }

    return instance;
}

globalThis.getInstanceByElement = getComponentByElement; // For debugging

export function tryGetComponentByElement(
    element: Element
): ComponentBase | null {
    return componentsById[element.id.slice('rio-id-'.length)] ?? null;
}

export function isComponentElement(element: Element): boolean {
    if (!element.id) {
        return false;
    }

    return element.id.startsWith('rio-id-');
}

export function getParentComponentElementIncludingInjected(
    element: HTMLElement
): HTMLElement | null {
    let curElement = element.parentElement;

    while (curElement !== null) {
        if (curElement.id.startsWith('rio-id-')) {
            return curElement;
        }

        curElement = curElement.parentElement;
    }

    return null;
}

export function getParentComponentElementExcludingInjected(
    element: HTMLElement
): HTMLElement | null {
    let curElement: HTMLElement | null = element;

    while (true) {
        curElement = getParentComponentElementIncludingInjected(curElement);

        if (curElement === null) {
            return null;
        }

        if (curElement.id.match(/rio-id-\d+$/)) {
            return curElement;
        }
    }
}

function getCurrentComponentState(
    id: ComponentId,
    deltaState: ComponentState
): ComponentState {
    let instance = componentsById[id];

    if (instance === undefined) {
        return deltaState;
    }

    return {
        ...instance.state,
        ...deltaState,
    };
}

function createLayoutComponentStates(
    componentId: number | string,
    deltaState: ComponentState,
    message: { [id: string]: ComponentState }
): number | string {
    let entireState = getCurrentComponentState(componentId, deltaState);
    let resultId = componentId;

    // Margin
    let margin = entireState['_margin_']!;
    if (margin === undefined) {
        console.error(`Got incomplete state for component ${componentId}`);
    }
    if (
        margin[0] !== 0 ||
        margin[1] !== 0 ||
        margin[2] !== 0 ||
        margin[3] !== 0
    ) {
        let marginId = `${componentId}-margin`;
        message[marginId] = {
            _type_: 'Margin-builtin',
            _python_type_: 'Margin (injected)',
            _key_: null,
            _margin_: [0, 0, 0, 0],
            _size_: [0, 0],
            _grow_: entireState['_grow_'],
            _rio_internal_: true,
            // @ts-ignore
            child: resultId,
            margin_left: margin[0],
            margin_top: margin[1],
            margin_right: margin[2],
            margin_bottom: margin[3],
        };
        resultId = marginId;
    }

    // Align
    let align = entireState['_align_']!;
    if (align[0] !== null || align[1] !== null) {
        let alignId = `${componentId}-align`;
        message[alignId] = {
            _type_: 'Align-builtin',
            _python_type_: 'Align (injected)',
            _key_: null,
            _margin_: [0, 0, 0, 0],
            _size_: entireState['_size_'],
            _grow_: entireState['_grow_'],
            _rio_internal_: true,
            // @ts-ignore
            child: resultId,
            align_x: align[0],
            align_y: align[1],
        };
        resultId = alignId;
    }

    return resultId;
}

/// Given a state, return the ids of all its children
export function getChildIds(state: ComponentState): ComponentId[] {
    let result: ComponentId[] = [];

    let propertyNamesWithChildren =
        globalThis.CHILD_ATTRIBUTE_NAMES[state['_type_']!] || [];

    for (let propertyName of propertyNamesWithChildren) {
        let propertyValue = state[propertyName];

        if (Array.isArray(propertyValue)) {
            result.push(...propertyValue);
        } else if (propertyValue !== null && propertyValue !== undefined) {
            result.push(propertyValue);
        }
    }

    return result;
}

function replaceChildrenWithLayoutComponents(
    deltaState: ComponentState,
    childIds: Set<string>,
    message: { [id: string]: ComponentState }
): void {
    let propertyNamesWithChildren =
        globalThis.CHILD_ATTRIBUTE_NAMES[deltaState['_type_']!] || [];

    function cleanId(id: string): string {
        return id.split('-')[0];
    }

    for (let propertyName of propertyNamesWithChildren) {
        let propertyValue = deltaState[propertyName];

        if (Array.isArray(propertyValue)) {
            deltaState[propertyName] = propertyValue.map((childId) => {
                childId = cleanId(childId.toString());
                childIds.add(childId);
                return createLayoutComponentStates(
                    childId,
                    message[childId] || {},
                    message
                );
            });
        } else if (propertyValue !== null && propertyValue !== undefined) {
            let childId = cleanId(propertyValue.toString());
            deltaState[propertyName] = createLayoutComponentStates(
                childId,
                message[childId] || {},
                message
            );
            childIds.add(childId);
        }
    }
}

function preprocessDeltaStates(message: {
    [id: string]: ComponentState;
}): void {
    // Fortunately the root component is created internally by the server, so we
    // don't need to worry about it having a margin or alignment.

    let originalComponentIds = Object.keys(message);

    // Keep track of which components have their parents in the message
    let childIds: Set<string> = new Set();

    // Walk over all components in the message and inject layout components. The
    // message is modified in-place, so take care to have a copy of all keys
    // (`originalComponentIds`)
    for (let componentId of originalComponentIds) {
        replaceChildrenWithLayoutComponents(
            message[componentId],
            childIds,
            message
        );
    }

    // Find all components which have had a layout component injected, and make
    // sure their parents are updated to point to the new component.
    for (let componentId of originalComponentIds) {
        // Child of another component in the message
        if (childIds.has(componentId)) {
            continue;
        }

        // The parent isn't contained in the message. Find and add it.
        let childElement = document.getElementById(`rio-id-${componentId}`);
        if (childElement === null) {
            continue;
        }

        let parentElement =
            getParentComponentElementExcludingInjected(childElement);
        if (parentElement === null) {
            continue;
        }

        let parentInstance = getComponentByElement(parentElement);
        if (parentInstance === undefined) {
            throw `Parent component with id ${parentElement} not found`;
        }

        let parentId = parentElement.id.slice('rio-id-'.length);
        let newParentState = { ...parentInstance.state };
        replaceChildrenWithLayoutComponents(newParentState, childIds, message);
        message[parentId] = newParentState;
    }
}

export function updateComponentStates(
    deltaStates: { [id: string]: ComponentState },
    rootComponentId: string | number | null
): void {
    // Preprocess the message. This converts `_align_` and `_margin_` properties
    // into actual components, amongst other things.
    preprocessDeltaStates(deltaStates);

    // Modifying the DOM makes the keyboard focus get lost. Remember which
    // element had focus so we can restore it later.
    let focusedElement = document.activeElement;
    // Find the component that this HTMLElement belongs to
    while (focusedElement !== null && !isComponentElement(focusedElement)) {
        focusedElement = focusedElement.parentElement;
    }
    let focusedComponent =
        focusedElement === null
            ? null
            : getComponentByElement(focusedElement as HTMLElement);

    // Create a HTML element to hold all latent components, so they aren't
    // garbage collected while updating the DOM.
    let latentComponents = document.createElement('div');
    latentComponents.id = 'rio-latent-components';
    latentComponents.style.display = 'none';
    document.body.appendChild(latentComponents);

    // Make sure all components mentioned in the message have a corresponding HTML
    // element
    for (let componentId in deltaStates) {
        let deltaState = deltaStates[componentId];
        let component = componentsById[componentId];

        // This is a reused component, no need to instantiate a new one
        if (component) {
            continue;
        }

        // Get the class for this component
        const componentClass = COMPONENT_CLASSES[deltaState._type_!];

        // Make sure the component type is valid (Just helpful for debugging)
        if (!componentClass) {
            throw `Encountered unknown component type: ${deltaState._type_}`;
        }

        // Create an instance for this component
        let newComponent = new componentClass(componentId, deltaState);

        // Register the component for quick and easy lookup
        componentsById[componentId] = newComponent;

        // Store the component's class name in the element. Used for debugging.
        newComponent.element.setAttribute(
            'dbg-py-class',
            deltaState._python_type_!
        );

        // Set the component's key, if it has one. Used for debugging.
        let key = deltaState['key'];
        if (key !== undefined) {
            newComponent.element.setAttribute('dbg-key', `${key}`);
        }
    }

    // Update all components mentioned in the message
    for (let id in deltaStates) {
        let deltaState = deltaStates[id];
        let component = componentsById[id]!;

        // Perform updates specific to this component type
        component.updateElement(deltaState);

        // If the component's width or height has changed, request a re-layout.
        let width_changed =
            Math.abs(deltaState._size_![0] - component.state._size_[0]) > 1e-6;
        let height_changed =
            Math.abs(deltaState._size_![1] - component.state._size_[1]) > 1e-6;

        if (width_changed || height_changed) {
            console.log(
                `Triggering re-layout because component #${id} changed size: ${component.state._size_} -> ${deltaState._size_}`
            );
            component.makeLayoutDirty();
        }

        // Update the component's state
        component.state = {
            ...component.state,
            ...deltaState,
        };
    }

    // Set the root component if necessary
    if (rootComponentId !== null) {
        let rootElement = componentsById[rootComponentId]!.element;
        document.body.appendChild(rootElement);

        // Initialize the debugger, or not
        //
        // TODO: This should absolutely not be done here. It's just a convenient
        // spot for development.
        if (globalThis.RIO_DEBUG_MODE && globalThis.rioDebugger === undefined) {
            // initializeDebugger();
        }
    }

    // Restore the keyboard focus
    if (focusedComponent !== null) {
        restoreKeyboardFocus(focusedComponent, latentComponents);
    }

    // Remove the latent components
    for (let element of latentComponents.children) {
        let component = tryGetComponentByElement(element);
        if (component === null) {
            console.error("Couldn't find instance for latent element", element);
        } else {
            // Destruct the component and all its children
            let queue = [component];
            for (let comp of queue) {
                queue.push(...comp.getDirectChildren());
                comp.onDestruction();
                delete componentsById[comp.id];
            }
        }
    }
    latentComponents.remove();

    // Update the layout
    updateLayout();
}

function canHaveKeyboardFocus(instance: ComponentBase): boolean {
    // @ts-expect-error
    return typeof instance.grabKeyboardFocus === 'function';
}

function restoreKeyboardFocus(
    focusedComponent: ComponentBase,
    latentComponents: HTMLElement
): void {
    // The elements that are about to die still know the id of the parent from
    // which they were just removed. We'll go up the tree until we find a parent
    // that can accept the keyboard focus.
    //
    // Keep in mind that we have to traverse the component tree all the way up to
    // the root. Because even if a component still has a parent, the parent itself
    // might be about to die.
    let rootComponent = getRootComponent();
    let current = focusedComponent;
    let winner: ComponentBase | null = null;

    while (current !== rootComponent) {
        // If this component is dead, no child of it can get the keyboard focus
        if (current.element.parentElement === latentComponents) {
            winner = null;
        }

        // If we don't currently know of a focusable (and live) component, check
        // if this one fits the bill
        else if (winner === null && canHaveKeyboardFocus(current)) {
            winner = current;
        }

        current = current.tryGetParent()!;
    }

    // We made it to the root. Do we have a winner?
    if (winner !== null) {
        // @ts-expect-error
        winner.grabKeyboardFocus();
    }
}

export function replaceOnlyChild(
    parentId: string,
    parentElement: HTMLElement,
    childId: null | undefined | ComponentId
): void {
    // If undefined, do nothing
    if (childId === undefined) {
        return;
    }

    // If null, remove the current child
    const currentChildElement = parentElement.firstElementChild;

    if (childId === null) {
        if (currentChildElement !== null) {
            let latentComponents = document.getElementById(
                'rio-latent-components'
            );
            latentComponents?.appendChild(currentChildElement);
        }

        console.assert(parentElement.firstElementChild === null);
        return;
    }

    // If a child already exists, either move it to the latent container or
    // leave it alone if it's already the correct element
    if (currentChildElement !== null) {
        // Don't reparent the child if not necessary. This way things like
        // keyboard focus are preserved
        if (currentChildElement.id === `rio-id-${childId}`) {
            return;
        }

        // Move the child element to a latent container, so it isn't garbage
        // collected
        let latentComponents = document.getElementById('rio-latent-components');
        latentComponents?.appendChild(currentChildElement);
    }

    // Add the replacement component
    let childElement = componentsById[childId]!.element;
    parentElement?.appendChild(childElement);
    childElement.dataset.parentId = parentId;
}

export function replaceChildren(
    parentId: string,
    parentElement: HTMLElement,
    childIds: undefined | ComponentId[],
    wrapInDivs: boolean = false
): void {
    // If undefined, do nothing
    if (childIds === undefined) {
        return;
    }
    let latentComponents = document.getElementById('rio-latent-components')!;

    let curElement = parentElement.firstElementChild;
    let curIdIndex = 0;

    let wrap, unwrap;
    if (wrapInDivs) {
        wrap = (element: HTMLElement) => {
            let wrapper = document.createElement('div');
            wrapper.appendChild(element);
            return wrapper;
        };
        unwrap = (element: HTMLElement) => {
            return element.firstElementChild!;
        };
    } else {
        wrap = (element: HTMLElement) => element;
        unwrap = (element: HTMLElement) => element;
    }

    while (true) {
        // If there are no more children in the DOM element, add the remaining
        // children
        if (curElement === null) {
            while (curIdIndex < childIds.length) {
                let curId = childIds[curIdIndex];

                let childElement = componentsById[curId]!.element;
                parentElement.appendChild(wrap(childElement));
                childElement.dataset.parentId = parentId;

                curIdIndex++;
            }
            break;
        }

        // If there are no more children in the message, remove the remaining
        // DOM children
        if (curIdIndex >= childIds.length) {
            while (curElement !== null) {
                let nextElement = curElement.nextElementSibling;
                latentComponents.appendChild(wrap(curElement));
                curElement = nextElement;
            }
            break;
        }

        // This element is the correct element, move on
        let curId = childIds[curIdIndex];
        if (unwrap(curElement).id === `rio-id-${curId}`) {
            curElement = curElement.nextElementSibling;
            curIdIndex++;
            continue;
        }

        // This element is not the correct element, insert the correct one
        // instead
        let childElement = componentsById[curId]!.element;
        parentElement.insertBefore(wrap(childElement), curElement);
        childElement.dataset.parentId = parentId;

        curIdIndex++;
    }
}
