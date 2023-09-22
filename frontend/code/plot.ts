import { fillToCss } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

type PlotState = WidgetState & {
    _type_: 'plot';
    plotJson: string;
    boxStyle: object;
};

function loadPlotly(callback) {
    if (typeof Plotly === 'undefined') {
        console.log('Fetching plotly.js');
        let script = document.createElement('script');
        script.src = '/rio/asset/plotly.min.js';
        script.onload = callback;
        document.head.appendChild(script);
    } else {
        callback();
    }
}

function applyStyle(element: HTMLElement, style: any) {
    // Fill
    element.style.background = fillToCss(style.fill);

    // Corner radius
    element.style.borderRadius = `${style.cornerRadius[0]}em ${style.cornerRadius[1]}em ${style.cornerRadius[2]}em ${style.cornerRadius[3]}em`;

    // The remaining values are currently not supported.
}

export class PlotWidget extends WidgetBase {
    state: Required<PlotState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.style.display = 'inline-block';

        // Force the corner radius to be applied to plotly
        element.style.overflow = 'hidden';
        return element;
    }

    updateElement(element: HTMLElement, deltaState: PlotState): void {
        element.innerHTML = '';
        loadPlotly(() => {
            let plotJson = JSON.parse(deltaState.plotJson);
            Plotly.newPlot(element, plotJson.data, plotJson.layout, {
                responsive: true,
            });

            applyStyle(element, deltaState.boxStyle);
        });
    }
}
