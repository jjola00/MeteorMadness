/**
 * 
 * Handles orbit controls and basic interactions
 */
class ControlsManager {
    constructor(camera, renderer) {
        this.camera = camera;
        this.renderer = renderer;
        this.controls = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.selectedImpactPoint = null;
        this.impactMarker = null;
        this.isHoveringGlobe = false;
        
        this.init();
    }
    
    init() {
        this.setupOrbitControls();
        this.setupKeyboardControls();
        this.setupMouseControls();
    }
    
    setupOrbitControls() {
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.autoRotate = true;
        this.controls.autoRotateSpeed = 0.5;
        this.controls.enableZoom = true;
        this.controls.minDistance = 3;
        this.controls.maxDistance = 10;
    }
    
    setupKeyboardControls() {
        window.addEventListener('keydown', (event) => {
            switch(event.code) {
                case 'Space':
                    event.preventDefault();
                    this.spawnAsteroidToTarget();
                    break;
                case 'KeyC':
                    event.preventDefault();
                    this.clearAsteroids();
                    break;
            }
        });
    }
    
    setupMouseControls() {
        const canvas = this.renderer.domElement;
        
        // Mouse move for hover detection
        canvas.addEventListener('mousemove', (event) => {
            this.onMouseMove(event);
        });
        
        // Mouse click for target selection
        canvas.addEventListener('click', (event) => {
            this.onMouseClick(event);
        });
        
        // Mouse enter/leave for cursor changes
        canvas.addEventListener('mouseenter', () => {
            this.onMouseEnter();
        });
        
        canvas.addEventListener('mouseleave', () => {
            this.onMouseLeave();
        });
    }
    
    onMouseMove(event) {
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        this.updateCursor();
    }
    
    onMouseClick(event) {
        if (!this.isHoveringGlobe) return;
        
        // Update mouse coordinates
        const rect = this.renderer.domElement.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        // Raycast to find intersection with globe
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const globe = window.globeApp?.globeManager?.globe;
        
        if (globe) {
            // Get all intersections and sort by distance from camera
            const intersects = this.raycaster.intersectObject(globe);
            if (intersects.length > 0) {
                // Sort intersections by distance (closest first)
                intersects.sort((a, b) => a.distance - b.distance);
                
                // Get the closest intersection (front side of globe)
                const intersection = intersects[0];
                this.selectedImpactPoint = intersection.point.clone();
                this.showImpactMarker(this.selectedImpactPoint);
                
                // Enable defense button when target is selected
                if (window.globeApp?.defenseManager) {
                    window.globeApp.defenseManager.enableDefenseButton();
                }
                
                console.log('🎯 Target selected:', this.selectedImpactPoint);
                console.log('📏 Target distance from center:', this.selectedImpactPoint.length());
                console.log('🌍 Earth radius: 2.0');
                console.log('📐 Intersection distance from camera:', intersection.distance);
                console.log('🎯 Face index:', intersection.faceIndex);
                console.log('🔍 Total intersections found:', intersects.length);
                
                // Debug: show all intersection points
                if (intersects.length > 1) {
                    console.log('⚠️ Multiple intersections detected!');
                    intersects.forEach((intersect, index) => {
                        console.log(`  ${index}: distance=${intersect.distance.toFixed(2)}, point=(${intersect.point.x.toFixed(2)}, ${intersect.point.y.toFixed(2)}, ${intersect.point.z.toFixed(2)})`);
                    });
                }
            }
        }
    }
    
    onMouseEnter() {
        this.isHoveringGlobe = true;
        this.updateCursor();
    }
    
    onMouseLeave() {
        this.isHoveringGlobe = false;
        this.updateCursor();
    }
    
    updateCursor() {
        const canvas = this.renderer.domElement;
        if (this.isHoveringGlobe) {
            canvas.style.cursor = 'crosshair';
        } else {
            canvas.style.cursor = 'default';
        }
    }
    
