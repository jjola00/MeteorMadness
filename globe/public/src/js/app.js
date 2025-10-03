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
        // Create realistic rock-like asteroid
        const asteroid = this.createRealisticAsteroid();
        
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
            velocity: direction.multiplyScalar(0.1 + Math.random() * 0.2),
            rotationSpeed: {
                x: (Math.random() - 0.5) * 0.1,
                y: (Math.random() - 0.5) * 0.1,
                z: (Math.random() - 0.5) * 0.1
            },
            scale: 0.8 + Math.random() * 0.4, // Random size variation
            debris: [] // For particle effects
        };
        
        // Apply random scale
        asteroid.scale.setScalar(asteroid.userData.scale);
        
        this.sceneManager.getScene().add(asteroid);
        this.asteroids.push(asteroid);
        
        console.log('☄️ Realistic asteroid spawned!');
    }
    
    createRealisticAsteroid() {
        // Create irregular rock-like geometry
        const geometry = this.createAsteroidGeometry();
        const material = this.createAsteroidMaterial();
        
        const asteroid = new THREE.Mesh(geometry, material);
        asteroid.castShadow = true;
        asteroid.receiveShadow = true;
        
        // Add some random rotation offset
        asteroid.rotation.set(
            Math.random() * Math.PI * 2,
            Math.random() * Math.PI * 2,
            Math.random() * Math.PI * 2
        );
        
        return asteroid;
    }
    
    createAsteroidGeometry() {
        // Start with icosahedron for more natural shape
        const geometry = new THREE.IcosahedronGeometry(0.15, 3);
        
        // Add noise to vertices for rocky appearance
        const positions = geometry.attributes.position.array;
        const normals = geometry.attributes.normal.array;
        
        for (let i = 0; i < positions.length; i += 3) {
            // Add random noise to each vertex
            const noise1 = (Math.random() - 0.5) * 0.1;
            const noise2 = (Math.random() - 0.5) * 0.1;
            const noise3 = (Math.random() - 0.5) * 0.1;
            
            positions[i] += noise1;     // x
            positions[i + 1] += noise2; // y
            positions[i + 2] += noise3; // z
        }
        
        // Add more detail with subdivision
        geometry.computeVertexNormals();
        
        // Add craters and bumps
        this.addAsteroidDetails(geometry);
        
        return geometry;
    }
    
    addAsteroidDetails(geometry) {
        const positions = geometry.attributes.position.array;
        
        // Add some craters
        for (let crater = 0; crater < 5; crater++) {
            const craterCenter = Math.floor(Math.random() * positions.length / 3) * 3;
            const craterRadius = 0.02 + Math.random() * 0.03;
            const craterDepth = 0.01 + Math.random() * 0.02;
            
            for (let i = 0; i < positions.length; i += 3) {
                const distance = Math.sqrt(
                    Math.pow(positions[i] - positions[craterCenter], 2) +
                    Math.pow(positions[i + 1] - positions[craterCenter + 1], 2) +
                    Math.pow(positions[i + 2] - positions[craterCenter + 2], 2)
                );
                
                if (distance < craterRadius) {
                    const factor = 1 - (distance / craterRadius) * craterDepth;
                    const direction = new THREE.Vector3(
                        positions[i] - positions[craterCenter],
                        positions[i + 1] - positions[craterCenter + 1],
                        positions[i + 2] - positions[craterCenter + 2]
                    ).normalize();
                    
                    positions[i] -= direction.x * craterDepth * factor;
                    positions[i + 1] -= direction.y * craterDepth * factor;
                    positions[i + 2] -= direction.z * craterDepth * factor;
                }
            }
        }
        
        geometry.attributes.position.needsUpdate = true;
        geometry.computeVertexNormals();
    }
    
    createAsteroidMaterial() {
        // Create realistic rock material
        const material = new THREE.MeshPhongMaterial({
            color: this.getRandomRockColor(),
            shininess: 5,
            specular: 0x111111,
            transparent: false,
            side: THREE.FrontSide
        });
        
        // Add normal map for surface detail
        this.addRockTexture(material);
        
        return material;
    }
    
    getRandomRockColor() {
        const rockColors = [
            0x8B4513, // Saddle brown
            0x654321, // Dark brown
            0x2F4F4F, // Dark slate gray
            0x696969, // Dim gray
            0x8B7355, // Dark khaki
            0x556B2F, // Dark olive green
            0x2E8B57, // Sea green
            0x8B0000  // Dark red
        ];
        
        return rockColors[Math.floor(Math.random() * rockColors.length)];
    }
    
    addRockTexture(material) {
        // Create procedural rock texture
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        
        // Base rock color
        ctx.fillStyle = `#${material.color.getHexString()}`;
        ctx.fillRect(0, 0, 256, 256);
        
        // Add rock patterns
        for (let i = 0; i < 50; i++) {
            const x = Math.random() * 256;
            const y = Math.random() * 256;
            const radius = Math.random() * 20 + 5;
            
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
        
        // Create normal map for surface bumps
        this.createRockNormalMap(material);
    }
    
    createRockNormalMap(material) {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        
        // Create normal map
        const imageData = ctx.createImageData(256, 256);
        const data = imageData.data;
        
        for (let i = 0; i < data.length; i += 4) {
            const noise = Math.random();
            data[i] = 128 + noise * 50;     // R
            data[i + 1] = 128 + noise * 50; // G
            data[i + 2] = 255;              // B
            data[i + 3] = 255;              // A
        }
        
        ctx.putImageData(imageData, 0, 0);
        const normalTexture = new THREE.CanvasTexture(canvas);
        material.normalMap = normalTexture;
        material.normalScale = new THREE.Vector2(0.5, 0.5);
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
            
            // Rotate asteroid for visual effect
            asteroid.rotation.x += asteroid.userData.rotationSpeed.x;
            asteroid.rotation.y += asteroid.userData.rotationSpeed.y;
            asteroid.rotation.z += asteroid.userData.rotationSpeed.z;
            
            // Add particle trail effect
            this.updateAsteroidTrail(asteroid);
            
            // Check collision
            if (asteroid.position.length() <= 2.1) {
                this.handleImpact(asteroid, i);
            }
        }
    }
    
    updateAsteroidTrail(asteroid) {
        // Create particle trail
        if (Math.random() < 0.3) { // 30% chance per frame
            const particle = this.createTrailParticle(asteroid.position);
            asteroid.userData.debris.push(particle);
            this.sceneManager.getScene().add(particle);
            
            // Remove old particles
            if (asteroid.userData.debris.length > 20) {
                const oldParticle = asteroid.userData.debris.shift();
                this.sceneManager.getScene().remove(oldParticle);
            }
        }
        
        // Update existing particles
        asteroid.userData.debris.forEach(particle => {
            particle.material.opacity -= 0.02;
            particle.scale.multiplyScalar(0.98);
            
            if (particle.material.opacity <= 0) {
                this.sceneManager.getScene().remove(particle);
                const index = asteroid.userData.debris.indexOf(particle);
                if (index > -1) {
                    asteroid.userData.debris.splice(index, 1);
                }
            }
        });
    }
    
    createTrailParticle(position) {
        const geometry = new THREE.SphereGeometry(0.01, 4, 4);
        const material = new THREE.MeshBasicMaterial({
            color: 0xff6600,
            transparent: true,
            opacity: 0.8
        });
        
        const particle = new THREE.Mesh(geometry, material);
        particle.position.copy(position);
        
        // Add some random velocity
        particle.userData = {
            velocity: new THREE.Vector3(
                (Math.random() - 0.5) * 0.01,
                (Math.random() - 0.5) * 0.01,
                (Math.random() - 0.5) * 0.01
            )
        };
        
        return particle;
    }
    
    handleImpact(asteroid, index) {
        // Create realistic explosion effect
        this.createRealisticExplosion(asteroid.position);
        
        // Create debris field
        this.createDebrisField(asteroid);
        
        // Clean up asteroid debris
        asteroid.userData.debris.forEach(particle => {
            this.sceneManager.getScene().remove(particle);
        });
        
        // Remove asteroid
        this.sceneManager.getScene().remove(asteroid);
        this.asteroids.splice(index, 1);
        
        console.log('💥 Realistic asteroid impact!');
    }
    
    createRealisticExplosion(position) {
        // Main explosion sphere
        const explosionGroup = new THREE.Group();
        
        // Core explosion
        const coreGeometry = new THREE.SphereGeometry(0.1, 16, 12);
        const coreMaterial = new THREE.MeshBasicMaterial({
            color: 0xff4400,
            transparent: true,
            opacity: 0.9
        });
        const core = new THREE.Mesh(coreGeometry, coreMaterial);
        explosionGroup.add(core);
        
        // Outer shockwave
        const shockwaveGeometry = new THREE.SphereGeometry(0.2, 16, 12);
        const shockwaveMaterial = new THREE.MeshBasicMaterial({
            color: 0xffaa00,
            transparent: true,
            opacity: 0.6,
            side: THREE.BackSide
        });
        const shockwave = new THREE.Mesh(shockwaveGeometry, shockwaveMaterial);
        explosionGroup.add(shockwave);
        
        // Fireball
        const fireballGeometry = new THREE.SphereGeometry(0.15, 12, 8);
        const fireballMaterial = new THREE.MeshBasicMaterial({
            color: 0xff0000,
            transparent: true,
            opacity: 0.7
        });
        const fireball = new THREE.Mesh(fireballGeometry, fireballMaterial);
        explosionGroup.add(fireball);
        
        explosionGroup.position.copy(position);
        this.sceneManager.getScene().add(explosionGroup);
        
        // Animate explosion
        this.animateExplosion(explosionGroup);
        
        // Remove after 3 seconds
        setTimeout(() => {
            this.sceneManager.getScene().remove(explosionGroup);
        }, 3000);
    }
    
    animateExplosion(explosionGroup) {
        const startTime = Date.now();
        const duration = 3000;
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = elapsed / duration;
            
            if (progress >= 1) return;
            
            // Scale explosion
            const scale = 1 + progress * 4;
            explosionGroup.scale.setScalar(scale);
            
            // Fade out
            explosionGroup.children.forEach((child, index) => {
                const fadeRate = 1 - progress;
                child.material.opacity = fadeRate * (0.9 - index * 0.1);
            });
            
            requestAnimationFrame(animate);
        };
        animate();
    }
    
    createDebrisField(asteroid) {
        // Create debris particles
        for (let i = 0; i < 30; i++) {
            const debris = this.createDebrisParticle(asteroid.position);
            this.sceneManager.getScene().add(debris);
            
            // Remove debris after 5 seconds
            setTimeout(() => {
                this.sceneManager.getScene().remove(debris);
            }, 5000);
        }
    }
    
    createDebrisParticle(position) {
        const geometry = new THREE.SphereGeometry(0.02, 4, 4);
        const material = new THREE.MeshBasicMaterial({
            color: this.getRandomRockColor(),
            transparent: true,
            opacity: 0.8
        });
        
        const debris = new THREE.Mesh(geometry, material);
        debris.position.copy(position);
        
        // Random velocity for debris
        debris.userData = {
            velocity: new THREE.Vector3(
                (Math.random() - 0.5) * 0.2,
                (Math.random() - 0.5) * 0.2,
                (Math.random() - 0.5) * 0.2
            ),
            rotationSpeed: {
                x: (Math.random() - 0.5) * 0.2,
                y: (Math.random() - 0.5) * 0.2,
                z: (Math.random() - 0.5) * 0.2
            }
        };
        
        // Animate debris
        this.animateDebris(debris);
        
        return debris;
    }
    
    animateDebris(debris) {
        const animate = () => {
            if (!debris.parent) return; // Check if debris still exists
            
            // Update position
            debris.position.add(debris.userData.velocity);
            
            // Rotate debris
            debris.rotation.x += debris.userData.rotationSpeed.x;
            debris.rotation.y += debris.userData.rotationSpeed.y;
            debris.rotation.z += debris.userData.rotationSpeed.z;
            
            // Fade out
            debris.material.opacity -= 0.005;
            
            if (debris.material.opacity <= 0) {
                this.sceneManager.getScene().remove(debris);
                return;
            }
            
            requestAnimationFrame(animate);
        };
        animate();
    }
}

// Initialising the application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.globeApp = new GlobeApp();
});