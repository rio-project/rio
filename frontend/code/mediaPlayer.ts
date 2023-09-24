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

    private mediaElement: HTMLVideoElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-media-player', 'rio-aspect-ratio-container');

        this.mediaElement = document.createElement('video');
        this.mediaElement.textContent =
            'Your browser does not support video/audio playback.';
        element.appendChild(this.mediaElement);

        return element;
    }

    updateElement(
        element: HTMLMediaElement,
        deltaState: MediaPlayerState
    ): void {
        if (deltaState._media_asset !== undefined) {
            this.mediaElement.src = deltaState._media_asset;
        }

        if (deltaState.loop !== undefined) {
            this.mediaElement.loop = deltaState.loop;
        }

        if (deltaState.autoplay !== undefined) {
            this.mediaElement.autoplay = deltaState.autoplay;
        }

        if (deltaState.controls !== undefined) {
            this.mediaElement.controls = deltaState.controls;
        }

        if (deltaState.muted !== undefined) {
            this.mediaElement.muted = deltaState.muted;
        }

        if (deltaState.volume !== undefined) {
            this.mediaElement.volume = deltaState.volume;
        }
    }
}
