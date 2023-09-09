import { WidgetBase, WidgetState } from './widgetBase';

export type MediaPlayerState = WidgetState & {
    _type_: 'mediaPlayer';
    _media_asset?: string;
    loop?: boolean;
    autoplay?: boolean;
    controls?: boolean;
    muted?: boolean;
    volume?: number;
};

export class MediaPlayerWidget extends WidgetBase {
    state: Required<MediaPlayerState>;
    
    createElement(): HTMLElement {
        let element = document.createElement('video');
        return element;
    }

    updateElement(element: HTMLMediaElement, deltaState: MediaPlayerState): void {
        if (deltaState._media_asset !== undefined) {
            element.src = deltaState._media_asset;
        }

        if (deltaState.loop !== undefined) {
            element.loop = deltaState.loop;
        }

        if (deltaState.autoplay !== undefined) {
            element.autoplay = deltaState.autoplay;
        }

        if (deltaState.controls !== undefined) {
            element.controls = deltaState.controls;
        }

        if (deltaState.muted !== undefined) {
            element.muted = deltaState.muted;
        }

        if (deltaState.volume !== undefined) {
            element.volume = deltaState.volume;
        }
    }
}
