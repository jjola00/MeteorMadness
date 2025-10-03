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
        const geometry = new THREE.SphereGeometry(2, 128, 128);
        
        // Load Earth textures with fallbacks
        const textureLoader = new THREE.TextureLoader();
        
        // Primary Earth texture
        const earthTexture = textureLoader.load(
            'https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_atmos_2048.jpg',
            undefined,
            undefined,
            (error) => {
                console.warn('Failed to load Earth texture, using fallback:', error);
                // Fallback: create a procedural Earth-like texture
                this.createFallbackEarthTexture();
            }
        );
        
        // Normal map for surface detail
        const normalTexture = textureLoader.load(
            'https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_normal_2048.jpg',
            undefined,
            undefined,
            (error) => {
                console.warn('Failed to load normal texture:', error);
            }
        );
        
        const material = new THREE.MeshPhongMaterial({
            map: earthTexture,
            normalMap: normalTexture,
            shininess: 30,
            transparent: false,
            side: THREE.FrontSide
        });
        
        this.globe = new THREE.Mesh(geometry, material);
        this.globe.castShadow = true;
        this.globe.receiveShadow = true;
        this.scene.add(this.globe);
        
        console.log('🌍 Earth globe created with high detail');
    }
    
    createFallbackEarthTexture() {
        // Create a procedural Earth-like texture as fallback
        const canvas = document.createElement('canvas');
        canvas.width = 1024;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');
        
        // Create Earth-like colors
        const gradient = ctx.createLinearGradient(0, 0, 0, 512);
        gradient.addColorStop(0, '#4a90e2'); // Ocean blue
        gradient.addColorStop(0.3, '#2e7d32'); // Forest green
        gradient.addColorStop(0.7, '#8d6e63'); // Brown land
        gradient.addColorStop(1, '#4a90e2'); // Ocean blue
        
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, 1024, 512);
        
        // Add some landmasses
        ctx.fillStyle = '#2e7d32';
        ctx.beginPath();
        ctx.arc(200, 150, 80, 0, 2 * Math.PI);
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(800, 300, 100, 0, 2 * Math.PI);
        ctx.fill();
        
        const texture = new THREE.CanvasTexture(canvas);
        if (this.globe && this.globe.material) {
            this.globe.material.map = texture;
            this.globe.material.needsUpdate = true;
        }
    }
    
    createAtmosphere() {
        const geometry = new THREE.SphereGeometry(2.1, 128, 128);
        const material = new THREE.MeshPhongMaterial({
            color: 0x87ceeb,
            transparent: true,
            opacity: 0.15,
            side: THREE.BackSide,
            shininess: 100
        });
        
        this.atmosphere = new THREE.Mesh(geometry, material);
        this.scene.add(this.atmosphere);
        
        // Add atmospheric glow effect
        const glowGeometry = new THREE.SphereGeometry(2.15, 64, 64);
        const glowMaterial = new THREE.MeshBasicMaterial({
            color: 0x87ceeb,
            transparent: true,
            opacity: 0.05,
            side: THREE.BackSide
        });
        
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        this.scene.add(glow);
    }
    
    createStars() {
        const geometry = new THREE.BufferGeometry();
        const material = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 1.0,
            transparent: true,
            opacity: 0.8
        });
        
        const vertices = [];
        const colors = [];
        
        for (let i = 0; i < 20000; i++) {
            // Create spherical distribution
            const radius = 1000 + Math.random() * 1000;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);
            
            const x = radius * Math.sin(phi) * Math.cos(theta);
            const y = radius * Math.sin(phi) * Math.sin(theta);
            const z = radius * Math.cos(phi);
            
            vertices.push(x, y, z);
            
            // Vary star colors slightly
            const colorVariation = 0.8 + Math.random() * 0.4;
            colors.push(colorVariation, colorVariation, colorVariation);
        }
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        
        material.vertexColors = true;
        this.stars = new THREE.Points(geometry, material);
        this.scene.add(this.stars);
        
        console.log('✨ Enhanced starfield created');
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
