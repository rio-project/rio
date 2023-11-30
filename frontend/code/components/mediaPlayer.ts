import { applyIcon } from '../designApplication';
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

const overlayTimeout = 2000;

export class MediaPlayerComponent extends ComponentBase {
    state: Required<MediaPlayerState>;

    private video: HTMLVideoElement;
    private controls: HTMLElement;

    private playButton: HTMLElement;
    private muteButton: HTMLElement;
    private fullscreenButton: HTMLElement;

    private playtimeLabel: HTMLElement;

    private timelineOuter: HTMLElement;
    private timelineLoaded: HTMLElement;
    private timelineHover: HTMLElement;
    private timelinePlayed: HTMLElement;

    private volumeOuter: HTMLElement;
    private volumeCurrent: HTMLElement;

    private _lastInteractionAt: number = 0;
    private _overlayVisible: boolean = true;

    /// Update the overlay's opacity to be what it currently should be.
    _updateOverlay(): void {
        let visibilityBefore = this._overlayVisible;

        // If the video is paused, show the controls
        if (this.video.paused) {
            this._overlayVisible = true;
        }
        // If the video was recently interacted with, show the controls
        else if (Date.now() - this._lastInteractionAt < overlayTimeout) {
            this._overlayVisible = true;
        }
        // Otherwise, hide the controls
        else {
            this._overlayVisible = false;
        }

        // If nothing has changed don't transition. This avoids a CSS
        // transition re-trigger
        if (visibilityBefore == this._overlayVisible) {
            return;
        }

        // Apply the visibility
        this.controls.style.opacity = this._overlayVisible ? '1' : '0';
    }

    /// Register an interaction with the video player, so it knows to show/hide
    /// the controls.
    interact(): void {
        // Update the last interaction time
        this._lastInteractionAt = Date.now();

        // Update the overlay right now
        this._updateOverlay();

        // And again after the overlay timeout + some fudge factor
        setTimeout(this._updateOverlay, overlayTimeout + 50);
    }

    /// Play/Pause the video
    setPlay(play: boolean): void {
        if (play) {
            this.video.play();
            applyIcon(this.playButton, 'pause:fill', 'white');
        } else {
            this.video.pause();
            applyIcon(this.playButton, 'play-arrow:fill', 'white');
        }

        this.interact();
    }

    /// Update the content of the mute button to match the current state of the
    /// video.
    _updateMuteContent(): void {
        if (this.video.muted || this.video.volume == 0) {
            applyIcon(this.muteButton, 'volume-off:fill', 'white');
        } else if (this.video.volume < 0.5) {
            applyIcon(this.muteButton, 'volume-down:fill', 'white');
        } else {
            applyIcon(this.muteButton, 'volume-up:fill', 'white');
        }
    }

    /// Mute/Unmute the video
    setMute(mute: boolean): void {
        if (mute) {
            this.video.muted = true;
        } else {
            this.video.muted = false;

            if (this.video.volume == 0) {
                this.video.volume = 0.5;
            }
        }

        this._updateMuteContent();
    }

    /// Set the volume of the video
    setVolume(volume: number): void {
        // Hooman audio perception is stoopid
        this.video.volume = (Math.pow(3, volume) - 1) / 2;

        // Unmute, if previously muted
        if (volume > 0 && this.video.muted) {
            this.video.muted = false;
        }

        // Update the slider
        this.volumeCurrent.style.width = `${volume * 100}%`;

        this._updateMuteContent();
    }

    /// Enter/Exit fullscreen mode
    toggleFullscreen(): void {
        if (document.fullscreenElement) {
            applyIcon(this.fullscreenButton, 'fullscreen', 'white');
            document.exitFullscreen();
        } else {
            applyIcon(this.fullscreenButton, 'fullscreen-exit', 'white');
            this.element().requestFullscreen();
        }
    }

