import { ComponentBase, ComponentState } from "./components/componentBase";

import { AlignComponent } from './components/align';
import { ButtonComponent } from './components/button';
import { ClassContainerComponent } from './components/classContainer';
import { ColorPickerComponent } from './components/colorPicker';
import { ColumnComponent, RowComponent } from './components/linearContainers';
import { DrawerComponent } from './components/drawer';
import { DropdownComponent } from './components/dropdown';
import { GridComponent } from './components/grid';
import { IconComponent } from './components/icon';
import { ImageComponent } from './components/image';
import { KeyEventListenerComponent } from './components/keyEventListener';
import { LinkComponent } from './components/link';
import { MarginComponent } from './components/margin';
import { MarkdownViewComponent } from './components/markdownView';
import { MediaPlayerComponent } from './components/mediaPlayer';
import { MouseEventListenerComponent } from './components/mouseEventListener';
import { PlaceholderComponent } from './components/placeholder';
import { PlotComponent } from './components/plot';
import { PopupComponent } from './components/popup';
import { ProgressBarComponent } from './components/progressBar';
import { ProgressCircleComponent } from './components/progressCircle';
import { RectangleComponent } from './components/rectangle';
import { RevealerComponent } from './components/revealer';
import { ScrollContainerComponent } from './components/scrollContainer';
import { ScrollTargetComponent } from './components/scrollTarget';
import { SizeTripSwitchComponent } from './components/sizeTripSwitch';
import { SliderComponent } from './components/slider';
import { SlideshowComponent } from './components/slideshow';
import { StackComponent } from './components/stack';
import { SwitchComponent } from './components/switch';
import { TextInputComponent } from './components/textInput';
import { TextComponent } from './components/text';
import { ComponentId } from "./models";
import { HtmlComponent } from "./components/html";

const componentClasses = {
    'Align-builtin': AlignComponent,
    'Button-builtin': ButtonComponent,
    'ClassContainer-builtin': ClassContainerComponent,
    'ColorPicker-builtin': ColorPickerComponent,
    'Column-builtin': ColumnComponent,
    'Drawer-builtin': DrawerComponent,
    'Dropdown-builtin': DropdownComponent,
    'Grid-builtin': GridComponent,
    'Html-builtin': HtmlComponent,
    'Icon-builtin': IconComponent,
    'Image-builtin': ImageComponent,
    'KeyEventListener-builtin': KeyEventListenerComponent,
    'Link-builtin': LinkComponent,
    'Margin-builtin': MarginComponent,
    'MarkdownView-builtin': MarkdownViewComponent,
    'MediaPlayer-builtin': MediaPlayerComponent,
    'MouseEventListener-builtin': MouseEventListenerComponent,
    'Plot-builtin': PlotComponent,
    'Popup-builtin': PopupComponent,
    'ProgressBar-builtin': ProgressBarComponent,
    'ProgressCircle-builtin': ProgressCircleComponent,
    'Rectangle-builtin': RectangleComponent,
    'Revealer-builtin': RevealerComponent,
    'Row-builtin': RowComponent,
    'ScrollContainer-builtin': ScrollContainerComponent,
    'ScrollTarget-builtin': ScrollTargetComponent,
    'SizeTripSwitch-builtin': SizeTripSwitchComponent,
    'Slider-builtin': SliderComponent,
    'Slideshow-builtin': SlideshowComponent,
    'Stack-builtin': StackComponent,
    'Switch-builtin': SwitchComponent,
    'Text-builtin': TextComponent,
    'TextInput-builtin': TextInputComponent,
    Placeholder: PlaceholderComponent,
};

globalThis.componentClasses = componentClasses;


const componentTreeRootElement = document.body.firstElementChild as HTMLElement;

const elementsToInstances = new WeakMap<HTMLElement, ComponentBase>();


export function getElementByComponentId(id: ComponentId): HTMLElement {
    let element = document.getElementById(`rio-id-${id}`);

    if (element === null) {
        throw `Could not find html element with id ${id}`;
    }

    return element;
}

export function getInstanceByComponentId(id: ComponentId): ComponentBase {
    let element = getElementByComponentId(id);

    let instance = elementsToInstances.get(element);

    if (instance === undefined) {
        throw `Could not find component with id ${id}`;
    }

    return instance;
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
    id: number | string,
    deltaState: ComponentState
): ComponentState {
    let parentElement = document.getElementById(`rio-id-${id}`);

    if (parentElement === null) {
        return deltaState;
    }

    let parentInstance = elementsToInstances.get(parentElement);

    if (parentInstance === undefined) {
        return deltaState;
    }

    return {
        ...parentInstance.state,
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
            _size_: entireState['_size_'],
            _grow_: entireState['_grow_'],
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
            _size_: entireState['_size_'],
            _grow_: entireState['_grow_'],
            // @ts-ignore
            child: resultId,
            align_x: align[0],
            align_y: align[1],
        };
        resultId = alignId;
    }

    return resultId;
}

