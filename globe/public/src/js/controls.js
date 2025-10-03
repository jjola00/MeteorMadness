/**
 * 
 * Handles orbit controls and basic interactions
 */
class ControlsManager {
    constructor(camera, renderer) {
        this.camera = camera;
        this.renderer = renderer;
        this.controls = null;
        
        this.init();
    }
    
    init() {
        this.setupOrbitControls();
        this.setupKeyboardControls();
    }
    
    setupOrbitControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.autoRotate = true;
        this.controls.autoRotateSpeed = 0.5;
        this.controls.enableZoom = true;
        this.controls.minDistance = 3;
        this.controls.maxDistance = 10;
    }
    
    setupKeyboardControls() {
        window.addEventListener('keydown', (event) => {
            switch(event.code) {
                case 'Space':
                    event.preventDefault();
                    this.spawnAsteroid();
                    break;
                case 'KeyC':
                    event.preventDefault();
                    this.clearAsteroids();
                    break;
            }
        });
    }
    
    spawnAsteroid() {
        // Simple asteroid spawning
        if (window.globeApp && window.globeApp.spawnAsteroid) {
            window.globeApp.spawnAsteroid();
        }
    }
    
    clearAsteroids() {
        // Clear asteroids
        if (window.globeApp && window.globeApp.clearAsteroids) {
            window.globeApp.clearAsteroids();
        }
    }
    
    update() {
        if (this.controls) {
            this.controls.update();
        }
    }
}