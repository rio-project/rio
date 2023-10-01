import { WidgetBase, WidgetState } from "./widgets/widgetBase";

import { AlignWidget } from './widgets/align';
import { ButtonWidget } from './widgets/button';
import { ClassContainerWidget } from './widgets/classContainer';
import { ColorPickerWidget } from './widgets/colorPicker';
import { ColumnWidget, RowWidget } from './widgets/linearContainers';
import { DrawerWidget } from './widgets/drawer';
import { DropdownWidget } from './widgets/dropdown';
import { GridWidget } from './widgets/grid';
import { IconWidget } from './widgets/icon';
import { ImageWidget } from './widgets/image';
import { KeyEventListenerWidget } from './widgets/keyEventListener';
import { LinkWidget } from './widgets/link';
import { MarginWidget } from './widgets/margin';
import { MarkdownViewWidget } from './widgets/markdownView';
import { MediaPlayerWidget } from './widgets/mediaPlayer';
import { MouseEventListenerWidget } from './widgets/mouseEventListener';
import { PlaceholderWidget } from './widgets/placeholder';
import { PlotWidget } from './widgets/plot';
import { PopupWidget } from './widgets/popup';
import { ProgressBarWidget } from './widgets/progressBar';
import { ProgressCircleWidget } from './widgets/progressCircle';
import { RectangleWidget } from './widgets/rectangle';
import { RevealerWidget } from './widgets/revealer';
import { ScrollContainerWidget } from './widgets/scrollContainer';
import { ScrollTargetWidget } from './widgets/scrollTarget';
import { SizeTripSwitchWidget } from './widgets/sizeTripSwitch';
import { SliderWidget } from './widgets/slider';
import { SlideshowWidget } from './widgets/slideshow';
import { StackWidget } from './widgets/stack';
import { SwitchWidget } from './widgets/switch';
import { TextInputWidget } from './widgets/textInput';
import { TextWidget } from './widgets/text';
import { WidgetId } from "./models";

const widgetClasses = {
    'Align-builtin': AlignWidget,
    'Button-builtin': ButtonWidget,
    'ClassContainer-builtin': ClassContainerWidget,
    'ColorPicker-builtin': ColorPickerWidget,
    'Column-builtin': ColumnWidget,
    'Drawer-builtin': DrawerWidget,
    'Dropdown-builtin': DropdownWidget,
    'Grid-builtin': GridWidget,
    'Icon-builtin': IconWidget,
    'Image-builtin': ImageWidget,
    'KeyEventListener-builtin': KeyEventListenerWidget,
    'Link-builtin': LinkWidget,
    'Margin-builtin': MarginWidget,
    'MarkdownView-builtin': MarkdownViewWidget,
    'MediaPlayer-builtin': MediaPlayerWidget,
    'MouseEventListener-builtin': MouseEventListenerWidget,
    'Plot-builtin': PlotWidget,
    'Popup-builtin': PopupWidget,
    'ProgressBar-builtin': ProgressBarWidget,
    'ProgressCircle-builtin': ProgressCircleWidget,
    'Rectangle-builtin': RectangleWidget,
    'Revealer-builtin': RevealerWidget,
    'Row-builtin': RowWidget,
    'ScrollContainer-builtin': ScrollContainerWidget,
    'ScrollTarget-builtin': ScrollTargetWidget,
    'SizeTripSwitch-builtin': SizeTripSwitchWidget,
    'Slider-builtin': SliderWidget,
    'Slideshow-builtin': SlideshowWidget,
    'Stack-builtin': StackWidget,
    'Switch-builtin': SwitchWidget,
    'Text-builtin': TextWidget,
    'TextInput-builtin': TextInputWidget,
    Placeholder: PlaceholderWidget,
};

globalThis.widgetClasses = widgetClasses;


const widgetTreeRootElement = document.body.firstElementChild as HTMLElement;

const elementsToInstances = new WeakMap<HTMLElement, WidgetBase>();


export function getElementByWidgetId(id: WidgetId): HTMLElement {
    let element = document.getElementById(`rio-id-${id}`);

    if (element === null) {
        throw `Could not find html element with id ${id}`;
    }

    return element;
}

export function getInstanceByWidgetId(id: WidgetId): WidgetBase {
    let element = getElementByWidgetId(id);

    let instance = elementsToInstances.get(element);

    if (instance === undefined) {
        throw `Could not find widget with id ${id}`;
    }

    return instance;
}

