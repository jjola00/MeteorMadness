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
        // Enhanced lighting system for realistic rendering
        
        // Ambient light for overall illumination
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // Directional light simulating sunlight
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
        directionalLight.position.set(5, 5, 5);
        directionalLight.castShadow = true;
        
        // Configure shadow properties
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -10;
        directionalLight.shadow.camera.right = 10;
        directionalLight.shadow.camera.top = 10;
        directionalLight.shadow.camera.bottom = -10;
        
        this.scene.add(directionalLight);
        
        // Point light for additional detail
        const pointLight = new THREE.PointLight(0xffffff, 0.5, 100);
        pointLight.position.set(-5, 3, 5);
        this.scene.add(pointLight);
        
        // Hemisphere light for sky/ground color variation
        const hemisphereLight = new THREE.HemisphereLight(0x87ceeb, 0x2e7d32, 0.3);
        this.scene.add(hemisphereLight);
        
        console.log('💡 Enhanced lighting system initialized');
    }
}
