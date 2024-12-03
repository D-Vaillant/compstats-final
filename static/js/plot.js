class ParametricPlot {
    constructor() {
        this.isPreviewMode = false;
        this.points = null;
        
        // Initialize UI elements
        this.previewButton = document.getElementById('previewButton');
        this.resetButton = document.getElementById('resetButton');
        this.statusLog = document.getElementById('statusLog');
        
        // Initialize parameters with their DOM elements
        this.params = {
            A: document.getElementById('A'),         // Amplitude X
            a: document.getElementById('a'),         // Frequency X
            B: document.getElementById('B'),         // Amplitude Y
            b: document.getElementById('b'),         // Frequency Y
            phase: document.getElementById('phase'),  // Phase shift
            n_sampled: document.getElementById('n_sampled')   // Points to highlight
        };

        this.setupEventListeners();
        this.initializePlot();

        // Generate initial curve
        this.fetchAndUpdatePlot().then(() => {
            this.logStatus('Initial curve generated');
        });
    }

    setupEventListeners() {
        // Add event listeners for all parameter inputs
        Object.entries(this.params).forEach(([key, element]) => {
            element.addEventListener('input', () => {
                // Update the display value
                document.getElementById(`${key}Value`).textContent = element.value;
                // Update plot if not in preview mode
                if (!this.isPreviewMode) {
                    this.fetchAndUpdatePlot();
                }
            });
        });

        // Button event listeners
        this.previewButton.addEventListener('click', () => this.handlePreviewClick());
        this.resetButton.addEventListener('click', () => this.handleResetClick());
    }

    initializePlot() {
        // Setup initial plot layout
        const layout = {
            title: 'Parametric Curve',
            showlegend: true,
            xaxis: {
                title: 'X',
                zeroline: true,
                showgrid: true
            },
            yaxis: {
                title: 'Y',
                zeroline: true,
                showgrid: true,
                scaleanchor: 'x',  // Ensure equal scaling
                scaleratio: 1
            }
        };

        Plotly.newPlot('plot', [], layout);
    }

    async fetchAndUpdatePlot() {
        try {
            // Build query string from parameters
            const params = new URLSearchParams();
            Object.entries(this.params).forEach(([key, element]) => {
                params.append(key, element.value);
            });
    
            // Fetch points from backend using query parameters
            const response = await fetch(`/get_points?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                }
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
    
            this.points = await response.json();
            
            if (this.points.error) {
                throw new Error(this.points.error);
            }
    
            this.updatePlot();
            // this.logStatus('Data updated successfully');
        } catch (error) {
            this.logStatus('Error fetching data: ' + error.message);
            console.error('Error:', error);
        }
    }

    updatePlot() {
        if (!this.points) return;

        // Separate regular line points and highlighted points
        const linePoints = this.points.map(p => ({ x: p.x, y: p.y }));
        const highlightedPoints = this.points
            .filter(p => p.is_point)
            .map(p => ({
                x: p.x,
                y: p.y,
                color: p.color
            }));

        // Create data array for plotting
        const data = [
            // Continuous line
            {
                x: linePoints.map(p => p.x),
                y: linePoints.map(p => p.y),
                type: 'scatter',
                mode: 'lines',
                name: 'Curve',
                line: { color: '#2196F3', width: 2 }
            },
            // Highlighted points
            {
                x: highlightedPoints.map(p => p.x),
                y: highlightedPoints.map(p => p.y),
                type: 'scatter',
                mode: 'markers',
                name: 'Sampled Points',
                marker: {
                    size: 8,
                    color: highlightedPoints.map(p => p.color)
                }
            }
        ];

        Plotly.react('plot', data);
    }

    async handlePreviewClick() {
        if (!this.isPreviewMode) {
            // Enter preview mode
            this.isPreviewMode = true;
            this.previewButton.textContent = 'Run';
            this.resetButton.disabled = false;
            Object.values(this.params).forEach(param => param.disabled = true);
        } else {
            // Execute run action
            this.previewButton.disabled = true;
            
            try {
                // Send sampled points to fitting endpoint
                const response = await fetch('/fit_points', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.points.filter(p => p.is_point))
                });
    
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
    
                this.points = await response.json();
                this.updatePlot();
                this.logStatus('Curve fitted to points');
            } catch (error) {
                this.logStatus('Error fitting curve: ' + error.message);
                console.error('Error:', error);
            }
        }
    }

    handleResetClick() {
        // Reset to initial state
        this.isPreviewMode = false;
        this.previewButton.textContent = 'Preview';
        this.previewButton.disabled = false;
        this.resetButton.disabled = true;
        Object.values(this.params).forEach(param => param.disabled = false);
        this.points = null;
        this.updatePlot();
        this.logStatus('Plot reset');
    }

    logStatus(message) {
        // Add timestamped message to status log
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        const timestamp = new Date().toLocaleTimeString();
        entry.innerHTML = `<span class="timestamp">[${timestamp}]</span> ${message}`;
        this.statusLog.insertBefore(entry, this.statusLog.firstChild);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ParametricPlot();
});