export function getParentWidgetElementIncludingInjected(
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

export function getParentWidgetElementExcludingInjected(
    element: HTMLElement
): HTMLElement | null {
    let curElement: HTMLElement | null = element;

    while (true) {
        curElement = getParentWidgetElementIncludingInjected(curElement);

        if (curElement === null) {
            return null;
        }

        if (curElement.id.match(/rio-id-\d+$/)) {
            return curElement;
        }
    }
}

function getCurrentWidgetState(
    id: number | string,
    deltaState: WidgetState
): WidgetState {
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

function createLayoutWidgetStates(
    widgetId: number | string,
    deltaState: WidgetState,
    message: { [id: string]: WidgetState }
): number | string {
    let entireState = getCurrentWidgetState(widgetId, deltaState);
    let resultId = widgetId;

    // Margin
    let margin = entireState['_margin_']!;
    if (
        margin[0] !== 0 ||
        margin[1] !== 0 ||
        margin[2] !== 0 ||
        margin[3] !== 0
    ) {
        let marginId = `${widgetId}-margin`;
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
        let alignId = `${widgetId}-align`;
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

function replaceChildrenWithLayoutWidgets(
    deltaState: WidgetState,
    childIds: Set<string>,
    message: { [id: string]: WidgetState }
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
                return createLayoutWidgetStates(
                    childId,
                    message[childId] || {},
                    message
                );
            });
        } else if (propertyValue !== null && propertyValue !== undefined) {
            let childId = cleanId(propertyValue.toString());
            deltaState[propertyName] = createLayoutWidgetStates(
                childId,
                message[childId] || {},
                message
            );
            childIds.add(childId);
        }
    }
}

function preprocessDeltaStates(message: { [id: string]: WidgetState }): void {
    // Fortunately the root widget is created internally by the server, so we
    // don't need to worry about it having a margin or alignment.

    let originalWidgetIds = Object.keys(message);

    // Keep track of which widgets have their parents in the message
    let childIds: Set<string> = new Set();

    // Walk over all widgets in the message and inject layout widgets. The
    // message is modified in-place, so take care to have a copy of all keys
    for (let widgetId of originalWidgetIds) {
        replaceChildrenWithLayoutWidgets(message[widgetId], childIds, message);
    }

    // Find all widgets which have had a layout widget injected, and make sure
    // their parents are updated to point to the new widget.
    for (let widgetId of originalWidgetIds) {
        // Child of another widget in the message
        if (childIds.has(widgetId)) {
            continue;
        }

        // The parent isn't contained in the message. Find and add it.
        let childElement = document.getElementById(`rio-id-${widgetId}`);
        if (childElement === null) {
            continue;
        }

        let parentElement =
            getParentWidgetElementExcludingInjected(childElement);
        if (parentElement === null) {
            continue;
        }

        let parentInstance = elementsToInstances.get(parentElement);
        if (parentInstance === undefined) {
            throw `Parent widget with id ${parentElement} not found`;
        }

        let parentId = parentElement.id.slice('rio-id-'.length);
        let newParentState = { ...parentInstance.state };
        replaceChildrenWithLayoutWidgets(newParentState, childIds, message);
        message[parentId] = newParentState;
    }
}

