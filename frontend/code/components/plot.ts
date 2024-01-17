import { fillToCss } from '../cssUtils';
import { LayoutContext } from '../layouting';
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
    boxStyle: object;
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

function applyStyle(element: HTMLElement, style: any) {
    // Fill
    Object.assign(element.style, fillToCss(style.fill));

    // Corner radius
    element.style.borderRadius = `${style.cornerRadius[0]}em ${style.cornerRadius[1]}em ${style.cornerRadius[2]}em ${style.cornerRadius[3]}em`;

    // The remaining values are currently not supported.
}

export class PlotComponent extends ComponentBase {
    state: Required<PlotState>;

    private plotlyPlot: any = null;

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

            if (deltaState.plot.type === 'plotly') {
                let plot = deltaState.plot;

                loadPlotly(() => {
                    let plotJson = JSON.parse(plot.json);
                    this.plotlyPlot = window['Plotly'].newPlot(
                        this.element,
                        plotJson.data,
                        plotJson.layout
                        // {
                        //     responsive: true,
                        // }
                    );

                    let plotElement = this.element
                        .firstElementChild as HTMLElement;
                    plotElement.style.width = '100%';
                    plotElement.style.height = '100%';
                });
            } else {
                this.plotlyPlot = null;

                this.element.innerHTML = deltaState.plot.svg;

                let svgElement = this.element.querySelector(
                    'svg'
                ) as SVGElement;

                svgElement.style.width = '100%';
                svgElement.style.height = '100%';
            }
        }

        if (deltaState.boxStyle !== undefined) {
            applyStyle(this.element, deltaState.boxStyle);
        }
    }

    updateAllocatedHeight(ctx: LayoutContext): void {
        // Plotly is too dumb to layout itself. Help them out.
        if (this.plotlyPlot !== null) {
            window['Plotly'].Plots.resize(this.plotlyPlot);
            console.debug('Resized plotly plot');
        }
    }
}
