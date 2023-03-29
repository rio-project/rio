rootWidget = "{root_widget}";

initialStates = "{initial_states}";


function buildText(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-text");
    element.innerText = "TEXT!";
    return element;
}

function updateText(state) { }

function buildRow(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-row");

    for (const child of widget.children) {
        element.appendChild(buildWidget(child));
    }

    return element;
}

function updateRow(state) { }

function buildColumn(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-column");

    for (const child of widget.children) {
        element.appendChild(buildWidget(child));
    }

    return element;
}

function updateColumn(state) { }

function buildRectangle(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-rectangle");
    return element;
}

function updateRectangle(state) { }

function buildStack(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-stack");

    for (const child of widget.children) {
        element.appendChild(buildWidget(child));
    }

    return element;
}

function updateStack(state) { }

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

function updateAlign(state) { }

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
    result.id = "id-" + widget.id;

    return result;
}

function updateWidget(widget, state) {
    const callbacks = widgetHandlers[widget.type];

    if (callbacks === undefined) {
        throw "Cannot update unknown widget type: " + widget.type;
    }

    const [build, update] = callbacks;
    return update(state);
}

function main() {
    var body = document.getElementsByTagName("body")[0];
    body.appendChild(buildWidget(rootWidget));
}

main();