export function updateWidgetStates(
    message: { [id: string]: WidgetState },
    rootWidgetId: string | number | null
): void {
    // Preprocess the message. This converts `_align_` and `_margin_` properties
    // into actual widgets, amongst other things.
    preprocessDeltaStates(message);

    // Modifying the DOM makes the keyboard focus get lost. Remember which
    // element had focus, so we can restore it later.
    let focusedElement = document.activeElement;

    // Create a HTML element to hold all latent widgets, so they aren't
    // garbage collected while updating the DOM.
    let latentWidgets = document.createElement('div');
    latentWidgets.id = 'rio-latent-widgets';
    latentWidgets.style.display = 'none';
    document.body.appendChild(latentWidgets);

    // Make sure all widgets mentioned in the message have a corresponding HTML
    // element
    for (let widgetId in message) {
        let deltaState = message[widgetId];
        let elementId = `rio-id-${widgetId}`;
        let element = document.getElementById(elementId);

        // This is a reused element, no need to instantiate a new one
        if (element) {
            continue;
        }

        // Get the class for this widget
        const widgetClass = widgetClasses[deltaState._type_!];

        // Make sure the widget type is valid (Just helpful for debugging)
        if (!widgetClass) {
            throw `Encountered unknown widget type: ${deltaState._type_}`;
        }

        // Create an instance for this widget
        let instance: WidgetBase = new widgetClass(elementId, deltaState);

        // Build the widget
        element = instance.createElement();
        element.id = elementId;
        element.classList.add('rio-widget');

        // Store the widget's class name in the element. Used for debugging.
        element.setAttribute('dbg-py-class', deltaState._python_type_!);

        // Set the widget's key, if it has one. Used for debugging.
        let key = deltaState['key'];
        if (key !== undefined) {
            element.setAttribute('dbg-key', `${key}`);
        }

        // Create a mapping from the element to the widget instance
        elementsToInstances.set(element, instance);

        // Keep the widget alive
        latentWidgets.appendChild(element);
    }

    // Update all widgets mentioned in the message
    let widgetsNeedingLayoutUpdate = new Set<WidgetBase>();

    for (let id in message) {
        let deltaState = message[id];
        let element = getElementByWidgetId(id);

        // Perform updates common to all widgets
        commonUpdate(element, deltaState);

        // Perform updates specific to this widget type
        let instance = elementsToInstances.get(element!) as WidgetBase;
        instance.updateElement(element, deltaState);

        // Update the widget's state
        instance.state = {
            ...instance.state,
            ...deltaState,
        };

        // Queue the widget and its parent for a layout update
        widgetsNeedingLayoutUpdate.add(instance);

        let parentElement = getParentWidgetElementIncludingInjected(element!);
        if (parentElement) {
            let parentInstance = elementsToInstances.get(parentElement);

            if (!parentInstance) {
                throw `Failed to find parent widget for ${id}`;
            }

            widgetsNeedingLayoutUpdate.add(parentInstance);
        }
    }

    // Widgets that have changed, or had their parents changed need to have
    // their layout updated
    widgetsNeedingLayoutUpdate.forEach((widget) => {
        widget.updateChildLayouts();
    });

    // Replace the root widget if requested
    if (rootWidgetId !== null) {
        let rootElement = getElementByWidgetId(rootWidgetId);
        widgetTreeRootElement.innerHTML = '';
        widgetTreeRootElement.appendChild(rootElement);
    }

    // Restore the keyboard focus
    if (focusedElement instanceof HTMLElement) {
        focusedElement.focus();
    }

    // Remove the latent widgets
    latentWidgets.remove();
}

function commonUpdate(element: HTMLElement, state: WidgetState) {
    if (state._size_ !== undefined) {
        if (state._size_[0] === null) {
            element.style.removeProperty('min-width');
        } else {
            element.style.minWidth = `${state._size_[0]}em`;
        }

        if (state._size_[1] === null) {
            element.style.removeProperty('min-height');
        } else {
            element.style.minHeight = `${state._size_[1]}em`;
        }
    }
}

export function replaceOnlyChild(
    parentElement: HTMLElement,
    childId: null | undefined | number | string
) {
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
        let latentWidgets = document.getElementById('rio-latent-widgets');
        latentWidgets?.appendChild(currentChildElement);
    }

    // Add the replacement widget
    let newElement = getElementByWidgetId(childId);
    parentElement?.appendChild(newElement);
}

export function replaceChildren(
    parentElement: HTMLElement,
    childIds: undefined | (number | string)[],
    wrapInDivs: boolean = false
) {
    // If undefined, do nothing
    if (childIds === undefined) {
        return;
    }
    let latentWidgets = document.getElementById('rio-latent-widgets')!;

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
                let newElement = getElementByWidgetId(curId);
                parentElement.appendChild(wrap(newElement!));
                curIdIndex++;
            }
            break;
        }

        // If there are no more children in the message, remove the remaining
        // DOM children
        if (curIdIndex >= childIds.length) {
            while (curElement !== null) {
                let nextElement = curElement.nextElementSibling;
                latentWidgets.appendChild(wrap(curElement));
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
        let newElement = getElementByWidgetId(curId);
        parentElement.insertBefore(wrap(newElement!), curElement);
        curIdIndex++;
    }
}
