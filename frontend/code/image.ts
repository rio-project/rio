import { WidgetBase, WidgetState } from './widgetBase';


const FILL_MODE_TO_OBJECT_FIT = {
    'fit': 'contain',
    'stretch': 'fill',
    'zoom': 'cover',
} as const;


export type ImageState = WidgetState & {
    image_url?: string;
    fill_mode?: keyof typeof FILL_MODE_TO_OBJECT_FIT;
    report_error?: boolean;
};


export class ImageWidget extends WidgetBase {
    state: Required<ImageState>;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-aspect-ratio-container');

        element.onload = () => {
            element.classList.remove('rio-content-loading');
        };

        let img = document.createElement('img');
        element.appendChild(img);

        return element;
    }

    updateElement(element: HTMLElement, deltaState: ImageState): void {
        let imgElement = element.firstElementChild as HTMLImageElement;

        if (deltaState.image_url !== undefined && imgElement.src !== deltaState.image_url) {
            imgElement.classList.add('rio-content-loading');
            imgElement.src = deltaState.image_url;
        }

        if (deltaState.fill_mode !== undefined) {
            imgElement.style.objectFit = FILL_MODE_TO_OBJECT_FIT[deltaState.fill_mode];
        }

        if (deltaState.report_error !== undefined) {
            if (deltaState.report_error) {
                if (imgElement.onerror === null) {
                    imgElement.onerror = this._onError.bind(this);
                }
            } else {
                imgElement.onerror = null;
            }
        }
    }

    private _onError(event: string | Event): void {
        this.sendMessageToBackend({
            type: 'onError',
        });
    }
}
