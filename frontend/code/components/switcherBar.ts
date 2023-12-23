import { ComponentBase, ComponentState } from './componentBase';
import { MDCRipple } from '@material/ripple';
import { ColorSet, TextStyle } from '../models';
import { applyColorSet } from '../designApplication';
import { getTextDimensions } from '../layoutHelpers';
import { LayoutContext } from '../layouting';
import { textStyleToCss } from '../cssUtils';
import { pixelsPerEm } from '../app';

const ACCELERATION: number = 250; // rem/s^2

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
    selectedName?: string;
};

export class SwitcherBarComponent extends ComponentBase {
    state: Required<SwitcherBarState>;

    private innerElement: HTMLElement;
    private markerElement: HTMLElement;
    private backgroundOptionsElement: HTMLElement;
    private markerOptionsElement: HTMLElement;
    private isInitialized: boolean = false;

    // The requested width of each entry's name
    private nameWidths: number[];

    // The requested height of each entry's name
    private nameHeights: number[];

    // True if at least one of the entries has an icon
    private hasAtLeastOneIcon: boolean;

    // Marker animation state
    private markerCurLeft: number = 0;
    private markerCurTop: number = 0;
    private markerCurWidth: number = 0;
    private markerCurHeight: number = 0;

    private markerCurVelocity: number = 0;

    private animationIsRunning: boolean = false;
    private lastAnimationTickAt: number = 0;

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

        // Move the marker
        this.markerElement.style.left = `${left}px`;
        this.markerElement.style.top = `${top}px`;
        this.markerElement.style.width = `${width}px`;
        this.markerElement.style.height = `${height}px`;

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
    _updateMarkerInstantlyIfAnimationIsntRunning(): void {
        if (this.animationIsRunning) {
            return;
        }

        let target = this._getMarkerTarget();
        this._instantlyMoveMarkerTo(target[0], target[1], target[2], target[3]);
    }

    _animationWorker(): void {
        console.log('\n\n\nITER');
        // How much time has passed
        let now = Date.now();
        let deltaTime = (now - this.lastAnimationTickAt) / 1000;
        this.lastAnimationTickAt = now;

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
        console.log('target', target);
        console.log('curPos', curPos);
        console.log('targetPos', targetPos);
        console.log('signedRemainingDistance', signedRemainingDistance);

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
        console.log('accelerationFactor', accelerationFactor);

        let currentAcceleration =
            acceleration *
            accelerationFactor *
            Math.sign(signedRemainingDistance);

        // Update the velocity
        this.markerCurVelocity += currentAcceleration * deltaTime;
        let deltaDistance = this.markerCurVelocity * deltaTime;
        console.log('deltaDistance', deltaDistance);

        // Arrived?
        let t;
        if (Math.abs(deltaDistance) > Math.abs(signedRemainingDistance)) {
            t = 1;
            this.animationIsRunning = false;
        } else {
            t = deltaDistance / signedRemainingDistance;
            requestAnimationFrame(this._animationWorker.bind(this));
        }
        console.log('t', t);

        // Update the marker
        this._instantlyMoveMarkerTo(
            this.markerCurLeft + t * (target[0] - this.markerCurLeft),
            this.markerCurTop + t * (target[1] - this.markerCurTop),
            this.markerCurWidth + t * (target[2] - this.markerCurWidth),
            this.markerCurHeight + t * (target[3] - this.markerCurHeight)
        );
    }

