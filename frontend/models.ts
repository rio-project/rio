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
    _type_: 'text';
    _python_type_: string;
    text?: string;
    multiline?: boolean;
    font?: string;
    font_color?: Color;
    font_size?: number;
    font_weight?: string;
    italic?: boolean;
    underlined?: boolean;
};

export type JsonRow = {
    _type_: 'row';
    _python_type_: string;
    children?: number[];
};

export type JsonColumn = {
    _type_: 'column';
    _python_type_: string;
    children?: number[];
};

export type JsonRectangle = {
    _type_: 'rectangle';
    _python_type_: string;
    fill?: Fill;
    child?: number;
    corner_radius?: [number, number, number, number];
};

export type JsonStack = {
    _type_: 'stack';
    _python_type_: string;
    children?: number[];
};

export type JsonMargin = {
    _type_: 'margin';
    _python_type_: string;
    child?: number;
    margin_left?: number;
    margin_right?: number;
    margin_top?: number;
    margin_bottom?: number;
};

export type JsonAlign = {
    _type_: 'align';
    _python_type_: string;
    child?: number;
    align_x?: number;
    align_y?: number;
};

export type JsonMouseEventListener = {
    _type_: 'mouseEventListener';
    _python_type_: string;
    child?: number;
    reportMouseDown?: boolean;
    reportMouseUp?: boolean;
    reportMouseMove?: boolean;
    reportMouseEnter?: boolean;
    reportMouseLeave?: boolean;
};

export type JsonTextInput = {
    _type_: 'textInput';
    _python_type_: string;
    text?: string;
    placeholder?: string;
    secret?: boolean;
};

export type JsonOverride = {
    _type_: 'override';
    _python_type_: string;
    child?: number;
    width?: number;
    height?: number;
};

export type JsonPlaceholder = {
    _type_: 'placeholder';
    _python_type_: string;
    _child_?: number;
};

export type JsonWidget =
    | JsonText
    | JsonRow
    | JsonColumn
    | JsonRectangle
    | JsonStack
    | JsonMargin
    | JsonAlign
    | JsonMouseEventListener
    | JsonTextInput
    | JsonOverride
    | JsonPlaceholder;
