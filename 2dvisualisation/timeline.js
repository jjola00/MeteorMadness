// Timeline controller for temporal visualization

export class TimelineController {
    constructor() {
        this.currentTime = 0;
        this.duration = 86400 * 3; // 3 days default
        this.isPlaying = false;
        this.playbackSpeed = 1.0;
        this.animationId = null;
        this.lastUpdateTime = 0;
        this.callbacks = [];
    }

    initialize() {
        this.setupEventListeners();
        this.updateDisplay();
    }

    setupEventListeners() {
        const timelineSlider = document.getElementById('timelineSlider');
        const playPauseBtn = document.getElementById('playPauseBtn');
        const resetBtn = document.getElementById('resetBtn');
        const stepBtn = document.getElementById('stepBtn');
        const speedSlider = document.getElementById('speedSlider');
        const speedDisplay = document.getElementById('speedDisplay');

        if (!timelineSlider || !playPauseBtn) {
            console.error('Timeline elements not found');
            return;
        }

        timelineSlider.addEventListener('input', (e) => {
            const percentage = parseFloat(e.target.value);
            this.currentTime = (percentage / 100) * this.duration;
            this.updateDisplay();
            this.notifyCallbacks();
        });

        playPauseBtn.addEventListener('click', () => {
            this.togglePlayback();
        });

        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.reset();
            });
        }

        if (stepBtn) {
            stepBtn.addEventListener('click', () => {
                this.step();
            });
        }

        if (speedSlider && speedDisplay) {
            speedSlider.addEventListener('input', (e) => {
                this.playbackSpeed = parseFloat(e.target.value);
                speedDisplay.textContent = this.playbackSpeed.toFixed(1) + 'x';
            });
        }
    }

    togglePlayback() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }

    play() {
        this.isPlaying = true;
        const playPauseBtn = document.getElementById('playPauseBtn');
        if (playPauseBtn) {
            playPauseBtn.textContent = 'Pause';
        }
        this.lastUpdateTime = performance.now();
        this.animate();
    }

    pause() {
        this.isPlaying = false;
        const playPauseBtn = document.getElementById('playPauseBtn');
        if (playPauseBtn) {
            playPauseBtn.textContent = 'Play';
        }
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
    }

    reset() {
        this.pause();
        this.currentTime = 0;
        this.updateDisplay();
        this.notifyCallbacks();
    }

    step() {
        this.pause();
        this.currentTime = Math.min(this.currentTime + 3600, this.duration);
        this.updateDisplay();
        this.notifyCallbacks();
    }

    animate() {
        if (!this.isPlaying) return;

        const currentTime = performance.now();
        const deltaTime = (currentTime - this.lastUpdateTime) / 1000;
        this.lastUpdateTime = currentTime;

        this.currentTime += deltaTime * this.playbackSpeed * 3600;

        if (this.currentTime >= this.duration) {
            this.currentTime = this.duration;
            this.pause();
        }

        this.updateDisplay();
        this.notifyCallbacks();

        if (this.isPlaying) {
            this.animationId = requestAnimationFrame(() => this.animate());
        }
    }

    updateDisplay() {
        const percentage = (this.currentTime / this.duration) * 100;

        const timelineSlider = document.getElementById('timelineSlider');
        const timelineProgress = document.getElementById('timelineProgress');
        const currentTimeElement = document.getElementById('currentTime');

        if (timelineSlider) {
            timelineSlider.value = percentage;
        }
        if (timelineProgress) {
            timelineProgress.style.width = percentage + '%';
        }
        if (currentTimeElement) {
            currentTimeElement.textContent = this.formatTime(this.currentTime);
        }
    }

    updateMarkers(scenario) {
        const markersContainer = document.getElementById('timelineMarkers');
        if (!markersContainer) return;
        
        markersContainer.innerHTML = '';

        if (scenario.markers) {
            scenario.markers.forEach(marker => {
                const markerElement = document.createElement('div');
                markerElement.className = 'timeline-marker';
                markerElement.setAttribute('data-label', marker.label);

                const percentage = (marker.time / scenario.duration) * 100;
                markerElement.style.left = percentage + '%';

                markersContainer.appendChild(markerElement);
            });
        }
    }

    setDuration(duration) {
        this.duration = duration;
        this.currentTime = 0;
        this.pause();
        this.updateDisplay();
    }

    formatTime(seconds) {
        const isNegative = seconds < 0;
        const absSeconds = Math.abs(seconds);

        const days = Math.floor(absSeconds / 86400);
        const hours = Math.floor((absSeconds % 86400) / 3600);
        const minutes = Math.floor((absSeconds % 3600) / 60);
        const secs = Math.floor(absSeconds % 60);

        let timeStr = '';
        if (days > 0) {
            timeStr = `${days}d ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            timeStr = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }

        return (isNegative ? 'T-' : 'T+') + timeStr;
    }

    onTimeChange(callback) {
        this.callbacks.push(callback);
    }

    notifyCallbacks() {
        this.callbacks.forEach(callback => {
            try {
                callback(this.currentTime);
            } catch (error) {
                console.error('Error in timeline callback:', error);
            }
        });
    }
}