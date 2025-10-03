/**
 * 
 * Main application that coordinates everything
 */
class GlobeApp {
    constructor() {
        this.sceneManager = null;
        this.globeManager = null;
        this.lightingManager = null;
        this.controlsManager = null;
        this.asteroids = [];
        this.isRunning = false;
        
        this.init();
    }
    
    init() {
        // initialising all managers
        this.sceneManager = new SceneManager();
        this.globeManager = new GlobeManager(this.sceneManager.getScene());
        this.lightingManager = new LightingManager(this.sceneManager.getScene());
        this.controlsManager = new ControlsManager(
            this.sceneManager.getCamera(),
            this.sceneManager.getRenderer()
        );
        
        this.start();
    }
    
    start() {
        this.isRunning = true;
        this.animate();
        console.log('🌍 Simple Three.js Globe loaded successfully!');
    }
    
    animate() {
        if (!this.isRunning) return;
        
        requestAnimationFrame(() => this.animate());
        
        // Update globe animations
        this.globeManager.animateStars();
        
        // Update asteroids
        this.updateAsteroids();
        
        // Update controls
        this.controlsManager.update();
        
        // Render the scene
        this.sceneManager.render();
    }
    
    spawnAsteroid() {
        const geometry = new THREE.SphereGeometry(0.1, 8, 6);
        const material = new THREE.MeshPhongMaterial({
            color: 0x8B4513,
            shininess: 10
        });
        
        const asteroid = new THREE.Mesh(geometry, material);
        
        // Random spawn position
        const distance = 8 + Math.random() * 4;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;
        
        asteroid.position.set(
            distance * Math.sin(phi) * Math.cos(theta),
            distance * Math.sin(phi) * Math.sin(theta),
            distance * Math.cos(phi)
        );
        
        // Random velocity toward Earth
        const direction = new THREE.Vector3().subVectors(new THREE.Vector3(0, 0, 0), asteroid.position).normalize();
        direction.x += (Math.random() - 0.5) * 0.3;
        direction.y += (Math.random() - 0.5) * 0.3;
        direction.z += (Math.random() - 0.5) * 0.3;
        direction.normalize();
        
        asteroid.userData = {
            velocity: direction.multiplyScalar(0.1 + Math.random() * 0.2)
        };
        
        this.sceneManager.getScene().add(asteroid);
        this.asteroids.push(asteroid);
        
        console.log('☄️ Asteroid spawned!');
    }
    
    clearAsteroids() {
        this.asteroids.forEach(asteroid => {
            this.sceneManager.getScene().remove(asteroid);
        });
        this.asteroids = [];
        console.log('🗑️ All asteroids cleared!');
    }
    
    updateAsteroids() {
        for (let i = this.asteroids.length - 1; i >= 0; i--) {
            const asteroid = this.asteroids[i];
            
            // Apply gravity
            const directionToEarth = new THREE.Vector3().subVectors(new THREE.Vector3(0, 0, 0), asteroid.position).normalize();
            const gravityForce = directionToEarth.multiplyScalar(0.02);
            asteroid.userData.velocity.add(gravityForce);
            
            // Update position
            asteroid.position.add(asteroid.userData.velocity);
            
            // Check collision
            if (asteroid.position.length() <= 2.1) {
                this.handleImpact(asteroid, i);
            }
        }
    }
    
    handleImpact(asteroid, index) {
        // Create explosion effect
        const explosionGeometry = new THREE.SphereGeometry(0.2, 8, 6);
        const explosionMaterial = new THREE.MeshBasicMaterial({
            color: 0xff6600,
            transparent: true,
            opacity: 0.8
        });
        
        const explosion = new THREE.Mesh(explosionGeometry, explosionMaterial);
        explosion.position.copy(asteroid.position);
        this.sceneManager.getScene().add(explosion);
        
        // Remove explosion after 2 seconds
        setTimeout(() => {
            this.sceneManager.getScene().remove(explosion);
        }, 2000);
        
        // Remove asteroid
        this.sceneManager.getScene().remove(asteroid);
        this.asteroids.splice(index, 1);
        
        console.log('💥 Asteroid impact!');
    }
}

// Initialising the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.globeApp = new GlobeApp();
});