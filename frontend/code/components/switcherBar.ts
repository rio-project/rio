import { ComponentBase, ComponentState } from './componentBase';
import { MDCRipple } from '@material/ripple';
import { ColorSet, TextStyle } from '../models';
import { applyColorSet } from '../designApplication';
import { getTextDimensions } from '../layoutHelpers';
import { LayoutContext } from '../layouting';
import { textStyleToCss } from '../cssUtils';
import { pixelsPerEm } from '../app';
import { easeInOut } from '../easeFunctions';

const ACCELERATION: number = 350; // rem/s^2

const MARKER_FADE_DURATION: number = 0.18; // s

const ITEM_MARGIN: number = 0.5;
const SVG_HEIGHT: number = 1.8;
const ICON_MARGIN: number = 0.5;
const ICON_HEIGHT: number = SVG_HEIGHT + ICON_MARGIN;

const TEXT_STYLE: TextStyle = {
    fontName: 'Roboto',
    fill: [0, 0, 0, 1],
    fontSize: 1,
    italic: false,
    fontWeight: 'bold',
    underlined: false,
    allCaps: false,
};

const TEXT_STYLE_CSS_OPTIONS: object = textStyleToCss(TEXT_STYLE);

export type SwitcherBarState = ComponentState & {
    _type_: 'SwitcherBar-builtin';
    names?: string[];
    icon_svg_sources?: (string | null)[];
    color?: ColorSet;
    orientation?: 'horizontal' | 'vertical';
    spacing?: number;
    allow_none: boolean;
    selectedName?: string | null;
};

export class SwitcherBarComponent extends ComponentBase {
    state: Required<SwitcherBarState>;

    private innerElement: HTMLElement;
    private markerElement: HTMLElement;
    private backgroundOptionsElement: HTMLElement;
    private markerOptionsElement: HTMLElement;

    // The requested width of each entry's name
    private nameWidths: number[];

    // The requested height of each entry's name
    private nameHeights: number[];

    // True if at least one of the entries has an icon
    private hasAtLeastOneIcon: boolean;

    // Marker animation state
    private markerCurLeft: number;
    private markerCurTop: number;
    private markerCurWidth: number;
    private markerCurHeight: number;

    private markerCurVelocity: number;

    private moveAnimationIsRunning: boolean = false;
    private lastMoveAnimationTickAt: number = 0;

    // Marker fade animation state
    //
    // 0 if the marker is entirely invisible, 1 if it's entirely visible
    private fadeAnimationIsRunning: boolean = false;
    private markerVisibility: number = 0;
    private lastFadeAnimationTickAt: number = 0;

    // Allows to determine whether this is the first time the element is
    // being updated.
    private isInitialized: boolean = false;

    createElement(): HTMLElement {
        // Create the elements
        let elementOuter = document.createElement('div');
        elementOuter.classList.add('rio-switcher-bar');

        this.innerElement = document.createElement('div');
        elementOuter.appendChild(this.innerElement);

        this.markerElement = document.createElement('div');
        this.markerElement.classList.add('rio-switcher-bar-marker');

        return elementOuter;
    }

    /// Instantly move the marker to the given location
    _instantlyMoveMarkerTo(
        left: number,
        top: number,
        width: number,
        height: number
    ): void {
        // Update the stored values
        this.markerCurLeft = left;
        this.markerCurTop = top;
        this.markerCurWidth = width;
        this.markerCurHeight = height;

        // Account for the marker's resize animation
        let fadeT = easeInOut(this.markerVisibility);
        let scaledWidth = width * fadeT;
        let scaledHeight = height * fadeT;

        left += (width - scaledWidth) / 2;
        top += (height - scaledHeight) / 2;

        // Move the marker
        this.markerElement.style.left = `${left}px`;
        this.markerElement.style.top = `${top}px`;
        this.markerElement.style.width = `${scaledWidth}px`;
        this.markerElement.style.height = `${scaledHeight}px`;

        // Move the inner options in the opposite direction so they stay put
        this.markerOptionsElement.style.left = `-${left}px`;
        this.markerOptionsElement.style.top = `-${top}px`;
    }

    /// Fetch the target position of the marker
    _getMarkerTarget(): [number, number, number, number] {
        let selectedIndex = this.state.names.indexOf(this.state.selectedName!);
        let selectedElement = this.backgroundOptionsElement.children[
            selectedIndex
        ] as HTMLElement;

        return [
            selectedElement.offsetLeft,
            selectedElement.offsetTop,
            selectedElement.offsetWidth,
            selectedElement.offsetHeight,
        ];
    }

