import hljs from 'highlight.js/lib/common';
import { componentsById } from '../componentManagement';
import { getElementDimensions } from '../layoutHelpers';
import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { applyIcon } from '../designApplication';
import { commitCss, disableTransitions, enableTransitions } from '../utils';

// Layouting variables needed by both JS and CSS
const MAIN_GAP = 1;
const BOX_PADDING = 1;
const ARROW_SIZE = 3;
const ADDITIONAL_SPACE = (BOX_PADDING * 2 + MAIN_GAP) * 2 + ARROW_SIZE;

export type CodeExplorerState = ComponentState & {
    _type_: 'CodeExplorer-builtin';
    source_code?: string;
    build_result?: ComponentId;
    line_indices_to_component_keys: (string | null)[];
};

export class CodeExplorerComponent extends ComponentBase {
    state: Required<CodeExplorerState>;

    private sourceCodeElement: HTMLElement;
    private arrowElement: HTMLElement;
    private buildResultElement: HTMLElement;

    private highlighterElement: HTMLElement;

    private sourceCodeDimensions: [number, number];

    createElement(): HTMLElement {
        // Build the HTML
        let element = document.createElement('div');
        element.classList.add('rio-code-explorer');

        element.innerHTML = `
            <div class="rio-code-explorer-source-code"></div>
            <div class="rio-code-explorer-arrow"></div>
            <div class="rio-code-explorer-build-result"></div>
        `;

        this.highlighterElement = document.createElement('div');
        this.highlighterElement.classList.add('rio-code-explorer-highlighter');

        // Expose the elements
        [this.sourceCodeElement, this.arrowElement, this.buildResultElement] =
            Array.from(element.children) as HTMLElement[];

        // Finish initialization
        this.sourceCodeElement.style.padding = `${BOX_PADDING}rem`;

        element.style.gap = `${MAIN_GAP}rem`;

        this.arrowElement.style.width = `${ARROW_SIZE}rem`;
        this.arrowElement.style.height = `${ARROW_SIZE}rem`;

        applyIcon(
            this.arrowElement,
            'arrow-right-alt:fill',
            'var(--rio-local-text-color)'
        );

        return element;
    }

    updateElement(
        deltaState: CodeExplorerState,
        latentComponents: Set<ComponentBase>
    ): void {
        // Update the source
        if (deltaState.source_code !== undefined) {
            let hlResult = hljs.highlight(deltaState.source_code, {
                language: 'python',
                ignoreIllegals: true,
            });
            this.sourceCodeElement.innerHTML = hlResult.value;

            // Remember the dimensions now, for faster layouting
            this.sourceCodeDimensions = getElementDimensions(
                this.sourceCodeElement
            );

            // Connect event handlers
            this._connectHighlightEventListeners();
        }

        // Update the child
        if (deltaState.build_result !== undefined) {
            // Remove the highlighter prior to removing the child, as
            // `replaceOnlyChild` expects there to be at most one element
            this.highlighterElement.remove();

            // Update the child
            this.replaceOnlyChild(
                latentComponents,
                deltaState.build_result,
                this.buildResultElement
            );

            // Position it, so this doesn't happen every time during layouting
            let buildResultElement = componentsById[deltaState.build_result]!;
            buildResultElement.element.style.removeProperty('left');
            buildResultElement.element.style.removeProperty('top');

            // (Re-)Add the highlighter
            this.buildResultElement.appendChild(this.highlighterElement);
        }
    }

