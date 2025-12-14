/**
 * Hyperlocal B-Roll Generator
 * Frontend JavaScript Application
 */

class BRollGenerator {
    constructor() {
        this.form = document.getElementById('generate-form');
        this.locationInput = document.getElementById('location');
        this.creativeDirectionInput = document.getElementById('creative-direction');
        this.progressSection = document.getElementById('progress-section');
        this.resultsSection = document.getElementById('results-section');
        this.progressBar = document.getElementById('progress-bar');
        this.progressPercentage = document.getElementById('progress-percentage');
        this.progressMessage = document.getElementById('progress-message');
        this.clipsGrid = document.getElementById('clips-grid');
        this.generateMoreBtn = document.getElementById('generate-more');

        this.currentJobId = null;
        this.pollingInterval = null;

        this.init();
    }

    init() {
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));

        // Preset chips
        document.querySelectorAll('.preset-chip').forEach(chip => {
            chip.addEventListener('click', () => this.applyPreset(chip));
        });

        // Generate more button
        this.generateMoreBtn.addEventListener('click', () => this.resetToForm());
    }

    applyPreset(chip) {
        const presetValue = chip.dataset.preset;
        this.creativeDirectionInput.value = presetValue;

        // Visual feedback
        document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');

        // Focus on location if empty
        if (!this.locationInput.value) {
            this.locationInput.focus();
        }
    }

    async handleSubmit(e) {
        e.preventDefault();

        const location = this.locationInput.value.trim();
        const creativeDirection = this.creativeDirectionInput.value.trim();

        if (!location || !creativeDirection) {
            this.showNotification('Please fill in both fields', 'error');
            return;
        }

        // Start generation
        await this.startGeneration(location, creativeDirection);
    }

    async startGeneration(location, creativeDirection) {
        try {
            // Show progress section
            this.form.classList.add('hidden');
            this.progressSection.classList.remove('hidden');
            this.resultsSection.classList.add('hidden');

            // Reset progress UI
            this.updateProgress(0, 'Initializing...');
            this.resetSteps();

            // Make API request
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    location,
                    creative_direction: creativeDirection,
                    num_clips: 5
                })
            });

            if (!response.ok) {
                throw new Error('Failed to start generation');
            }

            const data = await response.json();
            this.currentJobId = data.job_id;

            // Start polling for status
            this.startPolling();

        } catch (error) {
            console.error('Generation error:', error);
            this.showNotification('Failed to start generation. Please try again.', 'error');
            this.resetToForm();
        }
    }

    startPolling() {
        // Poll every 2 seconds
        this.pollingInterval = setInterval(() => this.checkStatus(), 2000);
        // Also check immediately
        this.checkStatus();
    }

    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }

    async checkStatus() {
        if (!this.currentJobId) return;

        try {
            const response = await fetch(`/api/status/${this.currentJobId}`);

            if (!response.ok) {
                throw new Error('Failed to fetch status');
            }

            const data = await response.json();
            this.handleStatusUpdate(data);

        } catch (error) {
            console.error('Status check error:', error);
        }
    }

    handleStatusUpdate(data) {
        // Update progress bar
        this.updateProgress(data.progress, data.message);

        // Update steps based on progress
        this.updateSteps(data.progress);

        // Handle completion
        if (data.status === 'completed') {
            this.stopPolling();
            this.showResults(data.clips);
        } else if (data.status === 'failed') {
            this.stopPolling();
            this.showNotification(data.message, 'error');
            this.resetToForm();
        }
    }

    updateProgress(progress, message) {
        this.progressBar.style.width = `${progress}%`;
        this.progressPercentage.textContent = `${progress}%`;
        this.progressMessage.textContent = message;
    }

    resetSteps() {
        document.querySelectorAll('.step').forEach(step => {
            step.classList.remove('active', 'completed');
        });
    }

    updateSteps(progress) {
        const steps = document.querySelectorAll('.step');

        steps.forEach((step, index) => {
            const stepNum = index + 1;
            const stepThresholds = [10, 25, 45, 65];

            if (progress >= 100) {
                step.classList.remove('active');
                step.classList.add('completed');
            } else if (progress >= stepThresholds[index]) {
                if (index === steps.length - 1 || progress < stepThresholds[index + 1]) {
                    step.classList.add('active');
                    step.classList.remove('completed');
                } else {
                    step.classList.remove('active');
                    step.classList.add('completed');
                }
            }
        });
    }

    showResults(clips) {
        // Hide progress, show results
        this.progressSection.classList.add('hidden');
        this.resultsSection.classList.remove('hidden');
        this.resultsSection.classList.add('fade-in');

        // Render clips
        this.renderClips(clips);
    }

    renderClips(clips) {
        this.clipsGrid.innerHTML = '';

        clips.forEach((clip, index) => {
            const clipCard = document.createElement('div');
            clipCard.className = 'clip-card fade-in';
            clipCard.style.animationDelay = `${index * 100}ms`;

            clipCard.innerHTML = `
                <video src="${clip.url}" poster="${clip.thumbnail}" muted loop></video>
                <div class="play-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="5,3 19,12 5,21"/>
                    </svg>
                </div>
                <div class="clip-overlay">
                    <div class="clip-info">
                        <div class="clip-title">${clip.name}</div>
                        <div class="clip-meta">${clip.duration}s | ${clip.resolution}</div>
                    </div>
                </div>
            `;

            // Hover to play
            const video = clipCard.querySelector('video');
            clipCard.addEventListener('mouseenter', () => video.play());
            clipCard.addEventListener('mouseleave', () => {
                video.pause();
                video.currentTime = 0;
            });

            // Click to open modal (could be enhanced)
            clipCard.addEventListener('click', () => this.openClipModal(clip));

            this.clipsGrid.appendChild(clipCard);
        });
    }

    openClipModal(clip) {
        // Simple implementation - could be enhanced with a proper modal
        window.open(clip.url, '_blank');
    }

    resetToForm() {
        this.stopPolling();
        this.currentJobId = null;

        this.progressSection.classList.add('hidden');
        this.resultsSection.classList.add('hidden');
        this.form.classList.remove('hidden');
        this.form.classList.add('fade-in');

        // Reset progress
        this.updateProgress(0, 'Initializing...');
        this.resetSteps();
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;

        // Style inline for simplicity
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '16px 24px',
            borderRadius: '10px',
            background: type === 'error' ? '#ef4444' : type === 'success' ? '#22c55e' : '#8b5cf6',
            color: 'white',
            fontWeight: '500',
            boxShadow: '0 8px 30px rgba(0, 0, 0, 0.3)',
            zIndex: '1000',
            animation: 'fadeIn 0.3s ease'
        });

        document.body.appendChild(notification);

        // Auto remove
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease forwards';
            setTimeout(() => notification.remove(), 300);
        }, 4000);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new BRollGenerator();
});

// Add fadeOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-10px); }
    }
`;
document.head.appendChild(style);
