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

export type TextStyle = {
    fontName: string;
    fontColor: [number, number, number, number];
    fontSize: number;
    italic: boolean;
    fontWeight: 'normal' | 'bold';
    underlined: boolean;
    allCaps: boolean;
};

export type BoxStyle = {
    fill: Fill;
    strokeColor: [number, number, number, number];
    strokeWidth: number;
    cornerRadius: [number, number, number, number];
    shadowColor: [number, number, number, number];
    shadowRadius: number;
    shadowOffset: [number, number];
};
