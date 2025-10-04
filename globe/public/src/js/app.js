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
        this.defenseManager = null;
        this.asteroids = [];
        this.isRunning = false;
        
        this.init();
    }
    
    init() {
        this.sceneManager = new SceneManager();
        this.globeManager = new GlobeManager(this.sceneManager.getScene());
        this.lightingManager = new LightingManager(this.sceneManager.getScene());
        this.controlsManager = new ControlsManager(
            this.sceneManager.getCamera(),
            this.sceneManager.getRenderer()
        );
        this.defenseManager = new DefenseManager(
            this.sceneManager.getScene(),
            this.sceneManager.getCamera()
        );
        
        this.start();
    }
    
    start() {
        this.isRunning = true;
        this.animate();
        this.loadAsteroidInfoOnStartup();
        console.log('🌍 Simple Three.js Globe loaded successfully!');
    }
    
    loadAsteroidInfoOnStartup() {
        const asteroidConfig = this.getCustomAsteroidConfig();
        if (asteroidConfig) {
            this.updateAsteroidInfoDisplay(asteroidConfig);
        } else {
            this.showNoAsteroidConfiguredMessage();
        }
    }
    
    showNoAsteroidConfiguredMessage() {
        const nameElement = document.getElementById('asteroidName');
        const diameterElement = document.getElementById('asteroidDiameter');
        const speedElement = document.getElementById('asteroidSpeed');
        
        if (nameElement) nameElement.textContent = 'None configured';
        if (diameterElement) diameterElement.textContent = '-';
        if (speedElement) speedElement.textContent = '-';
        
        const infoPanel = document.getElementById('asteroidInfo');
        if (infoPanel) {
            infoPanel.style.display = 'block';
            
            const configurePrompt = document.createElement('div');
            configurePrompt.id = 'configurePrompt';
            configurePrompt.innerHTML = `
                <div style="
                    margin-top: 10px;
                    padding: 8px;
                    background: rgba(255, 102, 0, 0.2);
                    border: 1px solid rgba(255, 102, 0, 0.5);
                    border-radius: 5px;
                    text-align: center;
                ">
                    <p style="margin: 0; font-size: 0.8em; color: #ff6600;">
                        ⚙️ <a href="asteroid-config.html" style="color: #ff6600; text-decoration: none; font-weight: bold;">Configure Asteroid</a>
                    </p>
                </div>
            `;
            infoPanel.appendChild(configurePrompt);
        }
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
        
        // Update defense system
        this.defenseManager.update();
        
        // Render the scene
        this.sceneManager.render();
    }
    
    spawnAsteroidToTarget(targetPoint) {
        if (!targetPoint) {
            console.log('⚠️ No target point selected! Click on the globe first.');
            return;
        }
        
        // Clear existing asteroids first
        this.clearAsteroids();
        
        // Get custom asteroid configuration from localStorage
        const asteroidConfig = this.getCustomAsteroidConfig();
        
        // Create asteroid with custom configuration
        const asteroid = this.createCustomAsteroid(asteroidConfig);
        
        // Spawn position: Place asteroid behind camera, away from target
        const spawnDistance = 15; // Distance from Earth center
        
        // Calculate direction from camera to target point
        const cameraToTarget = new THREE.Vector3().subVectors(targetPoint, this.sceneManager.getCamera().position).normalize();
        
        // Spawn asteroid behind the camera, in the direction away from target
        asteroid.position.copy(this.sceneManager.getCamera().position.clone().add(cameraToTarget.multiplyScalar(-spawnDistance)));
        
        // Calculate velocity directly toward target point
        const direction = new THREE.Vector3().subVectors(targetPoint, asteroid.position).normalize();
        
        // Verify trajectory accuracy
        const trajectoryCheck = asteroid.position.clone().add(direction.clone().multiplyScalar(20));
        const trajectoryDistanceFromCenter = trajectoryCheck.length();
        console.log('🎯 Trajectory verification:');
        console.log('  📍 Spawn:', asteroid.position);
        console.log('  📍 Target:', targetPoint);
        console.log('  📐 Direction:', direction);
        console.log('  🔍 20 units ahead:', trajectoryCheck);
        console.log('  📏 Trajectory distance from center:', trajectoryDistanceFromCenter);
        
        // Calculate expected impact point
        const expectedImpactPoint = this.calculateExpectedImpactPoint(asteroid.position, direction, targetPoint);
        console.log('🎯 Expected impact point:', expectedImpactPoint);
        console.log('📏 Distance from target:', expectedImpactPoint.distanceTo(targetPoint));
        
        // No randomness - perfect targeting
        
        // Use custom speed from configuration
        const speed = asteroidConfig.speed * 0.01; // Convert km/s to scene units
        
        asteroid.userData = {
            velocity: direction.multiplyScalar(speed),
            rotationSpeed: {
                x: (Math.random() - 0.5) * 0.1,
                y: (Math.random() - 0.5) * 0.1,
                z: (Math.random() - 0.5) * 0.1
            },
            scale: asteroidConfig.diameter / 1000, // Convert meters to scene units
            debris: [], // For particle effects
            name: asteroidConfig.name,
            targetPoint: targetPoint.clone() // Store target for debugging
        };
        
        // Apply custom scale
        asteroid.scale.setScalar(asteroid.userData.scale);
        
        this.sceneManager.getScene().add(asteroid);
        this.asteroids.push(asteroid);
        
        // Launch defense spacecraft if defense is enabled
        if (this.defenseManager.isDefenseActive()) {
            const defenseLaunched = this.defenseManager.launchSpacecraft(asteroid, targetPoint);
            if (defenseLaunched) {
                console.log('🛡️ DART defense spacecraft launched!');
            }
        }
        
        // Update asteroid info display
        this.updateAsteroidInfoDisplay(asteroidConfig);
        
        console.log(`☄️ Custom asteroid "${asteroidConfig.name}" launched toward target!`);
        console.log('🎯 Target point:', targetPoint);
        console.log('📏 Target distance from center:', targetPoint.length());
        console.log('🚀 Spawn position:', asteroid.position);
        console.log('📏 Spawn distance from center:', asteroid.position.length());
        console.log('📐 Direction vector:', direction);
        console.log('🌍 Earth radius: 2.0, Collision at: 2.1');
    }
    
    getCustomAsteroidConfig() {
        // Try to get custom config from localStorage
        const storedConfig = localStorage.getItem('asteroidConfig');
        if (storedConfig) {
            try {
                const config = JSON.parse(storedConfig);
                console.log('🎯 Using custom asteroid config:', config);
                return config;
            } catch (error) {
                console.warn('⚠️ Failed to parse stored asteroid config:', error);
            }
        }
        
        // Default configuration if none stored
        return {
            name: 'Default Asteroid',
            diameter: 500,
            speed: 20
        };
    }
    
    createCustomAsteroid(config) {
        // Create asteroid with custom configuration
        const asteroid = this.createRealisticAsteroid();
        
        // Apply custom name (for logging/debugging)
        asteroid.userData.name = config.name;
        
        return asteroid;
    }
    
    updateAsteroidInfoDisplay(config) {
        // Update the asteroid info panel
        const nameElement = document.getElementById('asteroidName');
        const diameterElement = document.getElementById('asteroidDiameter');
        const speedElement = document.getElementById('asteroidSpeed');
        
        if (nameElement) nameElement.textContent = config.name;
        if (diameterElement) diameterElement.textContent = `${config.diameter}m`;
        if (speedElement) speedElement.textContent = `${config.speed} km/s`;
        
        // Show the info panel
        const infoPanel = document.getElementById('asteroidInfo');
        if (infoPanel) {
            infoPanel.style.display = 'block';
            
            // Remove configure prompt if it exists
            const configurePrompt = document.getElementById('configurePrompt');
            if (configurePrompt) {
                configurePrompt.remove();
            }
        }
    }
    
    calculateExpectedImpactPoint(spawnPosition, direction, targetPoint) {
        // Calculate where the asteroid will intersect with the Earth surface
        // Earth center is at (0,0,0) with radius 2
        
        // Ray-sphere intersection: ray from spawnPosition in direction
        // Sphere: center (0,0,0), radius 2
        
        const a = direction.dot(direction); // Should be 1 since direction is normalized
        const b = 2 * spawnPosition.dot(direction);
        const c = spawnPosition.dot(spawnPosition) - 4; // 4 = radius^2
        
        const discriminant = b * b - 4 * a * c;
        
        if (discriminant >= 0) {
            const t1 = (-b + Math.sqrt(discriminant)) / (2 * a);
            const t2 = (-b - Math.sqrt(discriminant)) / (2 * a);
            
            // Use the smaller positive t (closer intersection)
            const t = Math.min(t1, t2);
            if (t > 0) {
                return spawnPosition.clone().add(direction.clone().multiplyScalar(t));
            }
        }
        
        // Fallback: return target point
        return targetPoint.clone();
    }
    
    createRealisticAsteroid() {
        // Create irregular rock-like geometry
        const geometry = this.createAsteroidGeometry();
        const material = this.createAsteroidMaterial();
        
        const asteroid = new THREE.Mesh(geometry, material);
        
        // Add some random rotation offset
        asteroid.rotation.set(
            Math.random() * Math.PI * 2,
            Math.random() * Math.PI * 2,
            Math.random() * Math.PI * 2
        );
        
        return asteroid;
    }
    
    createAsteroidGeometry() {
        // Start with a sphere for simple shape
        const geometry = new THREE.SphereGeometry(0.15, 32, 32);
        
        // Add simple bumps to the surface
        this.addAsteroidBumps(geometry);
        
        // Recalculate normals for proper lighting
        geometry.computeVertexNormals();
        
        return geometry;
    }
    
    addAsteroidBumps(geometry) {
        const positions = geometry.attributes.position.array;
        
        // Add simple bumps by pushing vertices outward
        for (let i = 0; i < positions.length; i += 3) {
            // Add small random bumps
            const bumpStrength = 0.02 + Math.random() * 0.03; // Random bump size
            
            // Get the normal direction (from center to vertex)
            const normal = new THREE.Vector3(positions[i], positions[i + 1], positions[i + 2]).normalize();
            
            // Push vertex outward along normal
            positions[i] += normal.x * bumpStrength;
            positions[i + 1] += normal.y * bumpStrength;
            positions[i + 2] += normal.z * bumpStrength;
        }
        
        geometry.attributes.position.needsUpdate = true;
    }
    
    createAsteroidMaterial() {
        // Create simple dark grey material
        const material = new THREE.MeshPhongMaterial({
            color: 0x333333, 
            shininess: 10,
            specular: 0x222222,
            transparent: false,
            side: THREE.FrontSide
        });
        
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
            
            // Apply gravity toward Earth center
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
            
            // Check collision with Earth surface
            const distanceFromCenter = asteroid.position.length();
            if (distanceFromCenter <= 4) {
                // Check if asteroid was deflected by defense system
                if (asteroid.userData.wasDeflected) {
                    console.log('🛡️ Asteroid was successfully deflected! Moving away from Earth.');
                    // Continue with deflected trajectory - don't trigger impact
                    return;
                }
                
                // Ensure impact happens exactly at target point
                const targetPoint = asteroid.userData.targetPoint;
                if (targetPoint) {
                    // Check if we're already animating to target
                    if (!asteroid.userData.isAnimatingToTarget) {
                        console.log('🎬 Starting animation at distance:', distanceFromCenter);
                        // Start smooth movement animation to target
                        asteroid.userData.isAnimatingToTarget = true;
                        asteroid.userData.animationStartTime = Date.now();
                        asteroid.userData.animationDuration = 5000; // 5 seconds
                        asteroid.userData.startPosition = asteroid.position.clone();
                        asteroid.userData.targetPosition = targetPoint.clone();
                        
                    } else {
                        // Continue smooth animation
                        const elapsed = Date.now() - asteroid.userData.animationStartTime;
                        const progress = Math.min(elapsed / asteroid.userData.animationDuration, 1);
                        
                        // Debug progress every 20% to see if animation is working
                        if (Math.floor(progress * 5) !== Math.floor((progress - 0.001) * 5)) {
                            console.log(`🎬 Animation progress: ${Math.floor(progress * 100)}%`);
                        }
                        
                        
                        // Use easing function for smooth movement
                        const easedProgress = this.easeInOutCubic(progress);
                        
                        // Interpolate position
                        asteroid.position.lerpVectors(
                            asteroid.userData.startPosition,
                            asteroid.userData.targetPosition,
                            easedProgress
                        );
                        
                        // Check if animation is complete (use >= 0.8 since it gets stuck at 80%)
                        if (progress >= 0.8) {
                            console.log('🎬 Animation complete - calling handleImpact');
                            this.handleImpact(asteroid, i);
                        }
                    }
                } else {
                    // Fallback to instant impact if no target
                    console.log('💥 Impact detected!');
                    console.log('📍 Impact position:', asteroid.position);
                    console.log('📏 Distance from center:', asteroid.position.length());
                    this.handleImpact(asteroid, i);
                }
            }
        }
    }
    
    easeInOutCubic(t) {
        // Smooth easing function for natural movement
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
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
        console.log('🔥 IMPACT TRIGGERED!');
        // Show impact marker circle (the original impact circle)
        if (this.controlsManager && this.controlsManager.showImpactMarker) {
            console.log('🎯 Calling showImpactMarker');
            this.controlsManager.showImpactMarker(asteroid.position);
        } else {
            console.log('❌ controlsManager or showImpactMarker not available');
        }
        
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
        
        // Core explosion - smaller and more appropriate
        const coreGeometry = new THREE.SphereGeometry(0.1, 16, 12);
        const coreMaterial = new THREE.MeshBasicMaterial({
            color: 0xff4400,
            transparent: true,
            opacity: 0.9
        });
        const core = new THREE.Mesh(coreGeometry, coreMaterial);
        explosionGroup.add(core);
        
        // Outer shockwave - smaller
        const shockwaveGeometry = new THREE.SphereGeometry(0.15, 16, 12);
        const shockwaveMaterial = new THREE.MeshBasicMaterial({
            color: 0xffaa00,
            transparent: true,
            opacity: 0.6,
            side: THREE.BackSide
        });
        const shockwave = new THREE.Mesh(shockwaveGeometry, shockwaveMaterial);
        explosionGroup.add(shockwave);
        
        // Fireball - smaller
        const fireballGeometry = new THREE.SphereGeometry(0.12, 12, 8);
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
        
        // Remove after 5 seconds
        setTimeout(() => {
            this.sceneManager.getScene().remove(explosionGroup);
        }, 5000);
    }
    
    animateExplosion(explosionGroup) {
        const startTime = Date.now();
        const duration = 5000; // Match the removal timeout
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = elapsed / duration;
            
            if (progress >= 1) return;
            
            // Scale explosion moderately
            const scale = 1 + progress * 3; // Scale up to 4x original size
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