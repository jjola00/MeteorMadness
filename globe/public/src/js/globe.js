/**
 * 
 * Creates a Earth globe with textures
 */
class GlobeManager {
    constructor(scene) {
        this.scene = scene;
        this.globe = null;
        this.atmosphere = null;
        this.stars = null;
        
        this.init();
    }
    
    init() {
        this.createGlobe();
        this.createAtmosphere();
        this.createStars();
    }
    
    createGlobe() {
        const geometry = new THREE.SphereGeometry(2, 64, 64);
        
        // Load Earth texture
        const textureLoader = new THREE.TextureLoader();
        const earthTexture = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_atmos_2048.jpg');
        
        const material = new THREE.MeshPhongMaterial({
            map: earthTexture,
            shininess: 100,
            transparent: false
        });
        
        this.globe = new THREE.Mesh(geometry, material);
        this.scene.add(this.globe);
    }
    
    createAtmosphere() {
        const geometry = new THREE.SphereGeometry(2.1, 64, 64);
        const material = new THREE.MeshPhongMaterial({
            color: 0x87ceeb,
            transparent: true,
            opacity: 0.1,
            side: THREE.BackSide
        });
        
        this.atmosphere = new THREE.Mesh(geometry, material);
        this.scene.add(this.atmosphere);
    }
    
    createStars() {
        const geometry = new THREE.BufferGeometry();
        const material = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 0.5
        });
        
        const vertices = [];
        for (let i = 0; i < 10000; i++) {
            const x = (Math.random() - 0.5) * 2000;
            const y = (Math.random() - 0.5) * 2000;
            const z = (Math.random() - 0.5) * 2000;
            vertices.push(x, y, z);
        }
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        this.stars = new THREE.Points(geometry, material);
        this.scene.add(this.stars);
    }
    
    animateStars() {
        if (this.stars) {
            this.stars.rotation.x += 0.0001;
            this.stars.rotation.y += 0.0002;
        }
    }
    
    getGlobe() {
        return this.globe;
    }
}