    /// Instantly move the marker to the currently selected item
    _moveMarkerInstantlyIfAnimationIsntRunning(): void {
        // Already transitioning?
        if (this.moveAnimationIsRunning) {
            return;
        }

        // Nowhere to move to
        if (this.state.selectedName === null) {
            return;
        }

        // Move it
        let target = this._getMarkerTarget();
        this._instantlyMoveMarkerTo(target[0], target[1], target[2], target[3]);
    }

    _moveAnimationWorker(): void {
        this.moveAnimationIsRunning = false;
        return;

        // The value may have switched to `null` since the animation has started
        if (this.state.selectedName === null) {
            this.moveAnimationIsRunning = false;
            return;
        }

        // How much time has passed
        let now = Date.now();
        let deltaTime = (now - this.lastMoveAnimationTickAt) / 1000;
        this.lastMoveAnimationTickAt = now;

        // Calculate the distance to the target
        let target = this._getMarkerTarget();

        let curPos: number, targetPos: number;
        if (this.state.orientation == 'horizontal') {
            curPos = this.markerCurLeft;
            targetPos = target[0];
        } else {
            curPos = this.markerCurTop;
            targetPos = target[1];
        }

        let signedRemainingDistance = targetPos - curPos;

        // Which direction to accelerate towards?
        let acceleration = ACCELERATION * pixelsPerEm;
        let accelerationFactor; // + means towards the target
        let brakingDistance =
            Math.pow(this.markerCurVelocity, 2) / (2 * acceleration);

        // Case: Moving away from the target
        if (
            Math.sign(signedRemainingDistance) !=
            Math.sign(this.markerCurVelocity)
        ) {
            accelerationFactor = 3;
        }
        // Case: Don't run over the target quite so hard
        else if (Math.abs(signedRemainingDistance) < brakingDistance) {
            accelerationFactor = -1;
        }
        // Case: Accelerate towards the target
        else {
            accelerationFactor = 1;
        }

        let currentAcceleration =
            acceleration *
            accelerationFactor *
            Math.sign(signedRemainingDistance);

        // Update the velocity
        this.markerCurVelocity += currentAcceleration * deltaTime;
        let deltaDistance = this.markerCurVelocity * deltaTime;

        // Arrived?
        let t;
        if (Math.abs(deltaDistance) > Math.abs(signedRemainingDistance)) {
            t = 1;
            this.moveAnimationIsRunning = false;
        } else {
            t = deltaDistance / signedRemainingDistance;
            requestAnimationFrame(this._moveAnimationWorker.bind(this));
        }

        // Update the marker
        this._instantlyMoveMarkerTo(
            this.markerCurLeft + t * (target[0] - this.markerCurLeft),
            this.markerCurTop + t * (target[1] - this.markerCurTop),
            this.markerCurWidth + t * (target[2] - this.markerCurWidth),
            this.markerCurHeight + t * (target[3] - this.markerCurHeight)
        );
    }

    /// High level function to update the marker. It will animate the marker as
    /// appropriate.
    makeMarkerMatchState(): void {
        // No value selected? Fade out
        if (this.state.selectedName === null) {
            this.startFadeAnimationIfNotRunning();
            return;
        }

        // If the marker is currently invisible, teleport it
        if (this.markerVisibility === 0) {
            let target = this._getMarkerTarget();
            this._instantlyMoveMarkerTo(
                target[0],
                target[1],
                target[2],
                target[3]
            );
        }
        // Otherwise animate it smoothly
        else {
            this.startMoveAnimationIfNotRunning();
        }

        // The marker must be visible. Fade in
        if (this.markerVisibility !== 1) {
            this.startFadeAnimationIfNotRunning();
        }
    }

    startMoveAnimationIfNotRunning(): void {
        if (this.moveAnimationIsRunning) {
            return;
        }

        this.lastMoveAnimationTickAt = Date.now();
        this.moveAnimationIsRunning = true;
        this.markerCurVelocity = 0;
        requestAnimationFrame(this._moveAnimationWorker.bind(this));
    }

