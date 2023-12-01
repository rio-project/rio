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

const OVERLAY_TIMEOUT = 2000;

export class MediaPlayerComponent extends ComponentBase {
    state: Required<MediaPlayerState>;

    private mediaPlayer: HTMLVideoElement;
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
        if (this.mediaPlayer.paused) {
            this._overlayVisible = true;
        }
        // If the video was recently interacted with, show the controls
        else if (Date.now() - this._lastInteractionAt < OVERLAY_TIMEOUT) {
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
        if (this._overlayVisible) {
            this.controls.style.opacity = '1';
            this.mediaPlayer.style.cursor = 'default';
        } else {
            this.controls.style.opacity = '0';
            this.mediaPlayer.style.cursor = 'none';
        }
    }

    /// Register an interaction with the video player, so it knows to show/hide
    /// the controls.
    interact(): void {
        // Update the last interaction time
        this._lastInteractionAt = Date.now();

        // Update the overlay right now
        this._updateOverlay();

        // And again after the overlay timeout + some fudge factor
        setTimeout(this._updateOverlay.bind(this), OVERLAY_TIMEOUT + 50);
    }

    /// Play/Pause the video
    setPlay(play: boolean): void {
        if (play) {
            this.mediaPlayer.play();
            applyIcon(this.playButton, 'pause:fill', 'white');
        } else {
            this.mediaPlayer.pause();
            applyIcon(this.playButton, 'play-arrow:fill', 'white');
        }

        this.interact();
    }

    /// Update the content of the mute button to match the current state of the
    /// video.
    _updateMuteContent(): void {
        if (this.mediaPlayer.muted || this.mediaPlayer.volume == 0) {
            applyIcon(this.muteButton, 'volume-off:fill', 'white');
        } else if (this.mediaPlayer.volume < 0.5) {
            applyIcon(this.muteButton, 'volume-down:fill', 'white');
        } else {
            applyIcon(this.muteButton, 'volume-up:fill', 'white');
        }
    }

    /// Mute/Unmute the video
    setMute(mute: boolean): void {
        if (mute) {
            this.mediaPlayer.muted = true;
        } else {
            this.mediaPlayer.muted = false;

            if (this.mediaPlayer.volume == 0) {
                this.setVolume(0.5);
            }
        }

        this._updateMuteContent();
    }

