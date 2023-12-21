import { ComponentBase, ComponentState } from './componentBase';

const FILL_MODE_TO_OBJECT_FIT = {
    fit: 'contain',
    stretch: 'fill',
    zoom: 'cover',
} as const;

export type ImageState = ComponentState & {
    _type_: 'Image-builtin';
    fill_mode?: keyof typeof FILL_MODE_TO_OBJECT_FIT;
    imageUrl?: string;
    reportError?: boolean;
    corner_radius?: [number, number, number, number];
};

export class ImageComponent extends ComponentBase {
    state: Required<ImageState>;

    private imageElement: HTMLImageElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-image');
        element.classList.add('rio-zero-size-request-container');

        this.imageElement = document.createElement('img');
        element.appendChild(this.imageElement);

        this.imageElement.onload = () => {
            this.imageElement.classList.remove('rio-content-loading');
        };
        this.imageElement.onerror = this._onError.bind(this);

        return element;
    }

    updateElement(element: HTMLElement, deltaState: ImageState): void {
        let imgElement = element.firstElementChild as HTMLImageElement;

        if (
            deltaState.imageUrl !== undefined &&
            imgElement.src !== deltaState.imageUrl
        ) {
            imgElement.classList.add('rio-content-loading');
            imgElement.src = deltaState.imageUrl;
        }

        if (deltaState.fill_mode !== undefined) {
            imgElement.style.objectFit =
                FILL_MODE_TO_OBJECT_FIT[deltaState.fill_mode];
        }

        if (deltaState.corner_radius !== undefined) {
            let [topLeft, topRight, bottomRight, bottomLeft] =
                deltaState.corner_radius;

            imgElement.style.borderRadius = `${topLeft}rem ${topRight}rem ${bottomRight}rem ${bottomLeft}rem`;
        }
    }

    private _onError(event: string | Event): void {
        this.imageElement.classList.remove('rio-content-loading');

        this.sendMessageToBackend({
            type: 'onError',
        });
    }
}