    /// Pretty-string a duration (in seconds. FU JS)
    _durationToString(duration: number): string {
        let hours = Math.floor(duration / 3600);
        let minutes = Math.floor(duration / 60) % 60;
        let seconds = Math.floor(duration % 60);

        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds
                .toString()
                .padStart(2, '0')}`;
        } else if (minutes > 0) {
            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
        } else {
            return `0:${seconds.toString().padStart(2, '0')}`;
        }
    }

    /// Update the UI to reflect the current playback and loading progress
    _updateProgress(): void {
        // Progress Slider
        let progress = this.video.currentTime / this.video.duration;
        let percentage = `${progress * 100}%`;

        this.timelinePlayed.style.width = percentage;

        // Progress Label
        //
        // The duration may not be known yet if the browser hasn't loaded
        // the metadata.
        if (isNaN(this.video.duration)) {
            this.playtimeLabel.textContent = '0:00';
        } else {
            let playedString = this._durationToString(this.video.currentTime);
            let durationString = this._durationToString(this.video.duration);
            this.playtimeLabel.textContent = `${playedString} / ${durationString}`;
        }

        // Loaded Amount
        let loadedFraction =
            this.video.buffered.length > 0
                ? this.video.buffered.end(0) / this.video.duration
                : 0;
        this.timelineLoaded.style.width = `${loadedFraction * 100}%`;
    }

    _createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-media-player');

        element.innerHTML = `
            <video></video>
            <div class="rio-media-player-controls">
                <!-- Timeline -->
                <div class="rio-media-player-timeline">
                    <div>
                        <div class="rio-media-player-timeline-background"></div>
                        <div class="rio-media-player-timeline-loaded"></div>
                        <div class="rio-media-player-timeline-hover"></div>
                        <div class="rio-media-player-timeline-played">
                            <div class="rio-media-player-timeline-knob"></div>
                        </div>
                    </div>
                </div>
                <!-- Controls -->
                <div class="rio-media-player-controls-row">
                    <div class="rio-media-player-button rio-media-player-button-play"></div>
                    <div class="rio-media-player-button rio-media-player-button-mute"></div>
                    <!-- Volume -->
                    <div class="rio-media-player-volume">
                        <div>
                            <div class="rio-media-player-volume-background"></div>
                            <div class="rio-media-player-volume-current">
                                <div class="rio-media-player-volume-knob"></div>
                            </div>
                        </div>
                    </div>

                    <div class="rio-media-player-playtime-label"></div>

                    <!-- Spacer -->
                    <div style="flex-grow: 1;"></div>

