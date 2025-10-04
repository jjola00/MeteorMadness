/**
 * 
 * UI Controller for asteroid configuration panel
 */
class AsteroidConfigUI {
    constructor(sceneManager) {
        this.sceneManager = sceneManager;
        this.config = {
            name: 'Custom Asteroid',
            diameter: 500,
            speed: 20,
            type: 'mixed',
            features: {
                craters: true,
                ridges: true,
                bumps: true
            }
        };
        
        this.init();
    }
    
    init() {
        console.log('🎛️ Initializing asteroid configuration UI...');
        
        // Set initial values immediately
        this.setInitialValues();
        
        // Setup event listeners with immediate execution
        this.setupEventListeners();
        
        // Update display immediately
        this.updateDisplay();
        
        console.log('🎛️ Asteroid configuration UI initialized!');
    }
    
    setInitialValues() {
        // Set default values for all controls
        const nameInput = document.getElementById('asteroidName');
        if (nameInput) {
            nameInput.value = this.config.name;
        }
        
        const diameterSlider = document.getElementById('diameterSlider');
        if (diameterSlider) {
            diameterSlider.value = this.config.diameter;
        }
        
        const speedSlider = document.getElementById('speedSlider');
        if (speedSlider) {
            speedSlider.value = this.config.speed;
        }
        
        const typeSelect = document.getElementById('asteroidType');
        if (typeSelect) {
            typeSelect.value = this.config.type;
        }
        
        const cratersCheckbox = document.getElementById('craters');
        if (cratersCheckbox) {
            cratersCheckbox.checked = this.config.features.craters;
        }
        
        const ridgesCheckbox = document.getElementById('ridges');
        if (ridgesCheckbox) {
            ridgesCheckbox.checked = this.config.features.ridges;
        }
        
        const bumpsCheckbox = document.getElementById('bumps');
        if (bumpsCheckbox) {
            bumpsCheckbox.checked = this.config.features.bumps;
        }
        
        console.log('✅ Initial values set for all controls');
    }
    
    setupEventListeners() {
        // Setup event listeners immediately - no timeout needed
        try {
            console.log('🔗 Setting up event listeners...');
            
            // Name input
            const nameInput = document.getElementById('asteroidName');
            if (nameInput) {
                nameInput.addEventListener('input', (e) => {
                    this.config.name = e.target.value;
                    this.updateDisplay();
                    console.log('📝 Name updated:', this.config.name);
                });
                console.log('✅ Name input listener added');
            }
            
            // Diameter slider - REAL-TIME updates
            const diameterSlider = document.getElementById('diameterSlider');
            if (diameterSlider) {
                diameterSlider.addEventListener('input', (e) => {
                    this.config.diameter = parseInt(e.target.value);
                    this.updateDisplay();
                    this.updateAsteroidPreview();
                    console.log('📏 Diameter updated:', this.config.diameter);
                });
                console.log('✅ Diameter slider listener added');
            }
            
            // Speed slider - REAL-TIME updates
            const speedSlider = document.getElementById('speedSlider');
            if (speedSlider) {
                speedSlider.addEventListener('input', (e) => {
                    this.config.speed = parseInt(e.target.value);
                    this.updateDisplay();
                    console.log('⚡ Speed updated:', this.config.speed);
                });
                console.log('✅ Speed slider listener added');
            }
            
            // Asteroid type - REAL-TIME updates
            const typeSelect = document.getElementById('asteroidType');
            if (typeSelect) {
                typeSelect.addEventListener('change', (e) => {
                    this.config.type = e.target.value;
                    this.updateAsteroidPreview();
                    console.log('🪨 Type updated:', this.config.type);
                });
                console.log('✅ Type select listener added');
            }
            
            // Surface features checkboxes - REAL-TIME updates
            const cratersCheckbox = document.getElementById('craters');
            const ridgesCheckbox = document.getElementById('ridges');
            const bumpsCheckbox = document.getElementById('bumps');
            
            if (cratersCheckbox) {
                cratersCheckbox.addEventListener('change', (e) => {
                    this.config.features.craters = e.target.checked;
                    this.updateAsteroidPreview();
                    console.log('🕳️ Craters updated:', this.config.features.craters);
                });
                console.log('✅ Craters checkbox listener added');
            }
            
            if (ridgesCheckbox) {
                ridgesCheckbox.addEventListener('change', (e) => {
                    this.config.features.ridges = e.target.checked;
                    this.updateAsteroidPreview();
                    console.log('🏔️ Ridges updated:', this.config.features.ridges);
                });
                console.log('✅ Ridges checkbox listener added');
            }
            
            if (bumpsCheckbox) {
                bumpsCheckbox.addEventListener('change', (e) => {
                    this.config.features.bumps = e.target.checked;
                    this.updateAsteroidPreview();
                    console.log('🔺 Bumps updated:', this.config.features.bumps);
                });
                console.log('✅ Bumps checkbox listener added');
            }
            
            // Action buttons
            const previewBtn = document.getElementById('previewAsteroid');
            const launchBtn = document.getElementById('launchAsteroid');
            const backBtn = document.getElementById('backToGlobe');
            
            if (previewBtn) {
                previewBtn.addEventListener('click', () => {
                    this.updateAsteroidPreview();
                    console.log('🔄 Manual preview update triggered');
                });
                console.log('✅ Preview button listener added');
            }
            
            if (launchBtn) {
                launchBtn.addEventListener('click', () => {
                    this.launchAsteroid();
                    console.log('🚀 Launch asteroid triggered');
                });
                console.log('✅ Launch button listener added');
            }
            
            if (backBtn) {
                backBtn.addEventListener('click', () => {
                    this.goBackToGlobe();
                    console.log('🌍 Back to globe triggered');
                });
                console.log('✅ Back button listener added');
            }
            
            console.log('✅ All event listeners set up successfully!');
            
        } catch (error) {
            console.error('❌ Error setting up event listeners:', error);
        }
    }
    
