import { fillToCss } from '../cssUtils';
import { applyIcon } from '../designApplication';
import { Fill } from '../models';
import { ComponentBase, ComponentState } from './componentBase';

export type MediaPlayerState = ComponentState & {
    _type_: 'mediaPlayer';
    loop?: boolean;
    autoplay?: boolean;
    controls?: boolean;
    muted?: boolean;
    volume?: number;
    mediaUrl?: string;
    background: Fill;
    reportError?: boolean;
    reportPlaybackEnd?: boolean;
};

const OVERLAY_TIMEOUT = 2000;

async function hasAudio(element: HTMLMediaElement): Promise<boolean> {
    // Browser support for these things is poor, so we'll try various methods
    // and if none of them work, we'll play it safe and say there is audio.

    // @ts-ignore
    let mozHasAudio: boolean | undefined = element.mozHasAudio;
    if (mozHasAudio !== undefined) {
        return mozHasAudio;
    }

    // @ts-ignore
    let audioTracks: object[] | undefined = element.audioTracks;
    if (audioTracks !== undefined) {
        return audioTracks.length > 0;
    }

    // @ts-ignore
    let byteCount: number | undefined = element.webkitAudioDecodedByteCount;
    if (byteCount !== undefined) {
        if (byteCount > 0) {
            return true;
        }

        // Just because nothing has been decoded yet doesn't mean there's no
        // audio. Wait a little while and then check again.
        for (let i = 10; i > 0; i--) {
            await new Promise((r) => setTimeout(r, 50));
            // @ts-ignore
            if (element.webkitAudioDecodedByteCount > 0) {
                return true;
            }
        }
        return false;
    }

    return true;
}

export class MediaPlayerComponent extends ComponentBase {
    state: Required<MediaPlayerState>;

    private mediaPlayer: HTMLVideoElement;
    private altDisplay: HTMLElement;
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
    private volumeKnob: HTMLElement;

    private _lastInteractionAt: number = 0;
    private _overlayVisible: boolean = true;
    private _isFullScreen: boolean = false;
    private _hasAudio: boolean = false;

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

    /// Mute/Unmute the video
    setMute(mute: boolean): void {
        if (mute) {
            this.mediaPlayer.muted = true;
        } else {
            // If the media doesn't have audio, we can't unmute
            if (!this._hasAudio) {
                return;
            }

            this.mediaPlayer.muted = false;

            if (this.mediaPlayer.volume == 0) {
                this.setVolume(0.5);
            }
        }
    }

    /// Hooman eers are stoopid
    humanVolumeToLinear(volume: number): number {
        return (Math.pow(3, volume) - 1) / 2;
    }

    linearVolumeToHuman(volume: number): number {
        return Math.log(volume * 2 + 1) / Math.log(3);
    }

    /// Set the volume of the video
    setVolume(volume: number): void {
        this.mediaPlayer.volume = this.humanVolumeToLinear(volume);

        // Unmute, if previously muted
        if (volume > 0 && this.mediaPlayer.muted && this._hasAudio) {
            this.mediaPlayer.muted = false;
        }
    }

    /// Enter/Exit fullscreen mode
    toggleFullscreen(): void {
        if (this._isFullScreen) {
            document.exitFullscreen();
        } else {
            this.element().requestFullscreen();
        }
    }

