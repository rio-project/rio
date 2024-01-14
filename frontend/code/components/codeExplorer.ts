import hljs from 'highlight.js/lib/common';
import { componentsById } from '../componentManagement';
import { getElementDimensions } from '../layoutHelpers';
import { LayoutContext } from '../layouting';
import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';
import { applyIcon } from '../designApplication';

// Layouting variables needed by both JS and CSS
const CODE_VIEW_WIDTH = 50;
const MAIN_GAP = 1;
const ARROW_SIZE = 3;
const MAIN_SPACING = MAIN_GAP * 2 + ARROW_SIZE;

export type CodeExplorerState = ComponentState & {
    _type_: 'CodeExplorer-builtin';
    source_code?: string;
    build_result?: ComponentId;
};

export class CodeExplorerComponent extends ComponentBase {
    state: Required<CodeExplorerState>;

    private sourceCodeElement: HTMLElement;
    private arrowElement: HTMLElement;
    private buildResultElement: HTMLElement;

    private highlighter: HTMLElement;

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

        this.highlighter = document.createElement('div');
        this.highlighter.classList.add(
            'rio-debugger-component-highlighter',
            'rio-code-explorer-highlighter'
        );

        // Expose the elements
        [this.sourceCodeElement, this.arrowElement, this.buildResultElement] =
            Array.from(element.children) as HTMLElement[];

        // Finish initialization
        element.style.gap = `${MAIN_GAP}rem`;

        this.arrowElement.style.width = `${ARROW_SIZE}rem`;
        this.arrowElement.style.height = `${ARROW_SIZE}rem`;

        applyIcon(
            this.arrowElement,
            'arrow-right-alt:fill',
            'var(--rio-local-text-color)'
        );

        // Highlight the source code when hovered
        this.sourceCodeElement.addEventListener(
            'mousemove',
            this._onMouseMove.bind(this)
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

            this.sourceCodeDimensions = getElementDimensions(
                this.sourceCodeElement
            );
        }

        // Update the child
        if (deltaState.build_result !== undefined) {
            this.replaceOnlyChild(
                latentComponents,
                deltaState.build_result,
                this.buildResultElement
            );

            // Position it, so this doesn't happen every time during layouting
            let buildResultElement = componentsById[deltaState.build_result]!;
            buildResultElement.element.style.removeProperty('left');
            buildResultElement.element.style.removeProperty('top');
        }
    }

    private _findLine(event: MouseEvent): number {
        let line = 0;

        let lineElement = this.sourceCodeElement.firstElementChild;
        while (lineElement) {
            let rect = lineElement.getBoundingClientRect();
            if (event.clientY < rect.bottom) {
                break;
            }

            line++;
            lineElement = lineElement.nextElementSibling;
        }

        return line;
    }

    private _onMouseMove(event: MouseEvent): void {
        // Find the line that's being hovered
        let line = this._findLine(event);

        console.debug(`You're in line ${line}`);

        // Add the highlighter if it's not in the document yet
        if (!this.highlighter.parentElement) {
            document.body.appendChild(this.highlighter);
        }

        // Move the highlighter
        let targetRect = this.buildResultElement.getBoundingClientRect();

        this.highlighter.style.left = `${targetRect.left}px`;
        this.highlighter.style.top = `${targetRect.top + line * 16}px`;
        this.highlighter.style.width = `${targetRect.width}px`;
        this.highlighter.style.height = '16px';
    }

    updateNaturalWidth(ctx: LayoutContext): void {
        let buildResultElement = componentsById[this.state.build_result]!;
        this.naturalWidth =
            this.sourceCodeDimensions[0] +
            MAIN_SPACING +
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
