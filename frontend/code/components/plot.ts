import { pixelsPerEm } from '../app';
import { fillToCss } from '../cssUtils';
import { LayoutContext } from '../layouting';
import { Fill } from '../models';
import { ComponentBase, ComponentState } from './componentBase';

type PlotlyPlot = {
    type: 'plotly';
    json: string;
};

type MatplotlibPlot = {
    type: 'matplotlib';
    svg: string;
};

type PlotState = ComponentState & {
    _type_: 'Plot-builtin';
    plot: PlotlyPlot | MatplotlibPlot;
    background: Fill | null;
    corner_radius?: [number, number, number, number];
};

function loadPlotly(callback: () => void): void {
    if (typeof window['Plotly'] !== 'undefined') {
        callback();
        return;
    }

    console.log('Fetching plotly.js');
    let script = document.createElement('script');
    script.src = '/rio/asset/plotly.min.js';
    script.onload = callback;
    document.head.appendChild(script);
}

export class PlotComponent extends ComponentBase {
    state: Required<PlotState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-plot');
        return element;
    }

    updateElement(
        deltaState: PlotState,
        latentComponents: Set<ComponentBase>
    ): void {
        if (deltaState.plot !== undefined) {
            this.element.innerHTML = '';

            // Plotly
            if (deltaState.plot.type === 'plotly') {
                let plot = deltaState.plot;

                loadPlotly(() => {
                    let plotJson = JSON.parse(plot.json);
                    window['Plotly'].newPlot(
                        this.element,
                        plotJson.data,
                        plotJson.layout
                    );

                    this.updatePlotlyLayout();
                });
            }
            // Matplotlib (Just a SVG)
            else {
                this.element.innerHTML = deltaState.plot.svg;

                let svgElement = this.element.querySelector(
                    'svg'
                ) as SVGElement;

                svgElement.style.width = '100%';
                svgElement.style.height = '100%';
            }
        }

        if (deltaState.background === null) {
            this.element.style.background = 'var(--rio-local-plain-bg-variant)';
        } else if (deltaState.background !== undefined) {
            Object.assign(this.element.style, fillToCss(deltaState.background));
        }

        if (deltaState.corner_radius !== undefined) {
            let [topLeft, topRight, bottomRight, bottomLeft] =
                deltaState.corner_radius;

            this.element.style.borderRadius = `${topLeft}rem ${topRight}rem ${bottomRight}rem ${bottomLeft}rem`;
        }
    }

    updatePlotlyLayout(): void {
        window['Plotly'].update(
            this.element,
            {},
            {
                width: this.allocatedWidth * pixelsPerEm,
                height: this.allocatedHeight * pixelsPerEm,
            }
        );
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Plotly is too dumb to layout itself. Help out.
        if (
            this.state.plot.type === 'plotly' &&
            window['Plotly'] !== undefined
        ) {
            this.updatePlotlyLayout();
        }
    }
}
