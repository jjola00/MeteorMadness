/**
 * DefenseManager - Handles DART spacecraft defense system
 * Manages spacecraft creation, animation, and asteroid deflection
 */
class DefenseManager {
    constructor(scene, camera) {
        this.scene = scene;
        this.camera = camera;
        this.spacecraft = null;
        this.isDefenseEnabled = false;
        this.defenseButton = null;
        this.statusText = null;
        
        this.init();
    }
    
    init() {
        this.setupUI();
        this.setupEventListeners();
        console.log('🛡️ Defense Manager initialized');
    }
    
    setupUI() {
        this.defenseButton = document.getElementById('defenseButton');
        this.statusText = document.getElementById('defenseStatusText');
        
        if (!this.defenseButton || !this.statusText) {
            console.warn('⚠️ Defense UI elements not found');
            return;
        }
        
        this.updateUI();
    }
    
    setupEventListeners() {
        if (this.defenseButton) {
            this.defenseButton.addEventListener('click', () => {
                this.toggleDefense();
            });
        }
    }
    
    toggleDefense() {
        this.isDefenseEnabled = !this.isDefenseEnabled;
        this.updateUI();
        
        console.log(`🛡️ Defense ${this.isDefenseEnabled ? 'enabled' : 'disabled'}`);
        
        // If defense is enabled and there are asteroids in flight, launch spacecraft immediately
        if (this.isDefenseEnabled && window.globeApp && window.globeApp.asteroids.length > 0) {
            this.launchDefenseForExistingAsteroids();
        }
    }
    
    launchDefenseForExistingAsteroids() {
        // Find the first asteroid that hasn't been deflected yet
        const activeAsteroid = window.globeApp.asteroids.find(asteroid => !asteroid.userData.wasDeflected);
        
        if (activeAsteroid && window.globeApp.controlsManager.selectedImpactPoint) {
            console.log('🚀 Defense enabled - launching spacecraft for existing asteroid');
            const defenseLaunched = this.launchSpacecraft(activeAsteroid, window.globeApp.controlsManager.selectedImpactPoint);
            if (defenseLaunched) {
                console.log('🛡️ DART defense spacecraft launched for existing asteroid!');
            }
        } else if (activeAsteroid) {
            console.log('⚠️ No target point selected - cannot launch defense for existing asteroid');
        } else {
            console.log('ℹ️ No active asteroids found to defend');
        }
    }
    
    updateUI() {
        if (!this.defenseButton || !this.statusText) return;
        
        if (this.isDefenseEnabled) {
            this.defenseButton.textContent = '🛡️ Disable DART Defense';
            this.defenseButton.classList.add('enabled');
            this.statusText.textContent = 'Enabled';
            this.statusText.classList.add('enabled');
        } else {
            this.defenseButton.textContent = '🛡️ Enable DART Defense';
            this.defenseButton.classList.remove('enabled');
            this.statusText.textContent = 'Disabled';
            this.statusText.classList.remove('enabled');
        }
    }
    
    enableDefenseButton() {
        if (this.defenseButton) {
            this.defenseButton.disabled = false;
        }
        
        // If defense is already enabled and there are asteroids, launch defense immediately
        if (this.isDefenseEnabled && window.globeApp && window.globeApp.asteroids.length > 0) {
            this.launchDefenseForExistingAsteroids();
        }
    }
    
    disableDefenseButton() {
        if (this.defenseButton) {
            this.defenseButton.disabled = true;
        }
    }
    
    isDefenseActive() {
        return this.isDefenseEnabled;
    }
    