function replaceChildrenWithLayoutComponents(
    deltaState: ComponentState,
    childIds: Set<string>,
    message: { [id: string]: ComponentState }
): void {
    let propertyNamesWithChildren = globalThis.childAttributeNames[deltaState['_type_']!] || [];

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

function preprocessDeltaStates(message: { [id: string]: ComponentState }): void {
    // Fortunately the root component is created internally by the server, so we
    // don't need to worry about it having a margin or alignment.

    let originalComponentIds = Object.keys(message);

    // Keep track of which components have their parents in the message
    let childIds: Set<string> = new Set();

    // Walk over all components in the message and inject layout components. The
    // message is modified in-place, so take care to have a copy of all keys
    for (let componentId of originalComponentIds) {
        replaceChildrenWithLayoutComponents(message[componentId], childIds, message);
    }

    // Find all components which have had a layout component injected, and make sure
    // their parents are updated to point to the new component.
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

        let parentInstance = elementsToInstances.get(parentElement);
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
    message: { [id: string]: ComponentState },
    rootComponentId: string | number | null
): void {
    // Preprocess the message. This converts `_align_` and `_margin_` properties
    // into actual components, amongst other things.
    preprocessDeltaStates(message);

    // Modifying the DOM makes the keyboard focus get lost. Remember which
    // element had focus, so we can restore it later.
    let focusedElement = document.activeElement;

    // Create a HTML element to hold all latent components, so they aren't
    // garbage collected while updating the DOM.
    let latentComponents = document.createElement('div');
    latentComponents.id = 'rio-latent-components';
    latentComponents.style.display = 'none';
    document.body.appendChild(latentComponents);

    // Make sure all components mentioned in the message have a corresponding HTML
    // element
    for (let componentId in message) {
        let deltaState = message[componentId];
        let elementId = `rio-id-${componentId}`;
        let element = document.getElementById(elementId);

        // This is a reused element, no need to instantiate a new one
        if (element) {
            continue;
        }

        // Get the class for this component
        const componentClass = componentClasses[deltaState._type_!];

        // Make sure the component type is valid (Just helpful for debugging)
        if (!componentClass) {
            throw `Encountered unknown component type: ${deltaState._type_}`;
        }

        // Create an instance for this component
        let instance: ComponentBase = new componentClass(elementId, deltaState);

        // Build the component
        element = instance.createElement();

        // Store the component's class name in the element. Used for debugging.
        element.setAttribute('dbg-py-class', deltaState._python_type_!);

        // Set the component's key, if it has one. Used for debugging.
        let key = deltaState['key'];
        if (key !== undefined) {
            element.setAttribute('dbg-key', `${key}`);
        }

        // Create a mapping from the element to the component instance
        elementsToInstances.set(element, instance);

        // Keep the component alive
        latentComponents.appendChild(element);
    }

    // Update all components mentioned in the message
    let componentsNeedingLayoutUpdate = new Set<ComponentBase>();

    for (let id in message) {
        let deltaState = message[id];
        let element = getElementByComponentId(id);

        // Perform updates specific to this component type
        let instance = elementsToInstances.get(element!) as ComponentBase;
        instance.updateElement(element, deltaState);

        // Update the component's state
        instance.state = {
            ...instance.state,
            ...deltaState,
        };

        // Queue the component and its parent for a layout update
        componentsNeedingLayoutUpdate.add(instance);

        let parentElement = getParentComponentElementIncludingInjected(element!);
        if (parentElement) {
            let parentInstance = elementsToInstances.get(parentElement);

            if (!parentInstance) {
                throw `Failed to find parent component for ${id}`;
            }

            componentsNeedingLayoutUpdate.add(parentInstance);
        }
    }

    // Components that have changed, or had their parents changed need to have
    // their layout updated
    componentsNeedingLayoutUpdate.forEach((component) => {
        component.updateChildLayouts();
    });

    // Replace the root component if requested
    if (rootComponentId !== null) {
        let rootElement = getElementByComponentId(rootComponentId);
        componentTreeRootElement.innerHTML = '';
        componentTreeRootElement.appendChild(rootElement);
    }

    // Restore the keyboard focus
    if (focusedElement instanceof HTMLElement) {
        focusedElement.focus();
    }

    // Remove the latent components
    latentComponents.remove();
}


export function replaceOnlyChildAndResetCssProperties(
    parentElement: HTMLElement,
    childId: null | undefined | number | string
): void {
    // If undefined, do nothing
    if (childId === undefined) {
        return;
    }

    // If null, remove the child
    if (childId === null) {
        parentElement.innerHTML = '';
        return;
    }

    const currentChildElement = parentElement.firstElementChild;

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
    let newElement = getElementByComponentId(childId);
    parentElement?.appendChild(newElement);

    // Reset the new child's CSS properties
    let childInstance = getInstanceByComponentId(childId);
    childInstance.resetCssProperties();
}

export function replaceChildrenAndResetCssProperties(
    parentElement: HTMLElement,
    childIds: undefined | (number | string)[],
    wrapInDivs: boolean = false
) {
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

                let newElement = getElementByComponentId(curId);
                parentElement.appendChild(wrap(newElement!));

                let newInstance = getInstanceByComponentId(curId);
                newInstance.resetCssProperties();

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
        let newElement = getElementByComponentId(curId);
        parentElement.insertBefore(wrap(newElement!), curElement);

        let newInstance = getInstanceByComponentId(curId);
        newInstance.resetCssProperties();

        curIdIndex++;
    }
}
