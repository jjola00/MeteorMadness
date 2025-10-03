/**
 * 
 * Sets up basic lighting for the scene
 */
class LightingManager {
    constructor(scene) {
        this.scene = scene;
        this.init();
    }
    
    init() {
        // Ambient light only - provides uniform lighting across the entire globe
        const ambientLight = new THREE.AmbientLight(0x404040, 5);
        this.scene.add(ambientLight);
    }
}