    launchSpacecraft(asteroid, targetPoint) {
        if (!this.isDefenseEnabled) {
            console.log('🛡️ Defense not enabled, skipping spacecraft launch');
            return false;
        }
        
        // Remove any existing spacecraft first
        if (this.spacecraft) {
            this.removeSpacecraft();
        }
        
        console.log('🚀 Launching DART spacecraft to intercept asteroid');
        
        // Create spacecraft
        this.spacecraft = this.createSpacecraft();
        
        // Calculate launch position - launch from Earth surface closest to asteroid
        const earthRadius = 2.0;
        const launchDistance = earthRadius + 0.5; // Launch from just above Earth surface
        
        // Calculate direction from Earth center to asteroid
        const earthCenter = new THREE.Vector3(0, 0, 0);
        const asteroidDirection = asteroid.position.clone().normalize();
        
        // Launch spacecraft from Earth surface in the direction of the asteroid
        const launchPosition = asteroidDirection.clone().multiplyScalar(launchDistance);
        
        console.log('🚀 Launch position calculated:', launchPosition);
        console.log('☄️ Asteroid position:', asteroid.position);
        console.log('🎯 Target point:', targetPoint);
        console.log('📏 Distance from asteroid to launch:', launchPosition.distanceTo(asteroid.position).toFixed(2));
        
        // Calculate intercept trajectory
        const interceptPoint = this.calculateInterceptPoint(asteroid, launchPosition);
        
        if (!interceptPoint) {
            console.warn('⚠️ Could not calculate intercept point');
            this.scene.remove(this.spacecraft);
            this.spacecraft = null;
            return false;
        }
        
        // Position spacecraft at launch point
        this.spacecraft.position.copy(launchPosition);
        
        // Set up spacecraft animation to intercept point
        this.animateSpacecraftToIntercept(interceptPoint, asteroid);
        
        this.scene.add(this.spacecraft);
        return true;
    }
    
