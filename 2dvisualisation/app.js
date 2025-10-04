// Main application entry point

import { ImpactVisualizer } from './visualizer.js';

// Global visualizer instance
let visualizer;

// Global functions for HTML event handlers
window.loadScenarioWrapper = function(scenarioId, buttonElement) {
    // Update active button
    document.querySelectorAll('.scenario-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    if (buttonElement) {
        buttonElement.classList.add('active');
    }
    
    // Load the scenario
    visualizer.loadScenario(scenarioId);
};

window.toggleLayer = function(layerType) {
    visualizer.toggleLayer(layerType);
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Asteroid Impact Visualizer...');
    
    visualizer = new ImpactVisualizer();
    visualizer.initialize();
    
    // Set initial active button
    const firstButton = document.querySelector('.scenario-btn');
    if (firstButton) {
        firstButton.classList.add('active');
    }
    
    console.log('Application initialized successfully');
});