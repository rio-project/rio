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
      }
    | {
          type: 'image';
          imageUrl: string;
          fillMode: 'fit' | 'stretch' | 'tile' | 'zoom';
      };

export type JsonWidget = {
    _type_: string;
    _python_type_: string;
    _key_?: string;
    _margin_?: [number, number, number, number];
    _size_?: [number | null, number | null];
    _align_?: [number | null, number | null];
};

export type JsonText = JsonWidget & {
    text?: string;
    multiline?: boolean;
    font?: string;
    font_color?: Color;
    font_size?: number;
    font_weight?: string;
    italic?: boolean;
    underlined?: boolean;
};

export type JsonRow = JsonWidget & {
    _type_: 'row';
    children?: number[];
    spacing?: number;
};

export type JsonColumn = JsonWidget & {
    _type_: 'column';
    children?: number[];
    spacing?: number;
};

export type JsonRectangle = JsonWidget & {
    _type_: 'rectangle';
    fill?: Fill;
    child?: number;
    corner_radius?: [number, number, number, number];
    stroke_width?: number;
    stroke_color?: Color;
};

export type JsonStack = JsonWidget & {
    _type_: 'stack';
    children?: number[];
};

export type JsonMargin = JsonWidget & {
    _type_: 'margin';
    child?: number;
    margin_left?: number;
    margin_right?: number;
    margin_top?: number;
    margin_bottom?: number;
};

export type JsonAlign = JsonWidget & {
    _type_: 'align';
    child?: number;
    align_x?: number;
    align_y?: number;
};

export type JsonMouseEventListener = JsonWidget & {
    _type_: 'mouseEventListener';
    child?: number;
    reportMouseDown?: boolean;
    reportMouseUp?: boolean;
    reportMouseMove?: boolean;
    reportMouseEnter?: boolean;
    reportMouseLeave?: boolean;
};

export type JsonTextInput = JsonWidget & {
    _type_: 'textInput';
    text?: string;
    placeholder?: string;
    secret?: boolean;
};

export type JsonOverride = JsonWidget & {
    _type_: 'override';
    child?: number;
    width?: number;
    height?: number;
};

export type JsonDropdown = JsonWidget & {
    _type_: 'dropdown';
    optionNames?: string[];
};

export type JsonSwitch = JsonWidget & {
    _type_: 'switch';
    is_on?: boolean;
};

export type JsonPlaceholder = JsonWidget & {
    _type_: 'placeholder';
    _child_?: number;
};
