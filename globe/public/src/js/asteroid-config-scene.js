/**
 * 
 * 3D Scene manager for asteroid configuration preview
 */
class AsteroidConfigSceneManager {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.asteroid = null;
        this.stars = null;
        
        this.init();
    }
    
    init() {
        // Wait a bit for DOM to be fully ready
        setTimeout(() => {
            try {
                console.log('🎬 Initializing 3D scene...');
                
                // Create scene
                this.scene = new THREE.Scene();
                console.log('✅ Scene created');
                
                // Create camera
                this.camera = new THREE.PerspectiveCamera(
                    75, 
                    window.innerWidth / window.innerHeight, 
                    0.1, 
                    1000
                );
                console.log('✅ Camera created');
                
                // Create renderer
                this.renderer = new THREE.WebGLRenderer({ 
                    antialias: true,
                    alpha: true,
                    powerPreference: "high-performance"
                });
                this.renderer.setSize(window.innerWidth, window.innerHeight);
                this.renderer.setClearColor(0x000000);
                this.renderer.shadowMap.enabled = false;
                this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
                this.renderer.toneMappingExposure = 1.0;
                console.log('✅ Renderer created');
                
                // Get container and append renderer
                const container = document.getElementById('asteroidPreview');
                if (!container) {
                    console.error('❌ Asteroid preview container not found!');
                    throw new Error('Asteroid preview container not found!');
                }
                container.appendChild(this.renderer.domElement);
                console.log('✅ Renderer added to container');
                
                // Set camera position
                this.camera.position.z = 5;
                
                // Setup controls
                this.setupControls();
                console.log('✅ Controls setup');
                
                // Create lighting
                this.setupLighting();
                console.log('✅ Lighting setup');
                
                // Create starfield
                this.createStarfield();
                console.log('✅ Starfield created');
                
                // Create initial asteroid with default config - SIMPLIFIED
                try {
                    this.createSimpleAsteroid();
                    console.log('✅ Simple asteroid created');
                } catch (asteroidError) {
                    console.error('❌ Error creating asteroid:', asteroidError);
                    // Don't let asteroid creation failure break the whole page
                }
                
                // Handle window resize
                this.setupResizeHandler();
                
                // Start animation
                this.animate();
                
                console.log('🪨 Asteroid configuration scene initialized successfully!');
            } catch (error) {
                console.error('❌ Error initializing scene:', error);
                console.error('Error details:', error.stack);
            }
        }, 200);
    }
    
    setupControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.autoRotate = true;
        this.controls.autoRotateSpeed = 0.5;
        this.controls.enableZoom = true;
        this.controls.minDistance = 2;
        this.controls.maxDistance = 10;
    }
    
    setupLighting() {
        // Uniform lighting for asteroid preview
        const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 5, 5);
        this.scene.add(directionalLight);
        
        const pointLight1 = new THREE.PointLight(0xffffff, 0.6, 100);
        pointLight1.position.set(5, 0, 0);
        this.scene.add(pointLight1);
        
        const pointLight2 = new THREE.PointLight(0xffffff, 0.6, 100);
        pointLight2.position.set(-5, 0, 0);
        this.scene.add(pointLight2);
    }
    
    createStarfield() {
        const geometry = new THREE.BufferGeometry();
        const material = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 1.0,
            transparent: true,
            opacity: 0.8
        });
        
        const vertices = [];
        const colors = [];
        
        for (let i = 0; i < 15000; i++) {
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
    }
    
    createAsteroid(config = null) {
        // Remove existing asteroid
        if (this.asteroid) {
            this.scene.remove(this.asteroid);
            if (this.asteroid.geometry) this.asteroid.geometry.dispose();
            if (this.asteroid.material) this.asteroid.material.dispose();
        }
        
        // Use provided config or default
        const asteroidConfig = config || {
            diameter: 500,
            type: 'mixed',
            features: {
                craters: true,
                ridges: true,
                bumps: true
            }
        };
        
        console.log('🪨 Creating asteroid with config:', asteroidConfig);
        
        // Create asteroid geometry
        const geometry = this.createAsteroidGeometry();
        const material = this.createAsteroidMaterial(asteroidConfig.type);
        
        this.asteroid = new THREE.Mesh(geometry, material);
        
        // Scale based on diameter (convert meters to Three.js units)
        const scale = asteroidConfig.diameter / 1000; // 1000m = 1 unit
        this.asteroid.scale.setScalar(scale);
        
        this.scene.add(this.asteroid);
        
        // Start rotation animation
        this.animateAsteroid();
        
        console.log('✅ Asteroid created and added to scene');
    }
    
    createSimpleAsteroid() {
        console.log('🪨 Creating simple asteroid...');
        
        // Remove existing asteroid
        if (this.asteroid) {
            this.scene.remove(this.asteroid);
            if (this.asteroid.geometry) this.asteroid.geometry.dispose();
            if (this.asteroid.material) this.asteroid.material.dispose();
        }
        
        // Create simple sphere geometry
        const geometry = new THREE.SphereGeometry(0.5, 16, 16);
        
        // Create simple grey material
        const material = new THREE.MeshPhongMaterial({
            color: 0x808080,  // Grey color
            shininess: 10
        });
        
        // Create mesh
        this.asteroid = new THREE.Mesh(geometry, material);
        
        // Add to scene
        this.scene.add(this.asteroid);
        
        // Start rotation animation
        this.animateAsteroid();
        
        console.log('✅ Simple asteroid created successfully');
    }
    
    updateAsteroid(config) {
        console.log('🔄 Updating asteroid with config:', config);
        
        if (!this.asteroid) {
            console.warn('⚠️ No asteroid to update, creating simple one');
            this.createSimpleAsteroid();
            return;
        }
        
        // Update scale based on diameter
        const scale = config.diameter / 1000; // 1000m = 1 unit
        this.asteroid.scale.setScalar(scale);
        
        console.log('✅ Simple asteroid updated successfully');
    }
    
    createAsteroidGeometry() {
        // Start with sphere for clean ball shape
        const geometry = new THREE.SphereGeometry(1, 32, 32);
        
        // Add subtle noise to vertices for bumpy texture
        const positions = geometry.attributes.position.array;
        
        for (let i = 0; i < positions.length; i += 3) {
            // Add gentle random noise to each vertex
            const noise1 = (Math.random() - 0.5) * 0.15;
            const noise2 = (Math.random() - 0.5) * 0.15;
            const noise3 = (Math.random() - 0.5) * 0.15;
            
            positions[i] += noise1;     // x
            positions[i + 1] += noise2; // y
            positions[i + 2] += noise3; // z
        }
        
        geometry.attributes.position.needsUpdate = true;
        geometry.computeVertexNormals();
        
        return geometry;
    }
    
    // Removed complex asteroid details - keeping it simple with just bumpy texture
    
    createAsteroidMaterial(type = 'mixed') {
        // Simple grey material for all types
        const material = new THREE.MeshPhongMaterial({
            color: 0x808080,  // Grey color
            shininess: 10,
            specular: 0x222222,
            transparent: false,
            side: THREE.FrontSide
        });
        
        // Add bumpy texture
        this.addBumpyTexture(material);
        
        console.log('🎨 Simple grey material created');
        return material;
    }
    
    addBumpyTexture(material) {
        // Create simple bumpy texture
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');
        
        // Base grey color
        ctx.fillStyle = '#808080';
        ctx.fillRect(0, 0, 512, 512);
        
        // Add subtle bumpy patterns
        for (let i = 0; i < 50; i++) {
            const x = Math.random() * 512;
            const y = Math.random() * 512;
            const radius = Math.random() * 30 + 10;
            
            const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
            gradient.addColorStop(0, 'rgba(0,0,0,0.3)');
            gradient.addColorStop(1, 'rgba(0,0,0,0)');
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, 2 * Math.PI);
            ctx.fill();
        }
        
        const texture = new THREE.CanvasTexture(canvas);
        material.map = texture;
        
        // Create simple normal map for bumpy effect
        this.createSimpleNormalMap(material);
    }
    
    createSimpleNormalMap(material) {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        
        // Create simple normal map
        const imageData = ctx.createImageData(256, 256);
        const data = imageData.data;
        
        for (let i = 0; i < data.length; i += 4) {
            const noise = Math.random();
            data[i] = 128 + noise * 40;     // R - subtle variation
            data[i + 1] = 128 + noise * 40; // G - subtle variation
            data[i + 2] = 255;              // B
            data[i + 3] = 255;              // A
        }
        
        ctx.putImageData(imageData, 0, 0);
        const normalTexture = new THREE.CanvasTexture(canvas);
        material.normalMap = normalTexture;
        material.normalScale = new THREE.Vector2(0.5, 0.5);
    }
    
    animateAsteroid() {
        if (!this.asteroid) return;
        
        const animate = () => {
            if (!this.asteroid) return;
            
            // Rotate asteroid slowly
            this.asteroid.rotation.x += 0.005;
            this.asteroid.rotation.y += 0.01;
            this.asteroid.rotation.z += 0.003;
            
            requestAnimationFrame(animate);
        };
        animate();
    }
    
    updateAsteroid(config) {
        if (!this.asteroid) return;
        
        // Update size based on diameter
        const scale = config.diameter / 500; // Base diameter is 500m
        this.asteroid.scale.setScalar(scale);
        
        // Update material color based on type
        this.updateAsteroidMaterial(config.type);
        
        // Update surface features
        this.updateSurfaceFeatures(config);
    }
    
    updateAsteroidMaterial(type) {
        const colors = {
            'carbonaceous': 0x2F4F4F,  // Dark slate gray
            'silicate': 0x696969,       // Dim gray
            'metallic': 0x8B4513,       // Saddle brown
            'mixed': 0x556B2F           // Dark olive green
        };
        
        this.asteroid.material.color.setHex(colors[type] || 0x8B4513);
    }
    
    updateSurfaceFeatures(config) {
        // This would update the geometry based on checkbox selections
        // For now, we'll keep the same geometry but could add more detail
        // based on the surface feature selections
    }
    
    setupResizeHandler() {
        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }
    
    animate() {
        requestAnimationFrame(this.animate.bind(this)); // Fix: bind 'this' properly
        
        // Update controls
        if (this.controls) {
            this.controls.update();
        }
        
        // Animate stars
        if (this.stars) {
            this.stars.rotation.x += 0.0001;
            this.stars.rotation.y += 0.0002;
        }
        
        // Render the scene
        this.renderer.render(this.scene, this.camera);
    }
    
    getAsteroidConfig() {
        if (!this.asteroid) return null;
        
        return {
            diameter: this.asteroid.scale.x * 500, // Convert scale back to meters
            type: 'mixed', // Default type
            speed: 20 // Default speed
        };
    }
}
