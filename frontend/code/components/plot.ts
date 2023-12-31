import { fillToCss } from '../cssUtils';
import { ComponentBase, ComponentState } from './componentBase';

type PlotlyPlot = {
    type: 'plotly';
    json: string;
};

type MatplotlibPlot = {
    type: 'matplotlib';
    image: string;
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
                    window['Plotly'].newPlot(
                        this.element,
                        plotJson.data,
                        plotJson.layout,
                        {
                            responsive: true,
                        }
                    );

                    let plotElement = this.element
                        .firstElementChild as HTMLElement;
                    plotElement.style.width = '100%';
                    plotElement.style.height = '100%';
                });
            } else {
                let imgElement = document.createElement('img');
                imgElement.src =
                    'data:image/png;base64,' + deltaState.plot.image;
                imgElement.style.maxWidth = '100%';
                imgElement.style.maxHeight = '100%';
                this.element.appendChild(imgElement);
            }
        }

        if (deltaState.boxStyle !== undefined) {
            applyStyle(this.element, deltaState.boxStyle);
        }
    }
}
