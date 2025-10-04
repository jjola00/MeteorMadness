// Test script to validate the 2D impact visualizer functionality
// This can be run in the browser console to test different scenarios

console.log("Testing 2D Impact Visualizer...");

// Test data structure validation
function validateScenarioData(scenario) {
    const required = ['name', 'location', 'energy', 'casualties', 'crater', 'impactData'];
    const impactRequired = ['blast', 'seismic', 'thermal', 'population'];
    
    for (let field of required) {
        if (!scenario.hasOwnProperty(field)) {
            console.error(`Missing required field: ${field}`);
            return false;
        }
    }
    
    for (let field of impactRequired) {
        if (!scenario.impactData.hasOwnProperty(field)) {
            console.error(`Missing impact data field: ${field}`);
            return false;
        }
    }
    
    return true;
}

// Test all scenarios
function testAllScenarios() {
    console.log("Testing scenario data integrity...");
    
    const scenarios = ['tunguska', 'chelyabinsk', 'chicxulub', 'hypothetical'];
    let allValid = true;
    
    scenarios.forEach(scenarioId => {
        if (typeof impactScenarios !== 'undefined' && impactScenarios[scenarioId]) {
            const isValid = validateScenarioData(impactScenarios[scenarioId]);
            console.log(`${scenarioId}: ${isValid ? 'PASS' : 'FAIL'}`);
            allValid = allValid && isValid;
        } else {
            console.error(`Scenario ${scenarioId} not found`);
            allValid = false;
        }
    });
    
    return allValid;
}

// Test layer functionality
function testLayerControls() {
    console.log("Testing layer controls...");
    
    const layers = ['blast', 'seismic', 'thermal', 'population', 'crater'];
    let allLayersExist = true;
    
    layers.forEach(layer => {
        const checkbox = document.getElementById(`${layer}-layer`);
        if (!checkbox) {
            console.error(`Layer control not found: ${layer}`);
            allLayersExist = false;
        } else {
            console.log(`Layer control found: ${layer}`);
        }
    });
    
    return allLayersExist;
}

// Test map initialization
function testMapInitialization() {
    console.log("Testing map initialization...");
    
    if (typeof map === 'undefined') {
        console.error("Map not initialized");
        return false;
    }
    
    if (typeof layerGroups === 'undefined') {
        console.error("Layer groups not initialized");
        return false;
    }
    
    console.log("Map and layer groups initialized successfully");
    return true;
}

// Run all tests
function runAllTests() {
    console.log("=== 2D Impact Visualizer Test Suite ===");
    
    const tests = [
        { name: "Scenario Data Validation", test: testAllScenarios },
        { name: "Layer Controls", test: testLayerControls },
        { name: "Map Initialization", test: testMapInitialization }
    ];
    
    let allPassed = true;
    
    tests.forEach(({ name, test }) => {
        console.log(`\nRunning: ${name}`);
        const result = test();
        console.log(`${name}: ${result ? 'PASS' : 'FAIL'}`);
        allPassed = allPassed && result;
    });
    
    console.log(`\n=== Test Results ===`);
    console.log(`Overall: ${allPassed ? 'ALL TESTS PASSED' : 'SOME TESTS FAILED'}`);
    
    return allPassed;
}

// Auto-run tests if in browser environment
if (typeof window !== 'undefined') {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(runAllTests, 1000); // Wait for map to initialize
        });
    } else {
        setTimeout(runAllTests, 1000);
    }
}

// Export for Node.js testing if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        validateScenarioData,
        testAllScenarios,
        testLayerControls,
        testMapInitialization,
        runAllTests
    };
}