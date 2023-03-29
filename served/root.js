rootWidget = "{root_widget}";

initialStates = "{initial_states}";


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
    return element;
}

function updateRectangle(element, state) {
    if (state.fill !== undefined) {
        element.style.backgroundColor = "red";
    }

    if (state.cornerRadius !== undefined) {
        const [topLeft, topRight, bottomRight, bottomLeft] = state.cornerRadius;
        element.style.borderRadius = `${topLeft}em ${topRight}em ${bottomRight}em ${bottomLeft}em`;
    }
}

function buildStack(widget) {
    var element = document.createElement("div");

    for (const child of widget.children) {
        element.appendChild(buildWidget(child));
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

function updateAlign(element, state) { }

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