    fadeAnimationWorker(): void {
        // Fade in or out?
        let target = this.state.selectedName === null ? 0 : 1;

        // How much time has passed
        let now = Date.now();
        let deltaTime = (now - this.lastFadeAnimationTickAt) / 1000;
        this.lastFadeAnimationTickAt = now;

        // Update the marker
        let amount =
            (Math.sign(target - this.markerVisibility) * deltaTime) /
            MARKER_FADE_DURATION;
        this.markerVisibility += amount;
        this.markerVisibility = Math.min(Math.max(this.markerVisibility, 0), 1);

        this._instantlyMoveMarkerTo(
            this.markerCurLeft,
            this.markerCurTop,
            this.markerCurWidth,
            this.markerCurHeight
        );

        console.debug(`FADE: ${this.markerVisibility}`);

        // Done?
        if (this.markerVisibility === target) {
            this.fadeAnimationIsRunning = false;
        } else {
            requestAnimationFrame(this.fadeAnimationWorker.bind(this));
        }
    }

    startFadeAnimationIfNotRunning(): void {
        // Already running?
        if (this.fadeAnimationIsRunning) {
            return;
        }

        // Start it
        this.fadeAnimationIsRunning = true;
        this.lastFadeAnimationTickAt = Date.now();
        requestAnimationFrame(this.fadeAnimationWorker.bind(this));
    }

    _buildContent(deltaState: SwitcherBarState): HTMLElement {
        let result = document.createElement('div');
        result.classList.add('rio-switcher-bar-options');
        Object.assign(result.style, TEXT_STYLE_CSS_OPTIONS);
        result.style.removeProperty('color');

        let names = deltaState.names ?? this.state.names;
        let iconSvgSources =
            deltaState.icon_svg_sources ?? this.state.icon_svg_sources;

        // Iterate over both
        for (let i = 0; i < names.length; i++) {
            let name = names[i];
            let iconSvg = iconSvgSources[i];

            let optionElement = document.createElement('div');
            optionElement.classList.add('rio-switcher-bar-option');
            optionElement.style.padding = `${ITEM_MARGIN}rem`;
            result.appendChild(optionElement);

            // Icon
            let iconElement;
            if (iconSvg !== null) {
                optionElement.innerHTML = iconSvg;
                iconElement = optionElement.children[0] as HTMLElement;
                iconElement.style.width = `${SVG_HEIGHT}rem`;
                iconElement.style.height = `${SVG_HEIGHT}rem`;
                iconElement.style.marginBottom = `${ICON_MARGIN}rem`;
                iconElement.style.fill = 'currentColor';
            }

            // Text
            let textElement = document.createElement('div');
            optionElement.appendChild(textElement);
            textElement.textContent = name;

            // Add a ripple effect
            MDCRipple.attachTo(optionElement);

            // Detect clicks
            optionElement.addEventListener('click', () => {
                // If this item was already selected, the new value may be `None`
                if (this.state.selectedName === name) {
                    if (this.state.allow_none) {
                        this.state.selectedName = null;
                    } else {
                        return;
                    }
                } else {
                    this.state.selectedName = name;
                }

                // Update the marker
                this.makeMarkerMatchState();

                // Notify the backend
                this.sendMessageToBackend({
                    name: this.state.selectedName,
                });
            });
        }

        return result;
    }

