rootWidget = "{root_widget}";

initialStates = "{initial_states}";


function colorToCss(color) {
    const [r, g, b, a] = color;
    return `rgba(${r * 255}, ${g * 255}, ${b * 255}, ${a})`;
}


function fillToCss(fill) {
    // Solid Color
    if (fill.type === "solid") {
        return colorToCss(fill.color);
    }

    // Linear Gradient
    if (fill.type === "linearGradient") {
        if (fill.stops.length == 1) {
            return colorToCss(fill.stops[0][0]);
        }

        var stopStrings = [];
        for (var i = 0; i < fill.stops.length; i++) {
            var color = fill.stops[i][0];
            var position = fill.stops[i][1];
            stopStrings.push(`${colorToCss(color)} ${position * 100}%`);
        }

        return `linear-gradient(${fill.angleDegrees}deg, ${stopStrings.join(', ')})`;
    }

    // Unsupported
    throw `Unsupported fill type: ${fill.type}`;
}


function buildText(widget) {
    var element = document.createElement("div");
    return element;
}

function updateText(element, state) {
    if (state.text !== undefined) {
        element.innerText = state.text;
    }

    if (state.multiline !== undefined) {
        element.style.whiteSpace = state.multiline ? "normal" : "nowrap";
    }
}

function buildRow(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-row");

    for (const child of widget.children) {
        element.appendChild(buildWidget(child));
    }

    return element;
}

function updateRow(element, state) { }

function buildColumn(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-column");

    for (const child of widget.children) {
        element.appendChild(buildWidget(child));
    }

    return element;
}

function updateColumn(element, state) { }

function buildRectangle(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-rectangle");
    return element;
}

function updateRectangle(element, state) {
    if (state.fill !== undefined) {
        element.style.background = fillToCss(state.fill);
    }

    if (state.cornerRadius !== undefined) {
        const [topLeft, topRight, bottomRight, bottomLeft] = state.cornerRadius;
        element.style.borderRadius = `${topLeft}em ${topRight}em ${bottomRight}em ${bottomLeft}em`;
    }
}

function buildStack(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-stack");

    for (var ii = 0; ii < widget.children.length; ii++) {
        const childElement = buildWidget(widget.children[ii]);
        childElement.style.zIndex = ii + 1;
        element.appendChild(childElement);
    }

    return element;
}

function updateStack(element, state) { }

function buildMargin(widget) {
    var element = document.createElement("div");
    element.appendChild(buildWidget(widget.child));
    return element;
}

function updateMargin(state) { }

function buildAlign(widget) {
    var element = document.createElement("div");
    element.appendChild(buildWidget(widget.child));
    return element;
}

function updateAlign(element, state) {
    // style_props = ""

    // if self.align_x is not None:
    //     style_props += f"justify-content: {self.align_x*100}%;"

    // if self.align_y is not None:
    //     style_props += f"align-items: {self.align_y*100}%;"

    // yield f'<div style="width: 100%; height: 100%; display: flex; {style_props}">'
    // yield from self.child._as_html()
    // yield "</div>"
}

widgetHandlers = {
    "text": [buildText, updateText],
    "row": [buildRow, updateRow],
    "column": [buildColumn, updateColumn],
    "rectangle": [buildRectangle, updateRectangle],
    "stack": [buildStack, updateStack],
    "margin": [buildMargin, updateMargin],
    "align": [buildAlign, updateAlign],
}

function buildWidget(widget) {
    // Make sure the widget type is valid
    const callbacks = widgetHandlers[widget.type];

    if (callbacks === undefined) {
        throw "Cannot build unknown widget type: " + widget.type;
    }

    // Build the widget
    const [build, update] = callbacks;
    var result = build(widget);

    // Add a unique ID to the widget
    result.id = "pygui-id-" + widget.id;

    // Store the widget's type in the element. This is used by the update
    // function to determine the correct update function to call.
    result.setAttribute("data-pygui-type", widget.type);

    return result;
}

function updateWidget(widgetId, state) {
    // Get the widget element
    const element = document.getElementById("pygui-id-" + widgetId);

    // Get the appropriate update function
    const widgetType = element.getAttribute("data-pygui-type");
    const [build, update] = widgetHandlers[widgetType];

    // Update
    update(element, state);
}

function main() {
    // Build the HTML document
    var body = document.getElementsByTagName("body")[0];
    body.appendChild(buildWidget(rootWidget));

    // Apply the initial states
    for (const [widgetId, state] of Object.entries(initialStates)) {
        updateWidget(widgetId, state);
    }
}

main();
