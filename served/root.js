rootWidget = "{root_widget}";

initialStates = "{initial_states}";



function buildColumn(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-column");

    for (const child of widget.children) {
        element.appendChild(buildWidget(child));
    }

    return element;
}

function updateColumn(state) { }

function buildRow(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-row");

    for (const child of widget.children) {
        element.appendChild(buildWidget(child));
    }

    return element;
}

function updateRow(state) { }

function buildText(widget) {
    var element = document.createElement("div");
    element.classList.add("pygui-text");
    element.innerText = "TEXT!";
    return element;
}

function updateText(state) {
}

widgetHandlers = {
    "column": [buildColumn, updateColumn],
    "row": [buildRow, updateRow],
    "text": [buildText, updateText],
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