    showImpactMarker(position) {
        // Remove existing marker
        if (this.impactMarker) {
            window.globeApp.sceneManager.getScene().remove(this.impactMarker);
        }
        
        // Create new impact marker - much smaller and more precise
        const markerGeometry = new THREE.SphereGeometry(0.02, 8, 6); // Much smaller for precision
        const markerMaterial = new THREE.MeshBasicMaterial({
            color: 0xff0000,
            transparent: true,
            opacity: 1.0
        });
        
        this.impactMarker = new THREE.Mesh(markerGeometry, markerMaterial);
        this.impactMarker.position.copy(position);
        
        // Scale marker to be slightly above surface for visibility
        const direction = position.clone().normalize();
        this.impactMarker.position.add(direction.multiplyScalar(0.1)); // Closer to surface
        
        window.globeApp.sceneManager.getScene().add(this.impactMarker);
        
        console.log('🎯 Impact marker placed at:', this.impactMarker.position);
        console.log('📏 Marker distance from center:', this.impactMarker.position.length());
        
        // Animate marker
        this.animateImpactMarker();
    }
    
    animateImpactMarker() {
        if (!this.impactMarker) return;
        
        const startTime = Date.now();
        const duration = 2000;
        
        const animate = () => {
            // Check if marker still exists before animating
            if (!this.impactMarker) return;
            
            const elapsed = Date.now() - startTime;
            const progress = elapsed / duration;
            
            if (progress >= 1) {
                // Remove marker after animation
                if (this.impactMarker) {
                    window.globeApp.sceneManager.getScene().remove(this.impactMarker);
                    this.impactMarker = null;
                }
                return;
            }
            
            // Pulsing effect
            const scale = 1 + Math.sin(progress * Math.PI * 4) * 0.3;
            this.impactMarker.scale.setScalar(scale);
            
            // Fade effect
            this.impactMarker.material.opacity = 0.8 * (1 - progress * 0.5);
            
            requestAnimationFrame(animate);
        };
        animate();
    }
    
    spawnAsteroidToTarget() {
        // Check if asteroid is customized first
        const asteroidConfig = this.getCustomAsteroidConfig();
        if (!asteroidConfig) {
            this.showCustomizationWarning();
            return;
        }
        
        // Spawn asteroid to selected target
        if (window.globeApp && window.globeApp.spawnAsteroidToTarget) {
            window.globeApp.spawnAsteroidToTarget(this.selectedImpactPoint);
        }
    }
    
    getCustomAsteroidConfig() {
        // Try to get custom config from localStorage
        const storedConfig = localStorage.getItem('asteroidConfig');
        if (storedConfig) {
            try {
                return JSON.parse(storedConfig);
            } catch (error) {
                console.warn('⚠️ Failed to parse stored asteroid config:', error);
            }
        }
        return null;
    }
    
    showCustomizationWarning() {
        // Create warning message
        const warning = document.createElement('div');
        warning.id = 'customizationWarning';
        warning.innerHTML = `
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(255, 0, 0, 0.9);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                z-index: 1000;
                backdrop-filter: blur(10px);
                border: 2px solid #ff6600;
                box-shadow: 0 4px 20px rgba(255, 0, 0, 0.5);
            ">
                <h3>⚠️ Customize Asteroid First!</h3>
                <p>Please configure your asteroid before launching.</p>
                <a href="asteroid-config.html" style="
                    display: inline-block;
                    margin-top: 10px;
                    padding: 8px 16px;
                    background: #ff6600;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                ">Configure Asteroid</a>
            </div>
        `;
        
        document.body.appendChild(warning);
        
        // Remove warning after 5 seconds
        setTimeout(() => {
            if (warning.parentNode) {
                warning.parentNode.removeChild(warning);
            }
        }, 5000);
    }
    
    clearAsteroids() {
        // Clear asteroids and visual markers
        if (window.globeApp && window.globeApp.clearAsteroids) {
            window.globeApp.clearAsteroids();
        }
        this.clearAllVisuals();
    }
    
    clearAllVisuals() {
        // Clear impact marker
        if (this.impactMarker) {
            window.globeApp.sceneManager.getScene().remove(this.impactMarker);
            this.impactMarker = null;
        }
        this.selectedImpactPoint = null;
    }
    
    update() {
        if (this.controls) {
            this.controls.update();
        }
    }
}