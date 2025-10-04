// Impact scenario data for the asteroid impact simulator

export const impactScenarios = {
    tunguska: {
        name: "Tunguska Event (1908)",
        location: [60.8858, 101.8944], // Tunguska, Russia
        energy: "15 MT TNT",
        casualties: "0 (remote area)",
        crater: "No crater (airburst)",
        duration: 86400 * 3, // 3 days
        markers: [
            { time: 0, label: "Impact", phase: "Impact" },
            { time: 300, label: "Peak Blast", phase: "Blast Wave" },
            { time: 3600, label: "Fire Spread", phase: "Secondary Effects" },
            { time: 86400, label: "Day 1", phase: "Assessment" },
            { time: 259200, label: "Day 3", phase: "Recovery" }
        ],
        temporalEffects: {
            blastRadius: [0, 15, 30, 30, 25],
            seismicIntensity: [0, 5.0, 3.2, 1.5, 0.8],
            thermalRadius: [0, 8, 12, 10, 8],
            casualties: [0, 0, 0, 0, 0], // Remote area
            airQuality: [50, 150, 300, 200, 100], // AQI values
            temperatureRise: [0, 15, 25, 20, 10], // Celsius
            radiationLevel: [0, 0, 0, 0, 0], // No radiation from impact
            windSpeed: [0, 80, 120, 60, 20], // km/h from blast
            debrisCloud: [0, 0.5, 1.0, 0.8, 0.3], // Coverage factor
            infrastructureDamage: [0, 0, 0, 0, 0] // % damage (remote area)
        },
        impactData: {
            blast: [
                { center: [60.8858, 101.8944], radius: 15000, intensity: 1.0, description: "Total forest destruction" },
                { center: [60.8858, 101.8944], radius: 30000, intensity: 0.7, description: "Severe tree damage" },
                { center: [60.8858, 101.8944], radius: 50000, intensity: 0.4, description: "Moderate damage" }
            ],
            seismic: [
                { center: [60.8858, 101.8944], radius: 100000, intensity: 0.8, description: "Strong seismic waves" },
                { center: [60.8858, 101.8944], radius: 200000, intensity: 0.5, description: "Moderate tremors" },
                { center: [60.8858, 101.8944], radius: 500000, intensity: 0.2, description: "Detectable tremors" }
            ],
            thermal: [
                { center: [60.8858, 101.8944], radius: 20000, intensity: 0.9, description: "Intense heat flash" },
                { center: [60.8858, 101.8944], radius: 40000, intensity: 0.6, description: "Significant thermal effects" },
                { center: [60.8858, 101.8944], radius: 80000, intensity: 0.3, description: "Mild thermal effects" }
            ],
            population: [
                { bounds: [[60.5, 101.5], [61.2, 102.3]], density: 0.1, description: "Sparse population" }
            ],
            crater: null // No crater for airburst
        }
    },
    chelyabinsk: {
        name: "Chelyabinsk Meteor (2013)",
        location: [55.1540, 61.4291], // Chelyabinsk, Russia
        energy: "500 KT TNT",
        casualties: "~1,500 injured",
        crater: "No crater (airburst)",
        duration: 86400 * 2, // 2 days
        markers: [
            { time: 0, label: "Airburst", phase: "Airburst" },
            { time: 60, label: "Shockwave", phase: "Shockwave" },
            { time: 1800, label: "Damage Assessment", phase: "Assessment" },
            { time: 86400, label: "Day 1", phase: "Recovery" },
            { time: 172800, label: "Day 2", phase: "Cleanup" }
        ],
        temporalEffects: {
            blastRadius: [0, 8, 12, 10, 8],
            seismicIntensity: [0, 2.7, 1.8, 0.5, 0.2],
            thermalRadius: [0, 5, 8, 6, 4],
            casualties: [0, 500, 1500, 1200, 800],
            airQuality: [50, 200, 400, 300, 150],
            temperatureRise: [0, 8, 12, 8, 4],
            radiationLevel: [0, 0, 0, 0, 0],
            windSpeed: [0, 60, 100, 40, 15],
            debrisCloud: [0, 0.3, 0.7, 0.5, 0.2],
            infrastructureDamage: [0, 15, 35, 25, 10]
        },
        impactData: {
            blast: [
                { center: [55.1540, 61.4291], radius: 5000, intensity: 0.8, description: "Window damage zone" },
                { center: [55.1540, 61.4291], radius: 15000, intensity: 0.5, description: "Minor structural damage" },
                { center: [55.1540, 61.4291], radius: 30000, intensity: 0.2, description: "Light damage" }
            ],
            seismic: [
                { center: [55.1540, 61.4291], radius: 50000, intensity: 0.6, description: "Detectable tremors" },
                { center: [55.1540, 61.4291], radius: 100000, intensity: 0.3, description: "Weak tremors" }
            ],
            thermal: [
                { center: [55.1540, 61.4291], radius: 10000, intensity: 0.7, description: "Bright flash effects" },
                { center: [55.1540, 61.4291], radius: 25000, intensity: 0.4, description: "Visible thermal effects" }
            ],
            population: [
                { bounds: [[55.0, 61.2], [55.3, 61.7]], density: 0.8, description: "Urban area" },
                { bounds: [[54.8, 61.0], [55.5, 62.0]], density: 0.4, description: "Suburban area" }
            ],
            crater: null
        }
    },
    chicxulub: {
        name: "Chicxulub Impact (66 MYA)",
        location: [21.4, -89.5], // Yucatan Peninsula
        energy: "100 TT TNT",
        casualties: "Mass extinction event",
        crater: "180 km diameter",
        duration: 86400 * 365, // 1 year
        markers: [
            { time: 0, label: "Impact", phase: "Impact" },
            { time: 3600, label: "Global Shockwave", phase: "Global Effects" },
            { time: 86400, label: "Nuclear Winter Begins", phase: "Climate Change" },
            { time: 2592000, label: "Month 1", phase: "Mass Extinction" },
            { time: 15552000, label: "Month 6", phase: "Ecosystem Collapse" },
            { time: 31536000, label: "Year 1", phase: "Recovery Begins" }
        ],
        temporalEffects: {
            blastRadius: [0, 1000, 2000, 1800, 1500, 1200],
            seismicIntensity: [0, 11.0, 8.5, 6.0, 4.0, 2.0],
            thermalRadius: [0, 2000, 3000, 2500, 2000, 1500],
            casualties: [0, 500000000, 2000000000, 4000000000, 6000000000, 7000000000],
            airQuality: [50, 500, 999, 800, 600, 400],
            temperatureRise: [0, 100, 200, 150, 100, 50],
            radiationLevel: [0, 2, 5, 4, 3, 1], // Elevated from debris
            windSpeed: [0, 500, 800, 400, 200, 100],
            debrisCloud: [0, 1.0, 1.0, 0.9, 0.7, 0.5],
            infrastructureDamage: [0, 80, 95, 90, 85, 70]
        },
        impactData: {
            blast: [
                { center: [21.4, -89.5], radius: 500000, intensity: 1.0, description: "Complete devastation" },
                { center: [21.4, -89.5], radius: 1000000, intensity: 0.8, description: "Severe destruction" },
                { center: [21.4, -89.5], radius: 2000000, intensity: 0.6, description: "Major damage" }
            ],
            seismic: [
                { center: [21.4, -89.5], radius: 3000000, intensity: 0.9, description: "Magnitude 10+ earthquake" },
                { center: [21.4, -89.5], radius: 5000000, intensity: 0.7, description: "Severe seismic activity" }
            ],
            thermal: [
                { center: [21.4, -89.5], radius: 1500000, intensity: 1.0, description: "Global thermal pulse" },
                { center: [21.4, -89.5], radius: 3000000, intensity: 0.8, description: "Intense heat" }
            ],
            population: [
                { bounds: [[20.0, -91.0], [23.0, -88.0]], density: 0.0, description: "No human population (66 MYA)" }
            ],
            crater: { center: [21.4, -89.5], radius: 90000, description: "180 km diameter crater" }
        }
    },
    hypothetical: {
        name: "NYC Hypothetical Impact",
        location: [40.7128, -74.0060], // New York City
        energy: "50 MT TNT",
        casualties: "~8 million at risk",
        crater: "2 km diameter",
        duration: 86400 * 7, // 7 days
        markers: [
            { time: 0, label: "Impact", phase: "Impact" },
            { time: 600, label: "Peak Effects", phase: "Peak Damage" },
            { time: 3600, label: "Hour 1", phase: "Immediate Response" },
            { time: 86400, label: "Day 1", phase: "Assessment" },
            { time: 259200, label: "Day 3", phase: "Recovery" },
            { time: 604800, label: "Week 1", phase: "Reconstruction" }
        ],
        temporalEffects: {
            blastRadius: [0, 50, 75, 70, 60, 50],
            seismicIntensity: [0, 7.2, 5.8, 4.1, 2.5, 1.2],
            thermalRadius: [0, 30, 45, 40, 35, 30],
            casualties: [0, 2000000, 5000000, 4500000, 3000000, 2000000],
            airQuality: [50, 300, 500, 400, 250, 150],
            temperatureRise: [0, 30, 50, 40, 25, 15],
            radiationLevel: [0, 1, 2, 1.5, 1, 0.5],
            windSpeed: [0, 150, 250, 120, 80, 40],
            debrisCloud: [0, 0.8, 1.0, 0.9, 0.6, 0.3],
            infrastructureDamage: [0, 60, 85, 75, 50, 30]
        },
        impactData: {
            blast: [
                { center: [40.7128, -74.0060], radius: 10000, intensity: 1.0, description: "Total destruction" },
                { center: [40.7128, -74.0060], radius: 25000, intensity: 0.8, description: "Severe damage" },
                { center: [40.7128, -74.0060], radius: 50000, intensity: 0.6, description: "Moderate damage" },
                { center: [40.7128, -74.0060], radius: 100000, intensity: 0.3, description: "Light damage" }
            ],
            seismic: [
                { center: [40.7128, -74.0060], radius: 150000, intensity: 0.9, description: "Severe earthquake" },
                { center: [40.7128, -74.0060], radius: 300000, intensity: 0.6, description: "Strong tremors" },
                { center: [40.7128, -74.0060], radius: 500000, intensity: 0.3, description: "Moderate tremors" }
            ],
            thermal: [
                { center: [40.7128, -74.0060], radius: 30000, intensity: 1.0, description: "Lethal thermal radiation" },
                { center: [40.7128, -74.0060], radius: 60000, intensity: 0.7, description: "Severe burns" },
                { center: [40.7128, -74.0060], radius: 120000, intensity: 0.4, description: "Thermal effects" }
            ],
            population: [
                { bounds: [[40.4774, -74.2591], [40.9176, -73.7004]], density: 1.0, description: "Dense urban population" },
                { bounds: [[40.2, -74.5], [41.2, -73.5]], density: 0.6, description: "Metropolitan area" }
            ],
            crater: { center: [40.7128, -74.0060], radius: 1000, description: "2 km diameter crater" }
        }
    }
};