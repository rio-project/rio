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












