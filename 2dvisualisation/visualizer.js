// Main visualizer logic for asteroid impact simulation

import { impactScenarios } from './scenarios.js';
import { TimelineController } from './timeline.js';

export class ImpactVisualizer {
    constructor() {
        this.map = null;
        this.layerGroups = {
            blast: L.layerGroup(),
            seismic: L.layerGroup(),
            thermal: L.layerGroup(),
            population: L.layerGroup(),
            crater: L.layerGroup()
        };
        this.currentScenario = 'tunguska';
        this.timeline = new TimelineController();
    }

    initialize() {
        this.initMap();
        this.timeline.initialize();
        this.timeline.onTimeChange(() => this.updateVisualization());
        
        setTimeout(() => {
            this.loadScenario('tunguska');
        }, 100);
    }

    initMap() {
        this.map = L.map('map').setView([60.8858, 101.8944], 6);

        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);

        Object.values(this.layerGroups).forEach(layerGroup => {
            layerGroup.addTo(this.map);
        });
    }

    loadScenario(scenarioId) {
        const scenario = impactScenarios[scenarioId];
        if (!scenario) return;

        this.currentScenario = scenarioId;

        // Update scenario info
        document.getElementById('event-name').textContent = scenario.name;
        document.getElementById('event-energy').textContent = scenario.energy;
        document.getElementById('event-casualties').textContent = scenario.casualties;
        document.getElementById('event-crater').textContent = scenario.crater;

        // Center map on impact location
        this.map.setView(scenario.location, scenarioId === 'chicxulub' ? 4 : 8);

        // Update timeline
        this.timeline.setDuration(scenario.duration);
        this.timeline.updateMarkers(scenario);

        // Render visualization
        this.updateVisualization();
    }

    updateVisualization() {
        const scenario = impactScenarios[this.currentScenario];
        if (!scenario) return;

        if (this.timeline.currentTime === 0 || !scenario.temporalEffects) {
            this.renderStaticVisualization(scenario.impactData);
            this.updateRealtimeData(this.getStaticData());
        } else {
            const interpolatedData = this.interpolateTemporalData(this.timeline.currentTime, scenario);
            this.renderTemporalVisualization(scenario, interpolatedData);
            this.updateRealtimeData(interpolatedData);
        }
    }

    renderStaticVisualization(impactData) {
        this.clearLayers();

        if (impactData.blast) {
            this.renderBlastZones(impactData.blast);
        }
        if (impactData.seismic) {
            this.renderSeismicZones(impactData.seismic);
        }
        if (impactData.thermal) {
            this.renderThermalZones(impactData.thermal);
        }
        if (impactData.population) {
            this.renderPopulationDensity(impactData.population);
        }
        if (impactData.crater) {
            this.renderCrater(impactData.crater);
        }

        if (Array.isArray(impactData.blast) && impactData.blast.length > 0 && impactData.blast[0]?.center) {
            this.addImpactMarker(impactData.blast[0].center);
        }
    }

    renderTemporalVisualization(scenario, temporalData) {
        this.clearLayers();

        if (temporalData.blastRadius > 0) {
            const blastZones = [
                { center: scenario.location, radius: temporalData.blastRadius * 1000 * 0.5, intensity: 1.0, description: "Total destruction" },
                { center: scenario.location, radius: temporalData.blastRadius * 1000 * 0.8, intensity: 0.7, description: "Severe damage" },
                { center: scenario.location, radius: temporalData.blastRadius * 1000, intensity: 0.4, description: "Moderate damage" }
            ];
            this.renderBlastZones(blastZones);
        }

        if (temporalData.seismicIntensity > 0) {
            const seismicZones = [
                { center: scenario.location, radius: temporalData.seismicIntensity * 50000, intensity: 0.8, description: "Strong seismic waves" },
                { center: scenario.location, radius: temporalData.seismicIntensity * 100000, intensity: 0.5, description: "Moderate tremors" }
            ];
            this.renderSeismicZones(seismicZones);
        }

        if (temporalData.thermalRadius > 0) {
            const thermalZones = [
                { center: scenario.location, radius: temporalData.thermalRadius * 1000 * 0.6, intensity: 0.9, description: "Intense heat flash" },
                { center: scenario.location, radius: temporalData.thermalRadius * 1000, intensity: 0.6, description: "Significant thermal effects" }
            ];
            this.renderThermalZones(thermalZones);
        }

        // Render static population and crater data
        if (scenario.impactData?.population) {
            this.renderPopulationDensity(scenario.impactData.population);
        }
        if (scenario.impactData?.crater) {
            this.renderCrater(scenario.impactData.crater);
        }

        this.addImpactMarker(scenario.location);
    }

    clearLayers() {
        Object.values(this.layerGroups).forEach(layerGroup => {
            layerGroup.clearLayers();
        });
    }

    renderBlastZones(zones) {
        zones.forEach(zone => {
            const circle = L.circle(zone.center, {
                radius: zone.radius,
                fillColor: this.getEffectColor('blast', zone.intensity),
                color: this.getEffectColor('blast', zone.intensity),
                weight: 2,
                opacity: 0.8,
                fillOpacity: 0.4
            }).bindPopup(`
                <strong>Blast Zone</strong><br>
                Radius: ${(zone.radius / 1000).toFixed(1)} km<br>
                Intensity: ${(zone.intensity * 100).toFixed(0)}%<br>
                ${zone.description}
            `);
            this.layerGroups.blast.addLayer(circle);
        });
    }

    renderSeismicZones(zones) {
        zones.forEach(zone => {
            const circle = L.circle(zone.center, {
                radius: zone.radius,
                fillColor: this.getEffectColor('seismic', zone.intensity),
                color: this.getEffectColor('seismic', zone.intensity),
                weight: 2,
                opacity: 0.6,
                fillOpacity: 0.3
            }).bindPopup(`
                <strong>Seismic Effects</strong><br>
                Radius: ${(zone.radius / 1000).toFixed(1)} km<br>
                Intensity: ${(zone.intensity * 100).toFixed(0)}%<br>
                ${zone.description}
            `);
            this.layerGroups.seismic.addLayer(circle);
        });
    }

    renderThermalZones(zones) {
        zones.forEach(zone => {
            const circle = L.circle(zone.center, {
                radius: zone.radius,
                fillColor: this.getEffectColor('thermal', zone.intensity),
                color: this.getEffectColor('thermal', zone.intensity),
                weight: 2,
                opacity: 0.7,
                fillOpacity: 0.3
            }).bindPopup(`
                <strong>Thermal Effects</strong><br>
                Radius: ${(zone.radius / 1000).toFixed(1)} km<br>
                Intensity: ${(zone.intensity * 100).toFixed(0)}%<br>
                ${zone.description}
            `);
            this.layerGroups.thermal.addLayer(circle);
        });
    }

    renderPopulationDensity(areas) {
        areas.forEach(area => {
            const opacity = area.density * 0.5;
            const rectangle = L.rectangle(area.bounds, {
                fillColor: '#00ffff',
                color: '#00ffff',
                weight: 1,
                opacity: opacity,
                fillOpacity: opacity * 0.5
            }).bindPopup(`
                <strong>Population Density</strong><br>
                Density: ${(area.density * 100).toFixed(0)}%<br>
                ${area.description}
            `);
            this.layerGroups.population.addLayer(rectangle);
        });
    }

    renderCrater(crater) {
        const craterCircle = L.circle(crater.center, {
            radius: crater.radius,
            fillColor: '#8b4513',
            color: '#654321',
            weight: 3,
            opacity: 1.0,
            fillOpacity: 0.8
        }).bindPopup(`
            <strong>Impact Crater</strong><br>
            ${crater.description}
        `);
        this.layerGroups.crater.addLayer(craterCircle);
    }

    addImpactMarker(location) {
        const impactMarker = L.marker(location, {
            icon: L.divIcon({
                className: 'impact-marker',
                html: '💥',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            })
        }).bindPopup('<strong>Impact Point</strong>');
        this.layerGroups.crater.addLayer(impactMarker);
    }

    getEffectColor(effectType, intensity) {
        const colors = {
            blast: {
                1.0: '#ff0000',
                0.8: '#ff4500',
                0.6: '#ffa500',
                0.4: '#ffff00',
                0.2: '#90ee90'
            },
            seismic: {
                1.0: '#8b0000',
                0.8: '#ff4500',
                0.6: '#ffa500',
                0.4: '#ffff00',
                0.2: '#90ee90'
            },
            thermal: {
                1.0: '#ffff00',
                0.8: '#ffd700',
                0.6: '#ffa500',
                0.4: '#ff6347',
                0.2: '#90ee90'
            }
        };

        const colorMap = colors[effectType] || colors.blast;
        const intensities = Object.keys(colorMap).map(Number).sort((a, b) => b - a);
        
        for (let i of intensities) {
            if (intensity >= i) {
                return colorMap[i];
            }
        }
        return colorMap[intensities[intensities.length - 1]];
    }

    interpolateTemporalData(currentTime, scenario) {
        const markers = scenario.markers;
        const effects = scenario.temporalEffects;

        let beforeIndex = 0;
        let afterIndex = 0;

        for (let i = 0; i < markers.length - 1; i++) {
            if (currentTime >= markers[i].time && currentTime <= markers[i + 1].time) {
                beforeIndex = i;
                afterIndex = i + 1;
                break;
            }
        }

        if (currentTime <= markers[0].time) {
            return this.getEffectsAtIndex(0, effects);
        }

        if (currentTime >= markers[markers.length - 1].time) {
            return this.getEffectsAtIndex(markers.length - 1, effects);
        }

        const beforeMarker = markers[beforeIndex];
        const afterMarker = markers[afterIndex];
        const timeDiff = afterMarker.time - beforeMarker.time;
        const timeProgress = (currentTime - beforeMarker.time) / timeDiff;

        const interpolate = (before, after) => {
            return before + (after - before) * timeProgress;
        };

        return {
            blastRadius: interpolate(effects.blastRadius[beforeIndex], effects.blastRadius[afterIndex]),
            seismicIntensity: interpolate(effects.seismicIntensity[beforeIndex], effects.seismicIntensity[afterIndex]),
            thermalRadius: interpolate(effects.thermalRadius[beforeIndex], effects.thermalRadius[afterIndex]),
            casualties: Math.round(interpolate(effects.casualties[beforeIndex], effects.casualties[afterIndex])),
            airQuality: Math.round(interpolate(effects.airQuality[beforeIndex], effects.airQuality[afterIndex])),
            temperatureRise: interpolate(effects.temperatureRise[beforeIndex], effects.temperatureRise[afterIndex]),
            radiationLevel: interpolate(effects.radiationLevel[beforeIndex], effects.radiationLevel[afterIndex]),
            windSpeed: Math.round(interpolate(effects.windSpeed[beforeIndex], effects.windSpeed[afterIndex])),
            debrisCloud: interpolate(effects.debrisCloud[beforeIndex], effects.debrisCloud[afterIndex]),
            infrastructureDamage: Math.round(interpolate(effects.infrastructureDamage[beforeIndex], effects.infrastructureDamage[afterIndex]))
        };
    }

    getEffectsAtIndex(index, effects) {
        return {
            blastRadius: effects.blastRadius[index],
            seismicIntensity: effects.seismicIntensity[index],
            thermalRadius: effects.thermalRadius[index],
            casualties: effects.casualties[index],
            airQuality: effects.airQuality[index],
            temperatureRise: effects.temperatureRise[index],
            radiationLevel: effects.radiationLevel[index],
            windSpeed: effects.windSpeed[index],
            debrisCloud: effects.debrisCloud[index],
            infrastructureDamage: effects.infrastructureDamage[index]
        };
    }

    getStaticData() {
        return {
            blastRadius: 0,
            seismicIntensity: 0,
            thermalRadius: 0,
            casualties: 0,
            airQuality: 50,
            temperatureRise: 0,
            radiationLevel: 0,
            windSpeed: 0,
            debrisCloud: 0,
            infrastructureDamage: 0
        };
    }

    updateRealtimeData(data) {
        this.updateRichterScale(data.seismicIntensity);
        this.updateCasualties(data.casualties);
        this.updateAirQuality(data.airQuality);
        this.updateTemperature(data.temperatureRise);
        this.updateRadiation(data.radiationLevel);
        this.updateWindSpeed(data.windSpeed);
        this.updateDebrisCloud(data.debrisCloud);
        this.updateInfrastructure(data.infrastructureDamage);
    }

    updateRichterScale(value) {
        const element = document.getElementById('richter-value');
        if (!element) return;

        element.textContent = value.toFixed(1);
        element.className = 'data-value';
        
        if (value >= 7.0) {
            element.classList.add('critical');
        } else if (value >= 4.0) {
            element.classList.add('warning');
        } else if (value < 1.0) {
            element.classList.add('good');
        }
    }

    updateCasualties(value) {
        const element = document.getElementById('casualties-value');
        if (!element) return;

        element.textContent = this.formatNumber(value);
        element.className = 'data-value';
        
        if (value > 1000000) {
            element.classList.add('critical');
        } else if (value > 1000) {
            element.classList.add('warning');
        } else {
            element.classList.add('good');
        }
    }

    updateAirQuality(value) {
        const element = document.getElementById('aqi-value');
        if (!element) return;

        let text = '';
        let className = 'data-value';

        if (value <= 50) {
            text = `Good (${value})`;
            className += ' good';
        } else if (value <= 100) {
            text = `Moderate (${value})`;
        } else if (value <= 150) {
            text = `Unhealthy (${value})`;
            className += ' warning';
        } else if (value <= 300) {
            text = `Very Unhealthy (${value})`;
            className += ' critical';
        } else {
            text = `Hazardous (${value})`;
            className += ' critical';
        }

        element.textContent = text;
        element.className = className;
    }

    updateTemperature(value) {
        const element = document.getElementById('temp-value');
        if (!element) return;

        element.textContent = `+${value.toFixed(1)}°C`;
        element.className = 'data-value';
        
        if (value > 50) {
            element.classList.add('critical');
        } else if (value > 10) {
            element.classList.add('warning');
        } else {
            element.classList.add('good');
        }
    }

    updateRadiation(value) {
        const element = document.getElementById('radiation-value');
        if (!element) return;

        let text = '';
        let className = 'data-value';

        if (value === 0) {
            text = 'Normal';
            className += ' good';
        } else if (value < 1) {
            text = 'Slightly Elevated';
            className += ' warning';
        } else if (value < 3) {
            text = 'Elevated';
            className += ' warning';
        } else {
            text = 'Dangerous';
            className += ' critical';
        }

        element.textContent = text;
        element.className = className;
    }

    updateWindSpeed(value) {
        const element = document.getElementById('wind-value');
        if (!element) return;

        element.textContent = `${value} km/h`;
        element.className = 'data-value';
        
        if (value > 200) {
            element.classList.add('critical');
        } else if (value > 50) {
            element.classList.add('warning');
        } else {
            element.classList.add('good');
        }
    }

    updateDebrisCloud(value) {
        const element = document.getElementById('debris-value');
        if (!element) return;

        let text = '';
        let className = 'data-value';

        if (value === 0) {
            text = 'None';
            className += ' good';
        } else if (value < 0.3) {
            text = 'Light';
            className += ' warning';
        } else if (value < 0.7) {
            text = 'Moderate';
            className += ' warning';
        } else {
            text = 'Heavy';
            className += ' critical';
        }

        element.textContent = text;
        element.className = className;
    }

    updateInfrastructure(value) {
        const element = document.getElementById('infrastructure-value');
        if (!element) return;

        const remaining = 100 - value;
        element.textContent = `${remaining}%`;
        element.className = 'data-value';
        
        if (remaining < 20) {
            element.classList.add('critical');
        } else if (remaining < 50) {
            element.classList.add('warning');
        } else {
            element.classList.add('good');
        }
    }

    formatNumber(num) {
        if (num >= 1000000000) {
            return (num / 1000000000).toFixed(1) + 'B';
        } else if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }

    toggleLayer(layerType) {
        const checkbox = document.getElementById(`${layerType}-layer`);
        const layerGroup = this.layerGroups[layerType];

        if (checkbox.checked) {
            this.map.addLayer(layerGroup);
        } else {
            this.map.removeLayer(layerGroup);
        }
    }
}