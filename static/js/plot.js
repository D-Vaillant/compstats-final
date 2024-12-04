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
        if (!this.points) {
            console.log('No points data');
            return;
        }
        
        // console.log('Received data structure:', this.points);
    
        const data = [
            // Ground Truth Layer
            {
                x: this.points.groundTruth.map(p => p.x),
                y: this.points.groundTruth.map(p => p.y),
                type: 'scatter',
                mode: 'lines',
                name: 'Ground Truth',
                line: {
                    color: 'rgb(70, 70, 70)',
                    width: 2,
                    opacity: 0.3
                }
            },
            // Predicted Layer
            {
                x: this.points.predicted.map(p => p.x),
                y: this.points.predicted.map(p => p.y),
                type: 'scatter',
                mode: 'lines',
                name: 'Predicted',
                line: {
                    color: '#2196F3',
                    width: 3,
                    dash: 'dash',
                    opacity: 0.6
                }
            },
            // Sampled Points Layer
            {
                x: this.points.sampledPoints.filter(p => p.is_point).map(p => p.x),
                y: this.points.sampledPoints.filter(p => p.is_point).map(p => p.y),
                type: 'scatter',
                mode: 'markers',
                name: 'Samples',
                marker: {
                    size: 8,
                    color: this.points.sampledPoints
                        .filter(p => p.is_point)
                        .map(p => p.color),
                    symbol: 'circle',
                    opacity: 0.7,
                    line: {
                        color: 'white',
                        width: 2
                    }
                }
            }
        ];
    
        const layout = {
            title: 'Lissajous Curve',
            showlegend: true,
            legend: {
                x: 1,
                y: 0.5,
                xanchor: 'right',
                yanchor: 'middle',
                bgcolor: 'rgba(255, 255, 255, 0.8)',
                bordercolor: '#ccc',
                borderwidth: 1
            },
            xaxis: {
                gridcolor: '#eee',
                zerolinecolor: '#ccc',
                title: 'X'
            },
            yaxis: {
                gridcolor: '#eee',
                zerolinecolor: '#ccc',
                title: 'Y',
                scaleanchor: 'x',
                scaleratio: 1
            },
            paper_bgcolor: '#fafafa',
            plot_bgcolor: '#ececec'
        };
    
        Plotly.react('plot', data, layout);
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
                // Get all current points
                const response = await fetch('/fit_points', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        'sampled_points': this.points.sampledPoints,
                        'ground_truth': this.points.groundTruth})
                });
    
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
    
                this.points = await response.json();
                this.updatePlot();
                this.logStatus('Curves fitted and plotted');
            } catch (error) {
                this.logStatus('Error fitting curves: ' + error.message);
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