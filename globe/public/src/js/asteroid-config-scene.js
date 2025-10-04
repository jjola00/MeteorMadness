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
        // Realistic lighting setup for asteroid preview
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
        this.scene.add(ambientLight);
        
        // Main directional light (sunlight)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
        directionalLight.position.set(5, 3, 2);
        directionalLight.castShadow = false;
        this.scene.add(directionalLight);
        
        // Secondary fill light
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
        fillLight.position.set(-3, 2, -1);
        this.scene.add(fillLight);
        
        console.log('✅ Realistic lighting setup complete');
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
        console.log('🪨 Creating simple asteroid with craters...');
        
        // Remove existing asteroid
        if (this.asteroid) {
            this.scene.remove(this.asteroid);
            if (this.asteroid.geometry) this.asteroid.geometry.dispose();
            if (this.asteroid.material) this.asteroid.material.dispose();
        }
        
        // Create sphere geometry with more detail for craters
        const geometry = new THREE.IcosahedronGeometry(0.5, 6); // Better base geometry
        
        // Create shader-based asteroid material
        const material = this.createAsteroidShaderMaterial();
        
        // Create mesh
        this.asteroid = new THREE.Mesh(geometry, material);
        
        // Add to scene
        this.scene.add(this.asteroid);
        
        // Start rotation animation
        this.animateAsteroid();
        
        console.log('✅ Simple asteroid with craters created successfully');
    }
    
    addCratersToGeometry(geometry) {
        const positions = geometry.attributes.position.array;
        const vertexCount = positions.length / 3;

        const craterCount = 12; // more craters

        for (let crater = 0; crater < craterCount; crater++) {
            const craterCenterIndex = Math.floor(Math.random() * vertexCount) * 3;

            // Bigger craters relative to sphere radius (0.5)
            const craterRadius = 0.15 + Math.random() * 0.25; 
            const craterDepth = 0.05 + Math.random() * 0.1;   

            const cx = positions[craterCenterIndex];
            const cy = positions[craterCenterIndex + 1];
            const cz = positions[craterCenterIndex + 2];

            for (let i = 0; i < positions.length; i += 3) {
                const dx = positions[i] - cx;
                const dy = positions[i + 1] - cy;
                const dz = positions[i + 2] - cz;
                const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

                if (distance < craterRadius) {
                    const factor = 1 - (distance / craterRadius);
                    const craterEffect = craterDepth * factor * factor;
                    
                    // Clamp crater effect to prevent collapsing
                    const clampedEffect = Math.min(craterEffect, 0.15);
                    
                    // push inward
                    positions[i] -= (dx / distance) * clampedEffect;
                    positions[i + 1] -= (dy / distance) * clampedEffect;
                    positions[i + 2] -= (dz / distance) * clampedEffect;
                }
            }
        }

        geometry.attributes.position.needsUpdate = true;
        geometry.computeVertexNormals();

        console.log(`✅ Added ${craterCount} visible craters`);
    }
    
    createAsteroidShaderMaterial() {
        const material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 },
                baseColor: { value: new THREE.Color(0x6B6B6B) },
                lightDirection: { value: new THREE.Vector3(1.0, 1.0, 1.0).normalize() }
            },
            vertexShader: `
                uniform float time;
                varying vec3 vNormal;
                varying vec3 vPosition;
                varying vec3 vWorldPosition;
                
                // Simplex noise function
                vec3 mod289(vec3 x) {
                    return x - floor(x * (1.0 / 289.0)) * 289.0;
                }
                
                vec4 mod289(vec4 x) {
                    return x - floor(x * (1.0 / 289.0)) * 289.0;
                }
                
                vec4 permute(vec4 x) {
                    return mod289(((x*34.0)+1.0)*x);
                }
                
                vec4 taylorInvSqrt(vec4 r) {
                    return 1.79284291400159 - 0.85373472095314 * r;
                }
                
                float snoise(vec3 v) {
                    const vec2 C = vec2(1.0/6.0, 1.0/3.0);
                    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
                    
                    vec3 i = floor(v + dot(v, C.yyy));
                    vec3 x0 = v - i + dot(i, C.xxx);
                    
                    vec3 g = step(x0.yzx, x0.xyz);
                    vec3 l = 1.0 - g;
                    vec3 i1 = min(g.xyz, l.zxy);
                    vec3 i2 = max(g.xyz, l.zxy);
                    
                    vec3 x1 = x0 - i1 + C.xxx;
                    vec3 x2 = x0 - i2 + C.yyy;
                    vec3 x3 = x0 - D.yyy;
                    
                    i = mod289(i);
                    vec4 p = permute(permute(permute(
                        i.z + vec4(0.0, i1.z, i2.z, 1.0))
                        + i.y + vec4(0.0, i1.y, i2.y, 1.0))
                        + i.x + vec4(0.0, i1.x, i2.x, 1.0));
                    
                    float n_ = 0.142857142857;
                    vec3 ns = n_ * D.wyz - D.xzx;
                    
                    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
                    
                    vec4 x_ = floor(j * ns.z);
                    vec4 y_ = floor(j - 7.0 * x_);
                    
                    vec4 x = x_ *ns.x + ns.yyyy;
                    vec4 y = y_ *ns.x + ns.yyyy;
                    vec4 h = 1.0 - abs(x) - abs(y);
                    
                    vec4 b0 = vec4(x.xy, y.xy);
                    vec4 b1 = vec4(x.zw, y.zw);
                    
                    vec4 s0 = floor(b0)*2.0 + 1.0;
                    vec4 s1 = floor(b1)*2.0 + 1.0;
                    vec4 sh = -step(h, vec4(0.0));
                    
                    vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
                    vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
                    
                    vec3 p0 = vec3(a0.xy, h.x);
                    vec3 p1 = vec3(a0.zw, h.y);
                    vec3 p2 = vec3(a1.xy, h.z);
                    vec3 p3 = vec3(a1.zw, h.w);
                    
                    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
                    p0 *= norm.x;
                    p1 *= norm.y;
                    p2 *= norm.z;
                    p3 *= norm.w;
                    
                    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
                    m = m * m;
                    return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
                }
                
                // Fractal Brownian Motion
                float fbm(vec3 p) {
                    float value = 0.0;
                    float amplitude = 0.5;
                    float frequency = 1.0;
                    
                    for (int i = 0; i < 4; i++) {
                        value += amplitude * snoise(p * frequency);
                        amplitude *= 0.5;
                        frequency *= 2.0;
                    }
                    return value;
                }
                
                // Crater function
                float crater(vec3 p, vec3 center, float radius, float depth) {
                    float d = distance(p, center);
                    if (d < radius) {
                        float falloff = 1.0 - (d / radius);
                        return -depth * falloff * falloff;
                    }
                    return 0.0;
                }
                
                void main() {
                    vNormal = normal;
                    vPosition = position;
                    vWorldPosition = (modelMatrix * vec4(position, 1.0)).xyz;
                    
                    // Generate crater centers (fixed for consistency)
                    vec3 crater1 = vec3(0.3, 0.2, 0.1);
                    vec3 crater2 = vec3(-0.2, 0.4, -0.3);
                    vec3 crater3 = vec3(0.1, -0.3, 0.4);
                    vec3 crater4 = vec3(-0.4, -0.1, 0.2);
                    
                    // Apply FBM noise for rocky surface
                    float noise = fbm(position * 3.0 + time * 0.1);
                    float displacement = noise * 0.05;
                    
                    // Add craters
                    displacement += crater(position, crater1, 0.15, 0.08);
                    displacement += crater(position, crater2, 0.12, 0.06);
                    displacement += crater(position, crater3, 0.18, 0.1);
                    displacement += crater(position, crater4, 0.14, 0.07);
                    
                    // Apply displacement along normal
                    vec3 newPosition = position + normal * displacement;
                    
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
                }
            `,
            fragmentShader: `
                uniform vec3 baseColor;
                uniform vec3 lightDirection;
                varying vec3 vNormal;
                varying vec3 vPosition;
                varying vec3 vWorldPosition;
                
                // Simplex noise (same as vertex shader)
                vec3 mod289(vec3 x) {
                    return x - floor(x * (1.0 / 289.0)) * 289.0;
                }
                
                vec4 mod289(vec4 x) {
                    return x - floor(x * (1.0 / 289.0)) * 289.0;
                }
                
                vec4 permute(vec4 x) {
                    return mod289(((x*34.0)+1.0)*x);
                }
                
                vec4 taylorInvSqrt(vec4 r) {
                    return 1.79284291400159 - 0.85373472095314 * r;
                }
                
                float snoise(vec3 v) {
                    const vec2 C = vec2(1.0/6.0, 1.0/3.0);
                    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
                    
                    vec3 i = floor(v + dot(v, C.yyy));
                    vec3 x0 = v - i + dot(i, C.xxx);
                    
                    vec3 g = step(x0.yzx, x0.xyz);
                    vec3 l = 1.0 - g;
                    vec3 i1 = min(g.xyz, l.zxy);
                    vec3 i2 = max(g.xyz, l.zxy);
                    
                    vec3 x1 = x0 - i1 + C.xxx;
                    vec3 x2 = x0 - i2 + C.yyy;
                    vec3 x3 = x0 - D.yyy;
                    
                    i = mod289(i);
                    vec4 p = permute(permute(permute(
                        i.z + vec4(0.0, i1.z, i2.z, 1.0))
                        + i.y + vec4(0.0, i1.y, i2.y, 1.0))
                        + i.x + vec4(0.0, i1.x, i2.x, 1.0));
                    
                    float n_ = 0.142857142857;
                    vec3 ns = n_ * D.wyz - D.xzx;
                    
                    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
                    
                    vec4 x_ = floor(j * ns.z);
                    vec4 y_ = floor(j - 7.0 * x_);
                    
                    vec4 x = x_ *ns.x + ns.yyyy;
                    vec4 y = y_ *ns.x + ns.yyyy;
                    vec4 h = 1.0 - abs(x) - abs(y);
                    
                    vec4 b0 = vec4(x.xy, y.xy);
                    vec4 b1 = vec4(x.zw, y.zw);
                    
                    vec4 s0 = floor(b0)*2.0 + 1.0;
                    vec4 s1 = floor(b1)*2.0 + 1.0;
                    vec4 sh = -step(h, vec4(0.0));
                    
                    vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
                    vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
                    
                    vec3 p0 = vec3(a0.xy, h.x);
                    vec3 p1 = vec3(a0.zw, h.y);
                    vec3 p2 = vec3(a1.xy, h.z);
                    vec3 p3 = vec3(a1.zw, h.w);
                    
                    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
                    p0 *= norm.x;
                    p1 *= norm.y;
                    p2 *= norm.z;
                    p3 *= norm.w;
                    
                    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
                    m = m * m;
                    return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
                }
                
                void main() {
                    // Calculate lighting
                    vec3 lightDir = normalize(lightDirection);
                    vec3 normal = normalize(vNormal);
                    float diff = max(dot(normal, lightDir), 0.0);
                    
                    // Add surface variation with noise
                    float surfaceNoise = snoise(vPosition * 8.0) * 0.1;
                    vec3 color = baseColor + vec3(surfaceNoise);
                    
                    // Apply lighting
                    color = color * (0.3 + diff * 0.7);
                    
                    gl_FragColor = vec4(color, 1.0);
                }
            `,
            side: THREE.FrontSide
        });
        
        console.log('✅ Shader-based asteroid material created');
        return material;
    }
    
    addNoiseDisplacement(geometry) {
        const positions = geometry.attributes.position;
        const vertexCount = positions.count;
        
        // Simple noise function (simplified Perlin-like noise)
        function noise(x, y, z) {
            const n = Math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453;
            return (n - Math.floor(n)) * 2 - 1; // Return -1 to 1
        }
        
        // Apply noise displacement to create natural rocky surface
        for (let i = 0; i < vertexCount; i++) {
            const x = positions.getX(i);
            const y = positions.getY(i);
            const z = positions.getZ(i);
            
            // Calculate noise at multiple scales for natural variation
            const noise1 = noise(x * 3, y * 3, z * 3) * 0.03;
            const noise2 = noise(x * 8, y * 8, z * 8) * 0.015;
            const noise3 = noise(x * 15, y * 15, z * 15) * 0.008;
            
            const totalNoise = noise1 + noise2 + noise3;
            
            // Displace along normal direction to maintain sphere shape
            const length = Math.sqrt(x * x + y * y + z * z);
            const nx = x / length;
            const ny = y / length;
            const nz = z / length;
            
            // Apply displacement
            positions.setXYZ(
                i,
                x + nx * totalNoise,
                y + ny * totalNoise,
                z + nz * totalNoise
            );
        }
        
        positions.needsUpdate = true;
        geometry.computeVertexNormals();
        
        console.log('✅ Added noise displacement for rocky surface');
    }
    
    addCraterShadowTexture(material) {
        // Create texture with darker crater shadows
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');
        
        // Base grey rock color
        ctx.fillStyle = '#6B6B6B';
        ctx.fillRect(0, 0, 512, 512);
        
        // Add darker crater shadows
        for (let i = 0; i < 15; i++) {
            const x = Math.random() * 512;
            const y = Math.random() * 512;
            const radius = Math.random() * 40 + 20;
            
            const gradient = ctx.createRadialGradient(x, y, 0, x, y, radius);
            gradient.addColorStop(0, 'rgba(0,0,0,0.6)'); // Dark center
            gradient.addColorStop(0.7, 'rgba(0,0,0,0.3)'); // Medium shadow
            gradient.addColorStop(1, 'rgba(0,0,0,0)'); // Fade out
            
            ctx.fillStyle = gradient;
            ctx.beginPath();
            ctx.arc(x, y, radius, 0, 2 * Math.PI);
            ctx.fill();
        }
        
        const texture = new THREE.CanvasTexture(canvas);
        material.map = texture;
        
        console.log('✅ Added crater shadow texture');
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
        
        // Animate shader time uniform
        if (this.asteroid && this.asteroid.material.uniforms) {
            this.asteroid.material.uniforms.time.value += 0.01;
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
