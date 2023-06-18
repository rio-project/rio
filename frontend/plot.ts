import { WidgetBase, WidgetState } from './widgetBase';

type PlotState = WidgetState & {
    _type_: 'plot';
    plotJson?: string;
};

function loadPlotly(callback) {
    if (typeof Plotly === 'undefined') {
        console.log('Fetching plotly.js');
        let script = document.createElement('script');
        script.src = '/reflex/asset/plotly.min.js';
        script.onload = callback;
        document.head.appendChild(script);
    } else {
        callback();
    }
}

export class PlotWidget extends WidgetBase {
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.style.display = 'inline-block';
        return element;
    }

    updateElement(element: HTMLElement, deltaState: PlotState): void {
        if (deltaState.plotJson !== undefined) {
            element.innerHTML = '';
            loadPlotly(() => {
                let plotJson = JSON.parse(deltaState.plotJson);
                Plotly.newPlot(element, plotJson.data, plotJson.layout, {
                    responsive: true,
                });
            });
        }
    }
}
