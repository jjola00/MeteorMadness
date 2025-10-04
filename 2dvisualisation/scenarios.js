// Scenario metadata only - all impact data now comes from backend API

export const scenarioMetadata = {
    tunguska: {
        name: "Tunguska Event (1908)",
        description: "Small asteroid airburst similar to 1908 Tunguska event",
        backendParams: { scenario: 'small', location: 'land' },
        historicalLocation: [60.8858, 101.8944], // Tunguska, Russia
        defaultZoom: 8
    },
    chelyabinsk: {
        name: "Chelyabinsk Meteor (2013)",
        description: "Small asteroid airburst similar to 2013 Chelyabinsk event",
        backendParams: { scenario: 'small', location: 'land' },
        historicalLocation: [55.1540, 61.4291], // Chelyabinsk, Russia
        defaultZoom: 8
    },
    chicxulub: {
        name: "Chicxulub Impact (66 MYA)",
        description: "Large asteroid impact with global consequences",
        backendParams: { scenario: 'large', location: 'land' },
        historicalLocation: [21.4, -89.5], // Yucatan Peninsula
        defaultZoom: 4
    },
    hypothetical: {
        name: "NYC Hypothetical Impact",
        description: "Medium-sized asteroid impact in urban area",
        backendParams: { scenario: 'medium', location: 'land' },
        historicalLocation: [40.7128, -74.0060], // New York City
        defaultZoom: 8
    }
};

// Legacy support - will be removed once backend integration is complete
export const impactScenarios = scenarioMetadata;