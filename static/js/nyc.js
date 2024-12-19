class NYCMap {
    constructor() {
        this.base_layout = {
            map: {
                style: 'dark',
                bounds: {
                    north: 41.5,
                    south: 35.5,
                    west: -79,
                    east: -72
                },
                center: {
                    lat: 40.7813,
                    lon: -73.9667
                },
                zoom: 5
            },
            // coloraxis: {colorscale: "Viridis"},
            margin: {r: 0, t: 0, l: 0, b: 0},
            height: 600, width: 1200
        };

        Plotly.newPlot('nycMap', [], this.base_layout);

        this.fetchAndUpdatePlot().then(() => {
            console.log("Map loaded successfully.")
        });
    }

    async loadLocations() {
        const loadingDiv = document.getElementById('loading');

        loadingDiv.style.display = 'block';
        try {
            const response = await fetch('/nyc/locs');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const locations = await response.json();
            return locations;
        } catch (error) {
            console.error('Error loading locations:', error);
            alert('Error loading locations. Please try again.');
            return [];
        } finally {
            loadingDiv.style.display = 'none';
        }
    }
    
    async loadDensities() {
        try {
            const response = await fetch('/nyc/densities');
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const densities = await response.json();
            return densities;
        } catch (error) {
            console.error('Error loading densities:', error);
            alert('Error loading locations. Please try again.');
            return [];
        }
    }

    async fetchAndUpdatePlot() {
        const locations = await this.loadLocations();
        const densities = await this.loadDensities();

        const data = [{
            type: 'scattermap',
            lat: locations.map(loc => loc.decimalLatitude),
            lon: locations.map(loc => loc.decimalLongitude),
            mode: 'markers',
            marker: {
                size: 3,
                opacity: 0.5,
                color: 'white'
            },
            z: locations.map(loc => loc.individualCount),
            text: locations.map(loc => loc.individualCount),
            hoverinfo: 'text'
        }, {
            type: 'densitymap',
            lat: densities.map(loc => loc.lat),
            lon: densities.map(loc => loc.lon),
            z: densities.map(loc => (loc.z)),
            colorscale: 'Portland',
            radius: 25,
            opacity: 0.2
        }];

    Plotly.react('nycMap', data, this.base_layout);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new NYCMap();
});