    private _connectHighlightEventListeners(): void {
        // The text is a mix of spans and raw text. Some of them may extend over
        // multiple lines. Split them up, and use this opportunity to wrap all
        // text in spans as well.
        let lineIndex = 0;

        let elementsBefore = Array.from(this.sourceCodeElement.childNodes);
        this.sourceCodeElement.innerHTML = '';

        for (let element of elementsBefore) {
            // If this is just a plain text element, wrap it in a span
            let multiSpan: HTMLSpanElement;

            if (element instanceof Text) {
                let span = document.createElement('span');
                span.textContent = element.textContent!;
                multiSpan = span;
            } else {
                console.assert(element instanceof HTMLSpanElement);
                multiSpan = element as HTMLSpanElement;
            }

            // Re-add the spans, keeping track of the line
            let lines = multiSpan.textContent!.split('\n');

            for (let ii = 0; ii < lines.length; ii++) {
                if (ii !== 0) {
                    lineIndex += 1;
                    this.sourceCodeElement.appendChild(
                        document.createTextNode('\n')
                    );
                }

                let singleSpan = multiSpan.cloneNode() as HTMLSpanElement;
                singleSpan.innerText = lines[ii];
                singleSpan.dataset.lineIndex = lineIndex.toString();
                this.sourceCodeElement.appendChild(singleSpan);

                // Add the event listeners
                ((currentLineIndex) => {
                    singleSpan.addEventListener('mouseenter', () => {
                        this._onEnterLine(currentLineIndex);
                    });
                })(lineIndex);

                singleSpan.addEventListener('mouseleave', () => {
                    this._onEnterLine(null);
                });
            }
        }
    }

    private _onEnterLine(line: number | null): void {
        let key: string | null = null;

        // Which key should be highlighted?
        if (line !== null) {
            key = this.state.line_indices_to_component_keys[line];
        }

        // Find the component to highlight
        let targetComponent;
        if (key !== null) {
            targetComponent = this.findComponentByKey(
                componentsById[this.state.build_result]!,
                key
            );

            if (targetComponent === null) {
                console.error(
                    `CodeExplorer could not find component with key ${key}`
                );
                key = null;
            }
        }

        // Nothing to highlight
        if (key === null) {
            this.highlighterElement.style.opacity = '0';
            return;
        }

        // Highlight the target
        let rootRect = this.buildResultElement.getBoundingClientRect();
        let targetRect = targetComponent.element.getBoundingClientRect();

        // If the highlighter is currently completely invisible, teleport it.
        // Make sure to check the computed, current opacity, since it's animated
        let teleport = getComputedStyle(this.highlighterElement).opacity == '0'; // Note the == instead of ===

        // FIXME: Teleport isn't working
        // if (teleport) {
        //     disableTransitions(this.highlighterElement);
        //     commitCss(this.highlighterElement);
        // }

        this.highlighterElement.style.left = `${
            targetRect.left - rootRect.left
        }px`;
        this.highlighterElement.style.top = `${
            targetRect.top - rootRect.top
        }px`;
        this.highlighterElement.style.width = `${targetRect.width}px`;
        this.highlighterElement.style.height = `${targetRect.height}px`;

        // enableTransitions(this.highlighterElement);

        this.highlighterElement.style.opacity = '1';
    }

    private findComponentByKey(
        currentComponent: ComponentBase,
        key: string
    ): ComponentBase | null {
        // Found it?
        if (currentComponent.state._key_ === key) {
            return currentComponent;
        }

        // Nope, recurse
        for (let child of currentComponent.children) {
            let result = this.findComponentByKey(child, key);

            if (result !== null) {
                return result;
            }
        }

        // Exhausted all children
        return null;
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        let buildResultElement = componentsById[this.state.build_result]!;
        this.naturalWidth =
            this.sourceCodeDimensions[0] +
            ADDITIONAL_SPACE +
            buildResultElement.requestedWidth;
    }

    updateAllocatedWidth(ctx: LayoutContext): void {
        let buildResultElement = componentsById[this.state.build_result]!;
        buildResultElement.allocatedWidth = buildResultElement.requestedWidth;
    }

    updateNaturalHeight(ctx: LayoutContext): void {
        let buildResultElement = componentsById[this.state.build_result]!;
        this.naturalHeight = Math.max(
            this.sourceCodeDimensions[1],
            buildResultElement.requestedHeight
        );
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        let buildResultElement = componentsById[this.state.build_result]!;
        buildResultElement.allocatedHeight = Math.max(
            buildResultElement.requestedHeight,
            this.allocatedHeight
        );

        // Positioning the child is already done in `updateElement`
    }
}
