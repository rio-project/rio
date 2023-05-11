
export type Color = [number, number, number, number];



export type Fill =
    | {
        type: 'solid';
        color: Color;
    }
    | {
        type: 'linearGradient';
        angleDegrees: number;
        stops: [Color, number][];
    };


export type JsonText = {
    type: 'text',
    id: string,
    text: string,
    multiline: boolean,
    font: string,
    font_color: Color,
    font_size: number,
    font_weight: string,
    italic: boolean,
    underlined: boolean,
}


export type JsonRow = {
    type: 'row',
    id: string,
    children: JsonWidget[],
}

export type JsonColumn = {
    type: 'column',
    id: string,
    children: JsonWidget[],
}

export type JsonRectangle = {
    type: 'rectangle',
    id: string,
    fill: Fill,
    cornerRadius: [number, number, number, number],
}

export type JsonStack = {
    type: 'stack',
    id: string,
    children: JsonWidget[],
}


export type JsonMargin = {
    type: 'margin',
    id: string,
    child: JsonWidget,
    margin: [number, number, number, number],
}

export type JsonAlign = {
    type: 'align',
    id: string,
    child: JsonWidget,
    align_x?: number,
    align_y?: number,
}

export type JsonButton = {
    type: 'button',
    id: string,
    text: string,
}

export type JsonWidget = JsonText | JsonRow | JsonColumn | JsonRectangle | JsonStack | JsonMargin | JsonAlign;