    private _onFullscreenChange(): void {
        this._isFullScreen = document.fullscreenElement === this.element();

        if (this._isFullScreen) {
            applyIcon(this.fullscreenButton, 'fullscreen-exit', 'white');
        } else {
            applyIcon(this.fullscreenButton, 'fullscreen', 'white');
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
        // The duration may not be known yet if the browser hasn't loaded
        // the metadata. And if we don't know the duration, we can't really
        // display much.
        let duration = this.mediaPlayer.duration;
        if (isNaN(duration)) {
            this.timelinePlayed.style.width = '0';
            this.timelineLoaded.style.width = '0';
            this.playtimeLabel.textContent = '0:00';
            return;
        }

        let currentTime = this.mediaPlayer.currentTime;

        // Progress Slider
        let progress = currentTime / duration;
        let percentage = `${progress * 100}%`;

        this.timelinePlayed.style.width = percentage;

        // Progress Label
        let playedString = this._durationToString(currentTime);
        let durationString = this._durationToString(duration);
        this.playtimeLabel.textContent = `${playedString} / ${durationString}`;

        // Loaded Amount
        let loadedFraction =
            this.mediaPlayer.buffered.length > 0
                ? this.mediaPlayer.buffered.end(0) / duration
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
                <div class="rio-media-player-alt-display" style="display: none"></div>
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
        this.altDisplay = element.querySelector(
            '.rio-media-player-alt-display'
        ) as HTMLElement;

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
        this.volumeKnob = element.querySelector(
            '.rio-media-player-volume-knob'
        ) as HTMLElement;

        // Subscribe to events
        this.mediaPlayer.addEventListener(
            'timeupdate',
            this._updateProgress.bind(this)
        );

        element.addEventListener('mousemove', this.interact.bind(this), true);

        element.addEventListener('click', (event: Event) => {
            event.stopPropagation();

            if (!this.state.controls) {
                return;
            }
            if (this.mediaPlayer.paused) {
                this.mediaPlayer.play();
            } else {
                this.mediaPlayer.pause();
            }
        });

        this.playButton.addEventListener('click', (event: Event) => {
            event.stopPropagation();

            if (this.mediaPlayer.paused) {
                this.mediaPlayer.play();
            } else {
                this.mediaPlayer.pause();
            }
        });

        this.muteButton.addEventListener('click', (event: Event) => {
            event.stopPropagation();
            this.setMute(!this.mediaPlayer.muted);
        });

        this.fullscreenButton.addEventListener('click', (event: Event) => {
            event.stopPropagation();
            this.toggleFullscreen();
        });
        document.addEventListener(
            'fullscreenchange',
            this._onFullscreenChange.bind(this)
        );

        this.timelineOuter.addEventListener('click', (event: MouseEvent) => {
            event.stopPropagation();
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
            event.stopPropagation();

            // If the media doesn't have audio, the controls are disabled
            if (!this._hasAudio) {
                return;
            }

            let rect = this.volumeOuter.getBoundingClientRect();
            let volume = (event.clientX - rect.left) / rect.width;
            volume = Math.min(1, Math.max(0, volume));
            this.setVolume(volume);
        });

        this.muteButton.addEventListener(
            'wheel',
            this._onVolumeWheelEvent.bind(this)
        );
        this.volumeOuter.addEventListener(
            'wheel',
            this._onVolumeWheelEvent.bind(this)
        );

        element.addEventListener('dblclick', (event: MouseEvent) => {
            event.stopPropagation();

            if (!this.state.controls) {
                return;
            }

            this.toggleFullscreen();
        });

        element.addEventListener('keydown', this._onKeyPress.bind(this));

        this.mediaPlayer.addEventListener('play', () => {
            applyIcon(this.playButton, 'pause:fill', 'white');
        });

        this.mediaPlayer.addEventListener('pause', () => {
            applyIcon(this.playButton, 'play-arrow:fill', 'white');
        });

        this.mediaPlayer.addEventListener('ended', () => {
            applyIcon(this.playButton, 'play-arrow:fill', 'white');
        });

        this.mediaPlayer.addEventListener(
            'volumechange',
            this._onVolumeChange.bind(this)
        );

        this.mediaPlayer.addEventListener('loadedmetadata', async () => {
            // Update the progress display
            this._updateProgress();

            // Is this a video or audio?
            let isVideo = this.mediaPlayer.videoWidth > 0;

            // For videos, show the player and hide the alt display
            if (isVideo) {
                this.mediaPlayer.style.removeProperty('display');
                this.altDisplay.style.display = 'none';

                // Check if the file has audio and enable/disable the controls
                // accordingly
                this._hasAudio = await hasAudio(this.mediaPlayer);
            }
            // For audio, hide the player and show the alt display
            else {
                this.mediaPlayer.style.display = 'none';
                this.altDisplay.style.removeProperty('display');

                this._hasAudio = true;
            }

            // If there is audio, re-apply the mute setting. It might be out
            // of sync because unmuting isn't allowed while `_hasAudio` is
            // `false`.
            if (this._hasAudio) {
                this.mediaPlayer.muted = this.state.muted;
            }
            this._updateVolumeSliderAndIcon();
        });

        // Initialize
        applyIcon(this.altDisplay, 'music-note:fill', 'white');
        applyIcon(this.playButton, 'play-arrow:fill', 'white');
        applyIcon(this.fullscreenButton, 'fullscreen', 'white');
        applyIcon(this.muteButton, 'volume-up:fill', 'white');
        return element;
    }

    _updateElement(
        element: HTMLMediaElement,
        deltaState: MediaPlayerState
    ): void {
        if (deltaState.mediaUrl !== undefined) {
            let mediaUrl = new URL(deltaState.mediaUrl, document.location.href)
                .href;

            if (mediaUrl !== this.mediaPlayer.src) {
                this.mediaPlayer.src = mediaUrl;

                // Reset the time/progress bar (otherwise if the file can't be
                // played, the player would simply remains in whatever state it
                // was before)
                this._updateProgress();

                // Start the timeout that hides the controls
                this.interact();
            }
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

        if (deltaState.volume !== undefined) {
            this.setVolume(Math.min(1, Math.max(0, deltaState.volume)));
        }

        if (deltaState.muted !== undefined) {
            this.setMute(deltaState.muted);
        }

        // Force the volume display to update, since it usually only updates on
        // changes, i.e. when the <video> element's state differs from the
        // component's state.
        this._updateVolumeSliderAndIcon();

        if (deltaState.background !== undefined) {
            Object.assign(element.style, fillToCss(deltaState.background));
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

    private _onVolumeChange(): void {
        // Don't do anything if the volume is the same as before
        let newHumanVolume = this.linearVolumeToHuman(this.mediaPlayer.volume);

        let volumeHasChanged =
            Math.abs(newHumanVolume - this.state.volume) > 0.01;
        let mutedHasChanged = this.mediaPlayer.muted !== this.state.muted;

        if (!volumeHasChanged && !mutedHasChanged) {
            return;
        }

        this._updateVolumeSliderAndIcon();

        // Update the state and notify the backend
        this.setStateAndNotifyBackend({
            volume: newHumanVolume,
            muted: this.mediaPlayer.muted,
        });
    }

    private _updateVolumeSliderAndIcon(): void {
        let humanVolume = this.linearVolumeToHuman(this.mediaPlayer.volume);

        // Update the mute button's icon
        if (this.mediaPlayer.muted || this.mediaPlayer.volume == 0) {
            // When muted, the volume slider displays 0
            this.volumeCurrent.style.width = '0';

            let color = this._hasAudio ? 'white' : 'gray';
            applyIcon(this.muteButton, 'volume-off:fill', color);
            this.volumeKnob.style.background = color;
        } else {
            this.volumeCurrent.style.width = `${humanVolume * 100}%`;

            if (humanVolume < 0.5) {
                applyIcon(this.muteButton, 'volume-down:fill', 'white');
            } else {
                applyIcon(this.muteButton, 'volume-up:fill', 'white');
            }
        }
    }

    private _onVolumeWheelEvent(event: WheelEvent): void {
        // If the media doesn't have audio, the controls are disabled
        if (!this._hasAudio) {
            return;
        }

        if (event.deltaY < 0) {
            this._volumeUp();
        } else if (event.deltaY !== 0) {
            this._volumeDown();
        } else {
            return;
        }

        event.stopPropagation();
        event.preventDefault();
    }

    private _volumeUp(): void {
        let humanVolume = this.linearVolumeToHuman(this.mediaPlayer.volume);
        this.setVolume(Math.min(humanVolume + 0.1, 1));
    }

    private _volumeDown(): void {
        let humanVolume = this.linearVolumeToHuman(this.mediaPlayer.volume);
        this.setVolume(Math.max(humanVolume - 0.1, 0));
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

    private _onKeyPress(event: KeyboardEvent): void {
        console.log('PRESS', event.key);

        if (!this.state.controls) {
            return;
        }

        switch (event.key) {
            // Space plays/pauses the video
            case ' ':
                if (this.mediaPlayer.paused) {
                    this.mediaPlayer.play();
                } else {
                    this.mediaPlayer.pause();
                }
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
                this._volumeUp();
                break;
            case 'ArrowDown':
                this._volumeDown();
                break;

            // Number keys seek to a percentage of the video
            case '0':
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
            case '6':
            case '7':
            case '8':
            case '9':
                let percentage = parseInt(event.key) / 10;
                this.mediaPlayer.currentTime =
                    this.mediaPlayer.duration * percentage;

                this.interact();
                break;

            // Escape exists fullscreen mode (browsers usually have this built
            // in, but just in case)
            case 'Escape':
                if (this._isFullScreen) {
                    this.toggleFullscreen();
                }
                break;

            // All other keys are ignored
            default:
                return;
        }

        event.stopPropagation();
        event.preventDefault();
    }

    grabKeyboardFocus(): void {
        this.element().focus();
    }
}