    /// Set the volume of the video
    setVolume(volume: number): void {
        // Hooman eers are stoopid
        this.mediaPlayer.volume = (Math.pow(3, volume) - 1) / 2;

        // Unmute, if previously muted
        if (volume > 0 && this.mediaPlayer.muted) {
            this.mediaPlayer.muted = false;
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
        let progress = this.mediaPlayer.currentTime / this.mediaPlayer.duration;
        let percentage = `${progress * 100}%`;

        this.timelinePlayed.style.width = percentage;

        // Progress Label
        //
        // The duration may not be known yet if the browser hasn't loaded
        // the metadata.
        if (isNaN(this.mediaPlayer.duration)) {
            this.playtimeLabel.textContent = '0:00';
        } else {
            let playedString = this._durationToString(
                this.mediaPlayer.currentTime
            );
            let durationString = this._durationToString(
                this.mediaPlayer.duration
            );
            this.playtimeLabel.textContent = `${playedString} / ${durationString}`;
        }

        // Loaded Amount
        let loadedFraction =
            this.mediaPlayer.buffered.length > 0
                ? this.mediaPlayer.buffered.end(0) / this.mediaPlayer.duration
                : 0;
        this.timelineLoaded.style.width = `${loadedFraction * 100}%`;
    }

    _createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add(
            'rio-media-player',
            'rio-zero-size-request-container'
        );

        element.innerHTML = `
            <div>
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
            </div>
        `;

        this.mediaPlayer = element.querySelector('video') as HTMLVideoElement;
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

        // Subscribe to events
        this.mediaPlayer.addEventListener(
            'timeupdate',
            this._updateProgress.bind(this)
        );

        this.mediaPlayer.addEventListener(
            'mousemove',
            this.interact.bind(this)
        );
        this.timelineOuter.addEventListener(
            'mousemove',
            this.interact.bind(this)
        );
        this.volumeOuter.addEventListener(
            'mousemove',
            this.interact.bind(this)
        );
        this.playButton.addEventListener('mousemove', this.interact.bind(this));
        this.muteButton.addEventListener('mousemove', this.interact.bind(this));
        this.fullscreenButton.addEventListener(
            'mousemove',
            this.interact.bind(this)
        );

        this.mediaPlayer.addEventListener('click', () => {
            if (this.state.controls) {
                this.setPlay(this.mediaPlayer.paused);
            }
        });

        this.playButton.addEventListener('click', () => {
            this.setPlay(this.mediaPlayer.paused);
        });

        this.muteButton.addEventListener('click', () => {
            this.setMute(!this.mediaPlayer.muted);
        });

        this.fullscreenButton.addEventListener('click', () => {
            this.toggleFullscreen();
        });

        this.timelineOuter.addEventListener('click', (event: MouseEvent) => {
            let rect = this.timelineOuter.getBoundingClientRect();
            let progress = (event.clientX - rect.left) / rect.width;
            this.mediaPlayer.currentTime = this.mediaPlayer.duration * progress;
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

        this.mediaPlayer.addEventListener(
            'timeupdate',
            this._updateProgress.bind(this)
        );

        this.mediaPlayer.addEventListener('dblclick', () => {
            this.toggleFullscreen();
        });

        this.mediaPlayer.addEventListener('keydown', (event: KeyboardEvent) => {
            switch (event.key) {
                // Space plays/pauses the video
                case ' ':
                    this.setPlay(this.mediaPlayer.paused);
                    break;

                // M mutes/unmutes the video
                case 'm':
                    this.setMute(!this.mediaPlayer.muted);
                    break;

                // F toggles fullscreen
                case 'f':
                    this.toggleFullscreen();
                    break;

                // Left and right arrow keys seek the video
                case 'ArrowLeft':
                    this.mediaPlayer.currentTime -= 5;
                    break;
                case 'ArrowRight':
                    this.mediaPlayer.currentTime += 5;
                    break;

                // Up and down arrow keys change the volume
                case 'ArrowUp':
                    this.setVolume(Math.min(this.mediaPlayer.volume + 0.1, 1));
                    break;
                case 'ArrowDown':
                    this.setVolume(Math.max(this.mediaPlayer.volume - 0.1, 0));
                    break;

                // All other keys are ignored
                default:
                    return;
            }

            event.preventDefault();
        });

        this.mediaPlayer.addEventListener('ended', () => {
            this.setPlay(false);
        });

        this.mediaPlayer.addEventListener('loadedmetadata', () => {
            this._updateProgress();
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
            deltaState.mediaUrl !== this.mediaPlayer.src
        ) {
            this.mediaPlayer.src = deltaState.mediaUrl;
        }

        if (deltaState.loop !== undefined) {
            this.mediaPlayer.loop = deltaState.loop;
        }

        if (deltaState.autoplay !== undefined) {
            this.mediaPlayer.autoplay = deltaState.autoplay;
        }

        if (deltaState.controls === true) {
            this.controls.style.removeProperty('display');
        } else if (deltaState.controls === false) {
            this.controls.style.display = 'none';
        }

        if (deltaState.muted !== undefined) {
            this.setMute(deltaState.muted);
        }

        if (deltaState.volume !== undefined) {
            this.setVolume(Math.min(1, Math.max(0, deltaState.volume)));
        }

        if (deltaState.reportError !== undefined) {
            if (deltaState.reportError) {
                if (this.mediaPlayer.onerror === null) {
                    this.mediaPlayer.onerror = this._onError.bind(this);
                }
            } else {
                this.mediaPlayer.onerror = null;
            }
        }

        if (deltaState.reportPlaybackEnd !== undefined) {
            if (deltaState.reportPlaybackEnd) {
                if (this.mediaPlayer.onended === null) {
                    this.mediaPlayer.onended = this._onPlaybackEnd.bind(this);
                }
            } else {
                this.mediaPlayer.onended = null;
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