    startAnimationIfNotRunning(): void {
        if (this.animationIsRunning) {
            return;
        }

        this.lastAnimationTickAt = Date.now();
        this.animationIsRunning = true;
        this.markerCurVelocity = 0;
        requestAnimationFrame(this._animationWorker.bind(this));
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
                this.state.selectedName = name;
                this.startAnimationIfNotRunning();
                this.sendMessageToBackend({
                    name: name,
                });
            });
        }

        return result;
    }

    updateElement(element: HTMLElement, deltaState: SwitcherBarState): void {
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
            this.markerOptionsElement = this.backgroundOptionsElement.cloneNode(
                true
            ) as HTMLElement;
            this.markerElement.innerHTML = '';
            this.markerElement.appendChild(this.markerOptionsElement);

            // Re-layout
            this._updateMarkerInstantlyIfAnimationIsntRunning();
            this.makeLayoutDirty();
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

            this.backgroundOptionsElement.style.flexDirection = flexDirection;
            this.markerOptionsElement.style.flexDirection = flexDirection;

            // Re-layout
            this._updateMarkerInstantlyIfAnimationIsntRunning();
            this.makeLayoutDirty();
        }

        // Spacing
        if (deltaState.spacing !== undefined) {
            this._updateMarkerInstantlyIfAnimationIsntRunning();
            this.makeLayoutDirty();
        }

        // Does any of the changes affect the marker's placement?
        if (deltaState.selectedName !== undefined) {
            // Don't trigger an animation if this is the first time the
            // component is being updated
            if (this.isInitialized) {
                this.startAnimationIfNotRunning();
            } else {
                this._updateMarkerInstantlyIfAnimationIsntRunning();
                this.isInitialized = true;
            }
        }

        if (
            deltaState.names !== undefined ||
            deltaState.icon_svg_sources !== undefined
        ) {
            this._updateMarkerInstantlyIfAnimationIsntRunning();
        }
    }

    updateRequestedWidth(ctx: LayoutContext): void {
        if (this.state.orientation == 'horizontal') {
            this.requestedWidth =
                this.state.spacing * (this.nameWidths.length - 1) +
                ITEM_MARGIN * (this.nameWidths.length * 2);

            // Individual items
            for (let i = 0; i < this.nameWidths.length; i++) {
                this.requestedWidth += this.nameWidths[i];
            }
        } else {
            // Individual items
            this.requestedWidth = 0;
            for (let i = 0; i < this.nameWidths.length; i++) {
                this.requestedWidth = Math.max(
                    this.requestedWidth,
                    this.nameWidths[i]
                );
            }

            // Margin
            this.requestedWidth += ITEM_MARGIN * 2;
        }
    }

    updateRequestedHeight(ctx: LayoutContext): void {
        if (this.state.orientation == 'horizontal') {
            // Individual items
            this.requestedHeight = 0;
            for (let i = 0; i < this.nameHeights.length; i++) {
                this.requestedHeight = Math.max(
                    this.requestedHeight,
                    this.nameHeights[i]
                );
            }

            // Margin
            this.requestedHeight += ITEM_MARGIN * 2;

            // Icons, if any
            if (this.hasAtLeastOneIcon) {
                this.requestedHeight += ICON_HEIGHT;
            }
        } else {
            // Spacing + margin
            this.requestedHeight =
                this.state.spacing * (this.nameHeights.length - 1) +
                ITEM_MARGIN * (this.nameHeights.length * 2);

            // Individual items
            for (let i = 0; i < this.nameHeights.length; i++) {
                this.requestedHeight += this.nameHeights[i];
            }

            // Icons, if any
            if (this.hasAtLeastOneIcon) {
                this.requestedHeight += ICON_HEIGHT * this.nameHeights.length;
            }
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Update layouts
        this.backgroundOptionsElement.style.height = `${this.allocatedHeight}rem`;
        this.markerOptionsElement.style.height = `${this.allocatedHeight}rem`;

        if (this.state.orientation == 'horizontal') {
            let additionalHeight = this.allocatedHeight - this.requestedHeight;
            this.innerElement.style.left = '0';
            this.innerElement.style.top = `${additionalHeight / 2}rem`;
        } else {
            let additionalWidth = this.allocatedWidth - this.requestedWidth;
            this.innerElement.style.left = `${additionalWidth / 2}rem`;
            this.innerElement.style.top = '0';
        }

        // Reposition the marker
        this._updateMarkerInstantlyIfAnimationIsntRunning();
    }
}
