import { ComponentBase, ComponentState } from './componentBase';

export type MediaPlayerState = ComponentState & {
    _type_: 'mediaPlayer';
    loop?: boolean;
    autoplay?: boolean;
    controls?: boolean;
    muted?: boolean;
    volume?: number;
    mediaUrl?: string;
    reportError?: boolean;
    reportPlaybackEnd?: boolean;
};

export class MediaPlayerComponent extends ComponentBase {
    state: Required<MediaPlayerState>;

    private mediaElement: HTMLVideoElement;

    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add(
            'rio-media-player',
            'rio-zero-size-request-container'
        );

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
        if (deltaState.mediaUrl !== undefined) {
            this.mediaElement.src = deltaState.mediaUrl;
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

        if (deltaState.reportError !== undefined) {
            if (deltaState.reportError) {
                if (this.mediaElement.onerror === null) {
                    this.mediaElement.onerror = this._onError.bind(this);
                }
            } else {
                this.mediaElement.onerror = null;
            }
        }

        if (deltaState.reportPlaybackEnd !== undefined) {
            if (deltaState.reportPlaybackEnd) {
                if (this.mediaElement.onended === null) {
                    this.mediaElement.onended = this._onPlaybackEnd.bind(this);
                }
            } else {
                this.mediaElement.onended = null;
            }
        }
    }

    private _onError(event: string | Event): void {
        this.sendMessageToBackend({
            type: 'onError',
        });
    }

    private _onPlaybackEnd(event: Event): void {
        this.sendMessageToBackend({
            type: 'onPlaybackEnd',
        });
    }
}