    updateElement(
        deltaState: SwitcherBarState,
        latentComponents: Set<ComponentBase>
    ): void {
        let markerPositionNeedsUpdate = false;
        let needsReLayout = false;

        // If the names have changed, update their sizes
        if (deltaState.names !== undefined) {
            this.nameWidths = [];
            this.nameHeights = [];

            for (let i = 0; i < deltaState.names.length; i++) {
                let name = deltaState.names[i];
                let size = getTextDimensions(name, TEXT_STYLE);
                this.nameWidths.push(size[0]);
                this.nameHeights.push(size[1]);
            }
        }

        // If any of the icon sources have changed, update the hasAtLeastOneIcon
        // flag
        if (deltaState.icon_svg_sources !== undefined) {
            this.hasAtLeastOneIcon = deltaState.icon_svg_sources.some(
                (x) => x !== null
            );
        }

        // Update the options
        if (
            deltaState.names !== undefined ||
            deltaState.icon_svg_sources !== undefined
        ) {
            this.innerElement.innerHTML = '';

            // Background content
            this.backgroundOptionsElement = this._buildContent(deltaState);
            this.innerElement.appendChild(this.backgroundOptionsElement);

            // Marker
            this.innerElement.appendChild(this.markerElement);

            // Marker content
            this.markerOptionsElement = this._buildContent(deltaState);
            this.markerElement.innerHTML = '';
            this.markerElement.appendChild(this.markerOptionsElement);

            // Request some updates
            markerPositionNeedsUpdate = true;
            needsReLayout = true;
        }

        // Color
        if (deltaState.color !== undefined) {
            applyColorSet(
                this.markerElement,
                deltaState.color === 'keep'
                    ? 'accent-to-plain'
                    : deltaState.color
            );
        }

        // Orientation
        if (deltaState.orientation !== undefined) {
            let flexDirection =
                deltaState.orientation == 'vertical' ? 'column' : 'row';

            this.element.style.flexDirection = flexDirection;
            this.backgroundOptionsElement.style.flexDirection = flexDirection;
            this.markerOptionsElement.style.flexDirection = flexDirection;

            // Request some updates
            markerPositionNeedsUpdate = true;
            needsReLayout = true;
        }

        // Spacing
        if (deltaState.spacing !== undefined) {
            markerPositionNeedsUpdate = true;
            needsReLayout = true;
        }

        // If the selection has changed make sure to move the marker
        if (deltaState.selectedName !== undefined) {
            if (this.isInitialized) {
                this.state.selectedName = deltaState.selectedName;
                this.makeMarkerMatchState();
            } else {
                markerPositionNeedsUpdate = true;
                this.markerVisibility =
                    deltaState.selectedName === null ? 0 : 1;
            }
        }

        // Any future updates are not the first
        this.isInitialized = true;

        console.debug('POST UPDATE', markerPositionNeedsUpdate, needsReLayout);

        // Perform any requested updates
        setTimeout(() => {
            Object.assign(this.state, deltaState);

            console.debug(
                'Updating to ',
                markerPositionNeedsUpdate,
                needsReLayout,
                this.state
            );

            if (markerPositionNeedsUpdate) {
                this._moveMarkerInstantlyIfAnimationIsntRunning();
            }

            if (needsReLayout) {
                this.makeLayoutDirty();
            }
        }, 0);
    }

    /// Updates the layout of contained HTML elements:
    /// - Make sure the two elements containing the SwitcherBar's content take up
    ///   the entire major axis.
    /// - Center the inner element on the minor axis.
    updateContentLayout() {
        // Account for the orientation
        let width, height;
        if (this.state.orientation == 'horizontal') {
            width = `${this.allocatedWidth}rem`;
            height = '';
        } else {
            width = '';
            height = `${this.allocatedHeight}rem`;
        }

        // Assign the values
        this.backgroundOptionsElement.style.width = width;
        this.backgroundOptionsElement.style.height = height;

        this.markerOptionsElement.style.width = width;
        this.markerOptionsElement.style.height = height;
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        if (this.state.orientation == 'horizontal') {
            this.naturalWidth =
                this.state.spacing * (this.nameWidths.length - 1) +
                ITEM_MARGIN * (this.nameWidths.length * 2);

            // Individual items
            for (let i = 0; i < this.nameWidths.length; i++) {
                this.naturalWidth += this.nameWidths[i];
            }
        } else {
            // Individual items
            this.naturalWidth = 0;
            for (let i = 0; i < this.nameWidths.length; i++) {
                this.naturalWidth = Math.max(
                    this.naturalWidth,
                    this.nameWidths[i]
                );
            }

            // Margin
            this.naturalWidth += ITEM_MARGIN * 2;
        }
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        if (this.state.orientation == 'horizontal') {
            // Individual items
            this.naturalHeight = 0;
            for (let i = 0; i < this.nameHeights.length; i++) {
                this.naturalHeight = Math.max(
                    this.naturalHeight,
                    this.nameHeights[i]
                );
            }

            // Margin
            this.naturalHeight += ITEM_MARGIN * 2;

            // Icons, if any
            if (this.hasAtLeastOneIcon) {
                this.naturalHeight += ICON_HEIGHT;
            }
        } else {
            // Spacing + margin
            this.naturalHeight =
                this.state.spacing * (this.nameHeights.length - 1) +
                ITEM_MARGIN * (this.nameHeights.length * 2);

            // Individual items
            for (let i = 0; i < this.nameHeights.length; i++) {
                this.naturalHeight += this.nameHeights[i];
            }

            // Icons, if any
            if (this.hasAtLeastOneIcon) {
                this.naturalHeight += ICON_HEIGHT * this.nameHeights.length;
            }
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Update layouts
        this.updateContentLayout();

        // Reposition the marker
        this._moveMarkerInstantlyIfAnimationIsntRunning();
    }
}
