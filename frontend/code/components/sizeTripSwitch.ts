import { pixelsPerEm } from '../app';
import { ComponentId } from '../models';
import { SingleContainer } from './singleContainer';
import { ComponentState } from './componentBase';

export type SizeTripSwitchState = ComponentState & {
    _type_: 'SizeTripSwitch-builtin';
    child?: ComponentId;
    width_threshold?: number | null;
    height_threshold?: number | null;
    is_wide?: boolean;
    is_tall?: boolean;
};

// Call `callback` when the size of `component` changes. Furthermore, make sure to
// stop observing the component when it is no longer in the DOM.
function watchComponent(
    component: HTMLElement,
    callback: (width: number, height: number) => void
): void {
    let resizeObserver: ResizeObserver;

    // Watch for size changes
    const handleResize = (entries: ResizeObserverEntry[]) => {
        for (const entry of entries) {
            const { width, height } = entry.contentRect;
            callback(width, height);
        }
    };

    resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(component);

    // Periodically check if the component is still in the DOM, and stop observing
    // it if it is not.
    const checkComponentInDOM = () => {
        // Component is still in the DOM, so keep checking
        if (component.isConnected) {
            setTimeout(checkComponentInDOM, 30000);
        }

        // Stop observing the component
        resizeObserver.disconnect();
    };
    setTimeout(checkComponentInDOM, 30000);
}

export class SizeTripSwitchComponent extends SingleContainer {
    state: Required<SizeTripSwitchState>;

    _createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');

        // Watch for size changes
        watchComponent(element, this.processSize.bind(this));

        return element;
    }

    _updateElement(element: HTMLElement, deltaState: SizeTripSwitchState): void {
        // The update may have changed the thresholds, so reprocess the size
        this.processSize(element.clientWidth, element.clientHeight);
    }

    processSize(width: number, height: number): void {
        // Does the component exceed its thresholds?
        const is_wide =
            this.state.width_threshold !== null &&
            width / pixelsPerEm > this.state.width_threshold;
        const is_tall =
            this.state.height_threshold !== null &&
            height / pixelsPerEm > this.state.height_threshold;

        // If this differs from the previous state, notify the backend
        if (is_wide !== this.state.is_wide || is_tall !== this.state.is_tall) {
            this.setStateAndNotifyBackend({
                is_wide,
                is_tall,
            });
        }
    }
}
