import { pixelsPerEm, replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type SizeTripSwitchState = WidgetState & {
    _type_: 'SizeTripSwitch-builtin';
    child?: number | string;
    width_threshold?: number | null;
    height_threshold?: number | null;
    is_wide?: boolean;
    is_tall?: boolean;
};

// Call `callback` when the size of `widget` changes. Furthermore, make sure to
// stop observing the widget when it is no longer in the DOM.
function watchWidget(
    widget: HTMLElement,
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
    resizeObserver.observe(widget);

    // Periodically check if the widget is still in the DOM, and stop observing
    // it if it is not.
    const checkWidgetInDOM = () => {
        // Widget is still in the DOM, so keep checking
        if (widget.isConnected) {
            setTimeout(checkWidgetInDOM, 30000);
        }

        // Stop observing the widget
        resizeObserver.disconnect();
    };
    setTimeout(checkWidgetInDOM, 30000);
}

export class SizeTripSwitchWidget extends WidgetBase {
    state: Required<SizeTripSwitchState>;

    createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('reflex-single-container');

        // Watch for size changes
        watchWidget(element, this.processSize.bind(this));

        return element;
    }

    updateElement(element: HTMLElement, deltaState: SizeTripSwitchState): void {
        // Update the child
        replaceOnlyChild(element, deltaState.child);

        // The update may have changed the thresholds, so reprocess the size
        this.processSize(element.clientWidth, element.clientHeight);
    }

    processSize(width: number, height: number): void {
        // Does the widget exceed its thresholds?
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
