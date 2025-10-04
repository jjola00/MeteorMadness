/**
 * API client for connecting 2D visualization to environmental effects backend
 */

export class EnvironmentalEffectsAPI {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }

    /**
     * Calculate temporal environmental effects for an impact scenario
     * @param {Object} impactData - Impact parameters and location
     * @param {Array} timeRange - [startHours, endHours]
     * @param {number} timeResolution - Hours between data points
     * @param {Array} effectTypes - Types of effects to calculate
     * @returns {Promise<Object>} Temporal effects data
     */
    async calculateTemporalEffects(impactData, timeRange = [0, 168], timeResolution = 1.0, effectTypes = null) {
        try {
            const response = await fetch(`${this.baseUrl}/api/environmental-effects/temporal-effects`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    impact_data: impactData,
                    time_range_hours: timeRange,
                    time_resolution_hours: timeResolution,
                    effect_types: effectTypes
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status !== 'success') {
                throw new Error(result.message || 'API request failed');
            }

            return result.data;
        } catch (error) {
            console.error('Error calculating temporal effects:', error);
            throw error;
        }
    }

    /**
     * Get environmental effects at a specific point in time and location
     * @param {Object} impactData - Impact parameters
     * @param {number} timeHours - Time after impact in hours
     * @param {Object} location - {lat, lon} coordinates
     * @param {Array} effectTypes - Types of effects to calculate
     * @returns {Promise<Object>} Point effects data
     */
    async getPointEffects(impactData, timeHours, location, effectTypes = null) {
        try {
            const response = await fetch(`${this.baseUrl}/api/environmental-effects/point-effects`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    impact_data: impactData,
                    time_hours: timeHours,
                    location: location,
                    effect_types: effectTypes
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status !== 'success') {
                throw new Error(result.message || 'API request failed');
            }

            return result.data;
        } catch (error) {
            console.error('Error getting point effects:', error);
            throw error;
        }
    }

    /**
     * Get a sample scenario for testing
     * @param {string} scenario - 'small', 'medium', or 'large'
     * @param {string} location - 'land' or 'ocean'
     * @returns {Promise<Object>} Sample scenario data
     */
    async getSampleScenario(scenario = 'medium', location = 'land') {
        try {
            const response = await fetch(
                `${this.baseUrl}/api/environmental-effects/sample-scenario?scenario=${scenario}&location=${location}`
            );

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status !== 'success') {
                throw new Error(result.message || 'API request failed');
            }

            return result.data;
        } catch (error) {
            console.error('Error getting sample scenario:', error);
            throw error;
        }
    }

    /**
     * Get available effect types
     * @returns {Promise<Array>} List of available effect types
     */
    async getEffectTypes() {
        try {
            const response = await fetch(`${this.baseUrl}/api/environmental-effects/effect-types`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status !== 'success') {
                throw new Error(result.message || 'API request failed');
            }

            return result.data.effect_types;
        } catch (error) {
            console.error('Error getting effect types:', error);
            throw error;
        }
    }

    /**
     * Convert backend temporal effects data to frontend format
     * @param {Object} backendData - Data from temporal-effects API
     * @returns {Object} Frontend-compatible scenario data
     */
    convertToFrontendFormat(backendData) {
        const timeHours = backendData.time_hours;
        const effects = backendData.effects;

        // Extract data arrays for each effect type
        const temporalEffects = {
            blastRadius: [],
            seismicIntensity: [],
            thermalRadius: [],
            casualties: [],
            airQuality: [],
            temperatureChange: [],
            debrisCloud: [],
            infrastructureDamage: []
        };

        // Convert seismic effects
        if (effects.seismic) {
            const seismicTimeline = effects.seismic.intensity_grid || [];
            temporalEffects.seismicIntensity = seismicTimeline.map(intensities => {
                // Take maximum intensity across all distances for timeline
                return Math.max(...intensities);
            });
        }

        // Convert atmospheric effects
        if (effects.atmospheric) {
            const atmTimeline = effects.atmospheric.timeline || [];
            temporalEffects.airQuality = atmTimeline.map(t => t.air_quality_index || 50);
            temporalEffects.temperatureChange = atmTimeline.map(t => t.temperature_change_c || 0);
            temporalEffects.debrisCloud = atmTimeline.map(t =>
                Math.min(1.0, (t.dust_concentration_kg_m3 || 0) / 1e6)
            );
        }

        // Convert thermal effects
        if (effects.thermal) {
            const thermalTimeline = effects.thermal.timeline || [];
            temporalEffects.thermalRadius = thermalTimeline.map(t => t.thermal_radius_km || 0);
        }

        // Convert infrastructure effects
        if (effects.infrastructure) {
            const infraTimeline = effects.infrastructure.timeline || [];
            temporalEffects.infrastructureDamage = infraTimeline.map(t => {
                // Convert damage radius to damage percentage (simplified)
                const maxRadius = Math.max(
                    t.severe_damage_radius_km || 0,
                    t.moderate_damage_radius_km || 0,
                    t.light_damage_radius_km || 0
                );
                return Math.min(100, maxRadius / 10); // Rough conversion
            });
        }

        // Fill in missing arrays with zeros
        const numTimePoints = timeHours.length;
        Object.keys(temporalEffects).forEach(key => {
            if (temporalEffects[key].length === 0) {
                temporalEffects[key] = new Array(numTimePoints).fill(0);
            } else if (temporalEffects[key].length < numTimePoints) {
                // Pad with last value
                const lastValue = temporalEffects[key][temporalEffects[key].length - 1] || 0;
                while (temporalEffects[key].length < numTimePoints) {
                    temporalEffects[key].push(lastValue);
                }
            }
        });

        return {
            timeHours,
            temporalEffects,
            impactLocation: backendData.impact_location
        };
    }

    /**
     * Generate impact data layers for map visualization
     * @param {Object} backendData - Data from temporal-effects API
     * @param {number} currentTimeIndex - Current time index for visualization
     * @returns {Object} Map layer data
     */
    generateMapLayers(backendData, currentTimeIndex = 0) {
        const effects = backendData.effects;
        const impactLocation = backendData.impact_location;
        const center = [impactLocation.lat, impactLocation.lon];

        const layers = {
            blast: [],
            seismic: [],
            thermal: [],
            population: [],
            crater: null
        };

        // Generate blast layers from infrastructure effects
        if (effects.infrastructure) {
            const infraData = effects.infrastructure.timeline[currentTimeIndex] || effects.infrastructure.timeline[0];
            if (infraData) {
                if (infraData.severe_damage_radius_km > 0) {
                    layers.blast.push({
                        center,
                        radius: infraData.severe_damage_radius_km * 1000, // Convert to meters
                        intensity: 1.0,
                        description: "Severe damage zone"
                    });
                }
                if (infraData.moderate_damage_radius_km > 0) {
                    layers.blast.push({
                        center,
                        radius: infraData.moderate_damage_radius_km * 1000,
                        intensity: 0.7,
                        description: "Moderate damage zone"
                    });
                }
                if (infraData.light_damage_radius_km > 0) {
                    layers.blast.push({
                        center,
                        radius: infraData.light_damage_radius_km * 1000,
                        intensity: 0.4,
                        description: "Light damage zone"
                    });
                }
            }
        }

        // Generate seismic layers
        if (effects.seismic) {
            const distances = effects.seismic.distances_km || [];
            const intensities = effects.seismic.intensity_grid[currentTimeIndex] || [];

            for (let i = 0; i < distances.length; i += 10) { // Sample every 10th point
                if (intensities[i] > 0.1) { // Only show significant intensities
                    layers.seismic.push({
                        center,
                        radius: distances[i] * 1000,
                        intensity: Math.min(1.0, intensities[i] / 5.0), // Normalize to 0-1
                        description: `Seismic intensity ${intensities[i].toFixed(1)}`
                    });
                }
            }
        }

        // Generate thermal layers
        if (effects.thermal) {
            const thermalData = effects.thermal.timeline[currentTimeIndex] || effects.thermal.timeline[0];
            if (thermalData && thermalData.thermal_radius_km > 0) {
                layers.thermal.push({
                    center,
                    radius: thermalData.thermal_radius_km * 1000,
                    intensity: thermalData.intensity_fraction || 0.5,
                    description: "Thermal radiation zone"
                });
            }
        }

        // Add basic population layer (this will be enhanced with real population data later)
        const bounds = [
            [center[0] - 1, center[1] - 1],
            [center[0] + 1, center[1] + 1]
        ];
        layers.population.push({
            bounds,
            density: 0.5,
            description: "Population area (placeholder)"
        });

        return layers;
    }
}