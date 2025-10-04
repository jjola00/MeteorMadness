/**
 * 
 * Main asteroid configuration application
 */
class AsteroidConfigApp {
    constructor() {
        this.sceneManager = null;
        this.uiController = null;
        
        this.init();
    }
    
    init() {
        // Initialize 3D scene
        this.sceneManager = new AsteroidConfigSceneManager();
        
        // Initialize UI controller
        this.uiController = new AsteroidConfigUI(this.sceneManager);
        
        console.log('☄️ Asteroid Configuration App initialized!');
    }
}

// Initialize the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    try {
        console.log('🚀 Starting asteroid configuration app...');
        window.asteroidConfigApp = new AsteroidConfigApp();
        console.log('✅ Asteroid configuration app started successfully!');
    } catch (error) {
        console.error('❌ Failed to start asteroid configuration app:', error);
        console.error('Error details:', error.stack);
    }
});