                    <div class="rio-media-player-button rio-media-player-button-fullscreen"></div>
                </div>
            </div>
        `;

        this.video = element.querySelector('video') as HTMLVideoElement;
        this.controls = element.querySelector(
            '.rio-media-player-controls'
        ) as HTMLElement;

        this.playButton = element.querySelector(
            '.rio-media-player-button-play'
        ) as HTMLElement;
        this.muteButton = element.querySelector(
            '.rio-media-player-button-mute'
        ) as HTMLElement;
        this.fullscreenButton = element.querySelector(
            '.rio-media-player-button-fullscreen'
        ) as HTMLElement;

        this.playtimeLabel = element.querySelector(
            '.rio-media-player-playtime-label'
        ) as HTMLElement;

        this.timelineOuter = element.querySelector(
            '.rio-media-player-timeline'
        ) as HTMLElement;
        this.timelineLoaded = element.querySelector(
            '.rio-media-player-timeline-loaded'
        ) as HTMLElement;
        this.timelineHover = element.querySelector(
            '.rio-media-player-timeline-hover'
        ) as HTMLElement;
        this.timelinePlayed = element.querySelector(
            '.rio-media-player-timeline-played'
        ) as HTMLElement;

        this.volumeOuter = element.querySelector(
            '.rio-media-player-volume'
        ) as HTMLElement;
        this.volumeCurrent = element.querySelector(
            '.rio-media-player-volume-current'
        ) as HTMLElement;

        this.video.addEventListener(
            'timeupdate',
            this._updateProgress.bind(this)
        );

        // Subscribe to events
        this.video.addEventListener('mousemove', this.interact.bind(this));

        this.video.addEventListener('click', () => {
            this.setPlay(this.video.paused);
        });

        this.playButton.addEventListener('click', () => {
            this.setPlay(this.video.paused);
        });

        this.muteButton.addEventListener('click', () => {
            this.setMute(!this.video.muted);
        });

        this.fullscreenButton.addEventListener('click', () => {
            this.toggleFullscreen();
        });

        this.timelineOuter.addEventListener('click', (event: MouseEvent) => {
            let rect = this.timelineOuter.getBoundingClientRect();
            let progress = (event.clientX - rect.left) / rect.width;
            this.video.currentTime = this.video.duration * progress;
        });

        this.timelineOuter.addEventListener(
            'mousemove',
            (event: MouseEvent) => {
                let rect = this.timelineOuter.getBoundingClientRect();
                let progress = (event.clientX - rect.left) / rect.width;
                this.timelineHover.style.width = `${progress * 100}%`;
                this.timelineHover.style.opacity = '0.5';
            }
        );

        this.timelineOuter.addEventListener('mouseleave', () => {
            this.timelineHover.style.opacity = '0';
        });

        this.volumeOuter.addEventListener('click', (event: MouseEvent) => {
            let rect = this.volumeOuter.getBoundingClientRect();
            let volume = (event.clientX - rect.left) / rect.width;
            volume = Math.min(1, Math.max(0, volume));
            this.setVolume(volume);
        });

        this.video.addEventListener(
            'timeupdate',
            this._updateProgress.bind(this)
        );

        this.video.addEventListener('dblclick', () => {
            this.toggleFullscreen();
        });

        this.video.addEventListener('keydown', (event: KeyboardEvent) => {
            switch (event.key) {
                // Space plays/pauses the video
                case ' ':
                    this.setPlay(this.video.paused);
                    break;

                // M mutes/unmutes the video
                case 'm':
                    this.setMute(!this.video.muted);
                    break;

                // F toggles fullscreen
                case 'f':
                    this.toggleFullscreen();
                    break;

                // Left and right arrow keys seek the video
                case 'ArrowLeft':
                    this.video.currentTime -= 5;
                    break;
                case 'ArrowRight':
                    this.video.currentTime += 5;
                    break;

                // Up and down arrow keys change the volume
                case 'ArrowUp':
                    this.setVolume(this.video.volume + 0.1);
                    break;
                case 'ArrowDown':
                    this.setVolume(this.video.volume - 0.1);
                    break;

                // All other keys are ignored
                default:
                    return;
            }

            event.preventDefault();
        });

        this.video.addEventListener('ended', () => {
            this.setPlay(false);
        });

        // Initialize
        applyIcon(this.playButton, 'play-arrow:fill', 'white');
        applyIcon(this.fullscreenButton, 'fullscreen', 'white');
        this._updateMuteContent();
        this._updateProgress();

        return element;
    }

    _updateElement(
        element: HTMLMediaElement,
        deltaState: MediaPlayerState
    ): void {
        if (
            deltaState.mediaUrl !== undefined &&
            deltaState.mediaUrl !== this.video.src
        ) {
            this.video.src = deltaState.mediaUrl;
        }

        if (deltaState.loop !== undefined) {
            this.video.loop = deltaState.loop;
        }

        if (deltaState.autoplay !== undefined) {
            this.video.autoplay = deltaState.autoplay;
        }

        if (deltaState.controls !== undefined) {
            // TODO!
            console.log('TODO: Support enabling/disabling controls');
        }

        if (deltaState.muted !== undefined) {
            this.setMute(deltaState.muted);
        }

        if (deltaState.volume !== undefined) {
            this.setVolume(deltaState.volume);
        }

        if (deltaState.reportError !== undefined) {
            if (deltaState.reportError) {
                if (this.video.onerror === null) {
                    this.video.onerror = this._onError.bind(this);
                }
            } else {
                this.video.onerror = null;
            }
        }

        if (deltaState.reportPlaybackEnd !== undefined) {
            if (deltaState.reportPlaybackEnd) {
                if (this.video.onended === null) {
                    this.video.onended = this._onPlaybackEnd.bind(this);
                }
            } else {
                this.video.onended = null;
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

    grabKeyboardFocus(): void {
        this.element().focus();
    }
}
