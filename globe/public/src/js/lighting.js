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
        // Uniform lighting system - no day/night effect
        
        // Strong ambient light for even illumination across entire globe
        const ambientLight = new THREE.AmbientLight(0xffffff, 1);
        this.scene.add(ambientLight);
        
        // Soft directional light for subtle depth without shadows
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.3);
        directionalLight.position.set(5, 5, 5);
        directionalLight.castShadow = false; // Disable shadows for uniform lighting
        
        this.scene.add(directionalLight);
        
        // Additional point lights for even coverage
        const pointLight1 = new THREE.PointLight(0xffffff, 0.4, 100);
        pointLight1.position.set(5, 0, 0);
        this.scene.add(pointLight1);
        
        const pointLight2 = new THREE.PointLight(0xffffff, 0.4, 100);
        pointLight2.position.set(-5, 0, 0);
        this.scene.add(pointLight2);
        
        const pointLight3 = new THREE.PointLight(0xffffff, 0.4, 100);
        pointLight3.position.set(0, 5, 0);
        this.scene.add(pointLight3);
        
        const pointLight4 = new THREE.PointLight(0xffffff, 0.4, 100);
        pointLight4.position.set(0, -5, 0);
        this.scene.add(pointLight4);
        
        console.log('💡 Uniform lighting system initialized - no day/night effect');
    }
}
