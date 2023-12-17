import { MDCRipple } from '@material/ripple';
import { applyIcon } from './designApplication';
import { DebuggerTreeDriver as DebuggerTreeDriver } from './debuggerTree';

export class Debugger {
    rootElement: HTMLElement;
    contentContainer: HTMLElement;

    // Visually highlights the currently active navigation button
    marker: HTMLElement;

    // A string representing which page is currently being displayed in the
    // content container. `null` means that no page is being displayed and the
    // container is hidden.
    displayedPageName: string | null = null;

    // The class managing the current page
    currentDriver: DebuggerTreeDriver | null = null;

    constructor() {
        // Spawn the debugger's HTML
        this.rootElement = document.createElement('div');
        this.rootElement.classList.add('rio-debugger');
        document.body.appendChild(this.rootElement);

        this.rootElement.innerHTML = `
            <div class="rio-debugger-content rio-switcheroo-neutral"></div>
            <div class="rio-debugger-navigation rio-switcheroo-background">
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

        this.marker = this.rootElement.querySelector(
            '.rio-debugger-navigation-marker'
        ) as HTMLElement;

        // Initialize the buttons, in reverse order
        this.makeNavButton('AI', 'chat-bubble:fill', 'aiChat');
        this.makeNavButton('Docs', 'library-books:fill', 'docs');
        this.makeNavButton('Stats', 'monitor-heart:fill', 'admin');
        this.makeNavButton('Tree', 'view-quilt:fill', 'componentTree');
    }

    /// Moves the marker to the given button
    _updateNavigationMarker(
        oldButton: HTMLElement | null,
        newButton: HTMLElement | null
    ) {
        // If the button should be hidden, just do that
        if (newButton === null) {
            this.marker.style.opacity = '0';
            return;
        }

        // Where should the marker be at?
        let targetRect = newButton.getBoundingClientRect();

        // If the button was previously hidden teleport it to the correct
        // location, then fade it in
        if (oldButton === null) {
            // Disable CSS transitions
            this.marker.style.transition = 'none';
            this.marker.offsetHeight;

            // Teleport
            this.marker.style.top = `${targetRect.top}px`;
            this.marker.style.height = `${targetRect.height}px`;

            // Re-enable CSS transitions
            this.marker.style.removeProperty('transition');

            // Fade in
            this.marker.style.removeProperty('opacity');
            return;
        }

        // Otherwise move it there
        this.marker.style.top = `${targetRect.top}px`;
        this.marker.style.height = `${targetRect.height}px`;
    }

    /// Display the given page in the content container, replacing the current
    /// one.
    navigateTo(pageName: string | null) {
        // Already there?
        if (pageName === this.displayedPageName) {
            return;
        }

        // Remove the old page
        if (this.displayedPageName !== null) {
            this.contentContainer.innerHTML = '';
        }

        // Move the marker
        let oldButton =
            this.displayedPageName === null
                ? null
                : (this.rootElement.querySelector(
                      `#rio-debugger-navigation-button-${this.displayedPageName}`
                  ) as HTMLElement);

        let newButton =
            pageName === null
                ? null
                : (this.rootElement.querySelector(
                      `#rio-debugger-navigation-button-${pageName}`
                  ) as HTMLElement);

        this._updateNavigationMarker(oldButton, newButton);

        // Update the state
        this.displayedPageName = pageName;

        // Done?
        if (pageName === null) {
            return;
        }

        // Add the new page
        if (pageName === 'componentTree') {
            this.currentDriver = new DebuggerTreeDriver();
            this.contentContainer.appendChild(this.currentDriver.rootElement);
        } else {
            console.error(`Unknown debugger page: ${pageName}`);
        }
    }

    makeNavButton(text: string, icon: string, navTarget: string) {
        // Create the element
        let navBar = this.rootElement.querySelector(
            '.rio-debugger-navigation'
        ) as HTMLElement;

        let element = document.createElement('div');
        element.id = `rio-debugger-navigation-button-${navTarget}`;
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

        // Navigate when clicked
        element.addEventListener('click', (event) => {
            event.stopPropagation();

            // If this page is already selected deselect it
            if (this.displayedPageName === navTarget) {
                this.navigateTo(null);
            }
            // Otherwise switch to it
            else {
                this.navigateTo(navTarget);
            }
        });
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