    createSpacecraft() {
        // Create spacecraft geometry (simplified DART-like shape)
        const spacecraftGroup = new THREE.Group();
        
        // Main body - make it larger for easier collision detection
        const bodyGeometry = new THREE.CylinderGeometry(0.05, 0.06, 0.15, 8);
        const bodyMaterial = new THREE.MeshPhongMaterial({
            color: 0xcccccc,
            shininess: 50,
            specular: 0x444444
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        spacecraftGroup.add(body);
        
        // Solar panels
        const panelGeometry = new THREE.BoxGeometry(0.15, 0.05, 0.01);
        const panelMaterial = new THREE.MeshPhongMaterial({
            color: 0x0000ff,
            shininess: 30
        });
        
        const leftPanel = new THREE.Mesh(panelGeometry, panelMaterial);
        leftPanel.position.set(-0.08, 0, 0);
        spacecraftGroup.add(leftPanel);
        
        const rightPanel = new THREE.Mesh(panelGeometry, panelMaterial);
        rightPanel.position.set(0.08, 0, 0);
        spacecraftGroup.add(rightPanel);
        
        // Add some detail
        const noseGeometry = new THREE.ConeGeometry(0.01, 0.05, 6);
        const noseMaterial = new THREE.MeshPhongMaterial({
            color: 0xff6600,
            shininess: 80
        });
        const nose = new THREE.Mesh(noseGeometry, noseMaterial);
        nose.position.set(0, 0.075, 0);
        nose.rotation.x = Math.PI;
        spacecraftGroup.add(nose);
        
        // Add thruster glow effect
        const thrusterGeometry = new THREE.SphereGeometry(0.015, 8, 8);
        const thrusterMaterial = new THREE.MeshBasicMaterial({
            color: 0xff4400,
            transparent: true,
            opacity: 0.8
        });
        const thruster = new THREE.Mesh(thrusterGeometry, thrusterMaterial);
        thruster.position.set(0, -0.06, 0);
        spacecraftGroup.add(thruster);
        
        // Store reference for animation
        spacecraftGroup.userData = {
            thruster: thruster,
            originalThrusterOpacity: 0.8
        };
        
        return spacecraftGroup;
    }
    
    calculateInterceptPoint(asteroid, launchPosition) {
        // More aggressive intercept calculation
        const asteroidPosition = asteroid.position.clone();
        const asteroidVelocity = asteroid.userData.velocity.clone();
        
        // Calculate multiple intercept points along asteroid's path
        const spacecraftSpeed = 0.4; // Faster spacecraft
        
        // Try different intercept times
        for (let timeOffset = 5; timeOffset <= 30; timeOffset += 5) {
            const interceptPoint = asteroidPosition.clone().add(asteroidVelocity.clone().multiplyScalar(timeOffset));
            const distanceFromLaunch = launchPosition.distanceTo(interceptPoint);
            const timeToReach = distanceFromLaunch / spacecraftSpeed;
            
            // Check if we can reach this point in time
            if (timeToReach <= timeOffset + 5) { // Allow some buffer
                console.log(`🎯 Intercept found: time ${timeOffset}, distance ${distanceFromLaunch.toFixed(2)}`);
                return interceptPoint;
            }
        }
        
        // Fallback: aim directly at asteroid
        console.log(`🎯 Fallback: aiming directly at asteroid`);
        return asteroidPosition.clone();
    }
    
    animateSpacecraftToIntercept(interceptPoint, asteroid) {
        const startPosition = this.spacecraft.position.clone();
        const startTime = Date.now();
        
        // Calculate dynamic duration based on distance - make it much faster
        const distance = startPosition.distanceTo(interceptPoint);
        const baseDuration = 1000; // Much faster base duration (1 second)
        const distanceFactor = Math.min(distance / 10, 1.5); // Scale up to 1.5x for longer distances
        const duration = baseDuration + (distanceFactor * 300); // Add up to 0.5 seconds for long distances
        
        console.log(`🚀 Spacecraft animation: distance ${distance.toFixed(2)}, duration ${duration}ms`);
        
        const animate = () => {
            if (!this.spacecraft || !this.spacecraft.parent) return;
            
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Smooth easing
            const easedProgress = this.easeInOutCubic(progress);
            
            // Interpolate position
            this.spacecraft.position.lerpVectors(startPosition, interceptPoint, easedProgress);
            
            // Rotate spacecraft to face direction of travel
            const direction = new THREE.Vector3().subVectors(interceptPoint, startPosition).normalize();
            this.spacecraft.lookAt(this.spacecraft.position.clone().add(direction));
            
            // Animate thruster glow
            if (this.spacecraft.userData.thruster) {
                const thruster = this.spacecraft.userData.thruster;
                const pulse = Math.sin(elapsed * 0.01) * 0.3 + 0.7;
                thruster.material.opacity = this.spacecraft.userData.originalThrusterOpacity * pulse;
            }
            
            // Check for collision with asteroid during flight - more aggressive detection
            const distanceToAsteroid = this.spacecraft.position.distanceTo(asteroid.position);
            
            // Debug: Log distance every few frames
            if (Math.floor(elapsed / 100) % 5 === 0) {
                console.log(`🚀 Animation collision check: ${distanceToAsteroid.toFixed(3)} (threshold: 0.7)`);
            }
            
            if (distanceToAsteroid < 0.7) { // Even larger collision threshold
                console.log('💥 DART spacecraft collision detected! Distance:', distanceToAsteroid.toFixed(3));
                console.log('🚀 Spacecraft pos:', this.spacecraft.position);
                console.log('☄️ Asteroid pos:', asteroid.position);
                this.triggerDeflection(asteroid);
                this.removeSpacecraft();
                return;
            }
            
            // Additional fallback: if spacecraft is very close to asteroid's path, force collision
            const asteroidToSpacecraft = new THREE.Vector3().subVectors(this.spacecraft.position, asteroid.position);
            const asteroidVelocity = asteroid.userData.velocity.clone().normalize();
            const projectionLength = asteroidToSpacecraft.dot(asteroidVelocity);
            const closestPoint = asteroid.position.clone().add(asteroidVelocity.multiplyScalar(projectionLength));
            const distanceToPath = this.spacecraft.position.distanceTo(closestPoint);
            
            if (distanceToPath < 0.5) {
                console.log('🎯 Spacecraft very close to asteroid path - forcing collision!');
                this.triggerDeflection(asteroid);
                this.removeSpacecraft();
                return;
            }
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                // Fallback: if we reach the intercept point without collision, trigger deflection anyway
                console.log('🎯 Reached intercept point - triggering deflection');
                this.triggerDeflection(asteroid);
                this.removeSpacecraft();
            }
        };
        
        animate();
    }
    
    triggerDeflection(asteroid) {
        console.log('💥 DART impact! Deflecting asteroid...');
        
        // Mark asteroid as deflected
        asteroid.userData.wasDeflected = true;
        
        // Calculate deflection vector (away from Earth)
        const earthCenter = new THREE.Vector3(0, 0, 0);
        const asteroidToEarth = new THREE.Vector3().subVectors(earthCenter, asteroid.position).normalize();
        
        // Create a more dramatic deflection - asteroid flies away at an angle
        const deflectionStrength = 0.08; // Stronger deflection
        const deflectionVector = asteroidToEarth.clone().multiplyScalar(deflectionStrength);
        
        // Add perpendicular component to make it fly away at an angle
        const perpendicular = new THREE.Vector3(
            asteroidToEarth.y - asteroidToEarth.z,
            asteroidToEarth.z - asteroidToEarth.x,
            asteroidToEarth.x - asteroidToEarth.y
        ).normalize();
        
        // Combine radial and perpendicular deflection
        const perpendicularStrength = 0.06;
        deflectionVector.add(perpendicular.multiplyScalar(perpendicularStrength));
        
        // Apply deflection to asteroid velocity
        asteroid.userData.velocity.add(deflectionVector);
        
        // Start deflection animation
        this.animateDeflectedAsteroid(asteroid);
        
        // Create impact effect
        this.createImpactEffect(asteroid.position);
        
        // Show success message
        this.showDeflectionSuccess();
        
        console.log('🛡️ Asteroid deflected away from Earth!');
    }
    
    animateDeflectedAsteroid(asteroid) {
        const startTime = Date.now();
        const duration = 8000; // 8 seconds of deflection animation
        
        // Store original rotation speeds
        const originalRotationSpeed = {
            x: asteroid.userData.rotationSpeed.x,
            y: asteroid.userData.rotationSpeed.y,
            z: asteroid.userData.rotationSpeed.z
        };
        
        // Increase rotation speed for dramatic effect
        asteroid.userData.rotationSpeed.x *= 3;
        asteroid.userData.rotationSpeed.y *= 3;
        asteroid.userData.rotationSpeed.z *= 3;
        
        const animate = () => {
            if (!asteroid.parent) return; // Check if asteroid still exists
            
            const elapsed = Date.now() - startTime;
            const progress = elapsed / duration;
            
            if (progress >= 1) {
                // Animation complete - restore original rotation and fade out
                asteroid.userData.rotationSpeed = originalRotationSpeed;
                this.fadeOutDeflectedAsteroid(asteroid);
                return;
            }
            
            // Gradually increase deflection velocity over time
            const velocityIncrease = 1 + (progress * 0.5); // Increase by 50% over time
            asteroid.userData.velocity.multiplyScalar(velocityIncrease);
            
            // Add some wobble to make it look more realistic
            const wobbleStrength = 0.01 * Math.sin(elapsed * 0.005);
            const wobbleVector = new THREE.Vector3(
                (Math.random() - 0.5) * wobbleStrength,
                (Math.random() - 0.5) * wobbleStrength,
                (Math.random() - 0.5) * wobbleStrength
            );
            asteroid.userData.velocity.add(wobbleVector);
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    fadeOutDeflectedAsteroid(asteroid) {
        const startTime = Date.now();
        const fadeDuration = 3000; // 3 seconds to fade out
        
        const animate = () => {
            if (!asteroid.parent) return;
            
            const elapsed = Date.now() - startTime;
            const progress = elapsed / fadeDuration;
            
            if (progress >= 1) {
                // Remove asteroid from scene
                asteroid.parent.remove(asteroid);
                console.log('🌌 Deflected asteroid has left the scene');
                return;
            }
            
            // Fade out material
            if (asteroid.material) {
                asteroid.material.opacity = 1 - progress;
                asteroid.material.transparent = true;
            }
            
            // Scale down slightly
            const scale = 1 - (progress * 0.3);
            asteroid.scale.setScalar(scale);
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }
    
    showDeflectionSuccess() {
        // Create success message overlay
        const successDiv = document.createElement('div');
        successDiv.id = 'deflectionSuccess';
        successDiv.innerHTML = `
            <div style="
                position: fixed;
                top: 25%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: linear-gradient(135deg, #00cc66, #009944);
                color: white;
                padding: 20px 30px;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
                text-align: center;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
                z-index: 1000;
                border: 2px solid #00ff88;
                animation: successPulse 0.5s ease-out;
            ">
                🛡️ DART MISSION SUCCESS! 🛡️<br>
                <span style="font-size: 14px; opacity: 0.9;">Asteroid successfully deflected away from Earth</span>
            </div>
        `;
        
        // Add CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes successPulse {
                0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0; }
                50% { transform: translate(-50%, -50%) scale(1.1); opacity: 1; }
                100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(successDiv);
        
        // Remove message after 4 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
            if (style.parentNode) {
                style.parentNode.removeChild(style);
            }
        }, 4000);
    }
    
    createImpactEffect(position) {
        // Create impact explosion
        const explosionGroup = new THREE.Group();
        
        // Core explosion
        const coreGeometry = new THREE.SphereGeometry(0.05, 16, 12);
        const coreMaterial = new THREE.MeshBasicMaterial({
            color: 0xff8800,
            transparent: true,
            opacity: 0.9
        });
        const core = new THREE.Mesh(coreGeometry, coreMaterial);
        explosionGroup.add(core);
        
        // Shockwave
        const shockwaveGeometry = new THREE.SphereGeometry(0.08, 16, 12);
        const shockwaveMaterial = new THREE.MeshBasicMaterial({
            color: 0xffaa00,
            transparent: true,
            opacity: 0.6,
            side: THREE.BackSide
        });
        const shockwave = new THREE.Mesh(shockwaveGeometry, shockwaveMaterial);
        explosionGroup.add(shockwave);
        
        explosionGroup.position.copy(position);
        this.scene.add(explosionGroup);
        
        // Animate explosion
        this.animateDeflectionExplosion(explosionGroup);
        
        // Remove after 3 seconds
        setTimeout(() => {
            this.scene.remove(explosionGroup);
        }, 3000);
    }
    
    animateDeflectionExplosion(explosionGroup) {
        const startTime = Date.now();
        const duration = 3000;
        
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = elapsed / duration;
            
            if (progress >= 1) return;
            
            // Scale explosion
            const scale = 1 + progress * 2;
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
    
    removeSpacecraft() {
        if (this.spacecraft) {
            this.scene.remove(this.spacecraft);
            this.spacecraft = null;
            console.log('🚀 DART spacecraft mission complete');
        }
    }
    
    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }
    
    update() {
        // Update spacecraft if it exists
        if (this.spacecraft && this.spacecraft.parent) {
            // Check for collision with any asteroid in the scene
            if (window.globeApp && window.globeApp.asteroids) {
                for (let asteroid of window.globeApp.asteroids) {
                    if (!asteroid.userData.wasDeflected) {
                        const distance = this.spacecraft.position.distanceTo(asteroid.position);
                        
                        // Debug: Log distance every 30 frames to see what's happening
                        if (Math.floor(Date.now() / 100) % 3 === 0) {
                            console.log(`🔍 Distance check: ${distance.toFixed(3)} (threshold: 0.8)`);
                        }
                        
                        if (distance < 0.8) { // Increased collision threshold
                            console.log('💥 Global collision detection triggered! Distance:', distance.toFixed(3));
                            console.log('🚀 Spacecraft position:', this.spacecraft.position);
                            console.log('☄️ Asteroid position:', asteroid.position);
                            console.log('☄️ Asteroid velocity:', asteroid.userData.velocity);
                            
                            // Trigger deflection
                            this.triggerDeflection(asteroid);
                            this.removeSpacecraft();
                            break; // Only deflect one asteroid
                        }
                    }
                }
            }
        }
    }
    
    cleanup() {
        this.removeSpacecraft();
        this.isDefenseEnabled = false;
        this.updateUI();
    }
}