    updateDisplay() {
        try {
            // Update diameter display
            const diameterDisplay = document.getElementById('diameterDisplay');
            if (diameterDisplay) {
                diameterDisplay.textContent = this.config.diameter;
            }
            
            // Update speed display
            const speedDisplay = document.getElementById('speedDisplay');
            if (speedDisplay) {
                speedDisplay.textContent = this.config.speed;
            }
            
            // Update preview stats
            const diameterValue = document.getElementById('diameterValue');
            const speedValue = document.getElementById('speedValue');
            
            if (diameterValue) {
                diameterValue.textContent = `${this.config.diameter}m`;
            }
            if (speedValue) {
                speedValue.textContent = `${this.config.speed} km/s`;
            }
            
            console.log('📊 Display updated:', this.config);
        } catch (error) {
            console.error('❌ Error updating display:', error);
        }
    }
    
    updateAsteroidPreview() {
        try {
            if (this.sceneManager && this.sceneManager.updateAsteroid) {
                this.sceneManager.updateAsteroid(this.config);
                console.log('🔄 Asteroid preview updated');
            } else {
                console.warn('⚠️ Scene manager not ready yet');
            }
        } catch (error) {
            console.error('❌ Error updating asteroid preview:', error);
            // Don't let preview update failure break the page
        }
    }
    
    launchAsteroid() {
        // Store configuration in localStorage for the main app to use
        localStorage.setItem('asteroidConfig', JSON.stringify(this.config));
        
        // Show success message
        this.showMessage('🚀 Asteroid configuration saved! Redirecting to globe...', 'success');
        
        // Redirect to main globe after a longer delay to let user see the message
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 4000);
    }
    
    goBackToGlobe() {
        window.location.href = 'index.html';
    }
    
    showMessage(text, type = 'info') {
        // Create message element
        const message = document.createElement('div');
        message.className = `message message-${type}`;
        message.textContent = text;
        
        // Style the message
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            ${type === 'success' ? 'background: linear-gradient(135deg, #28a745, #34ce57);' : ''}
            ${type === 'error' ? 'background: linear-gradient(135deg, #dc3545, #e74c3c);' : ''}
            ${type === 'info' ? 'background: linear-gradient(135deg, #17a2b8, #20c997);' : ''}
        `;
        
        // Add animation keyframes
        if (!document.getElementById('messageStyles')) {
            const style = document.createElement('style');
            style.id = 'messageStyles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Add to page
        document.body.appendChild(message);
        
        // Remove after 3 seconds
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 300);
        }, 3000);
    }
    
    getConfig() {
        return this.config;
    }
    
    setConfig(config) {
        this.config = { ...this.config, ...config };
        this.updateDisplay();
        this.updateAsteroidPreview();
    }
}
