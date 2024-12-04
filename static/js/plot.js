class ParametricPlot {
    constructor() {
        this.isPreviewMode = false;
        this.points = null;
        
        // Initialize UI elements
        this.previewButton = document.getElementById('previewButton');
        this.resetButton = document.getElementById('resetButton');
        this.clearButton = document.getElementById('clearButton');
        this.statusLog = document.getElementById('statusLog');
        
        // Initialize parameters with their DOM elements
        this.params = {
            A: document.getElementById('A'),         // Amplitude X
            a: document.getElementById('a'),         // Frequency X
            B: document.getElementById('B'),         // Amplitude Y
            b: document.getElementById('b'),         // Frequency Y
            phase: document.getElementById('phase'),  // Phase shift
            kernel: document.getElementById('kernel'), // Kernel
            n_sampled: document.getElementById('n_sampled'),   // Points to highlight
            noise: document.getElementById('gauss_noise'),  // Amount of gaussian noise
            bandwidth: document.getElementById('bandwidth'), // Band width.
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
            if (element.tagName === 'SELECT') {
                return;
            }
            element.addEventListener('input', () => {
                // Update the display value
                document.getElementById(`${key}Value`).textContent = element.value;
                // Update plot if not in preview mode
                if (!(this.isPreviewMode || element.id === 'bandwidth')) {
                    this.fetchAndUpdatePlot();
                }
            });
        });

        // Button event listeners
        this.previewButton.addEventListener('click', () => this.handlePreviewClick());
        this.resetButton.addEventListener('click', () => this.handleResetClick());
        this.clearButton.addEventListener('click', () => this.handleClearClick());
    }

    initializePlot() {
        // Setup initial plot layout
        const layout = {
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
            console.log('Empty points array.');
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
            this.logStatus(`Regression parameters: kernel=${this.params.kernel.value}, bandwidth=${this.params.bandwidth.value}.`);
            Object.values(this.params).forEach(param => param.disabled = true);
        } else {
            // Execute run action
            this.previewButton.disabled = true;
            
            try {
                const response = await fetch('/fit_points', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        'sampled_points': this.points.sampledPoints,
                        'ground_truth': this.points.groundTruth,
                        'bandwidth': this.params.bandwidth.value,
                        'kernel': this.params.kernel.value})
                });
    
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
    
                const resp = await response.json()
                this.points = resp.points;
                this.updatePlot();
                this.logStatus(`Curves fitted and plotted. MSE = ${resp.error}`);
            } catch (error) {
                this.logStatus('Error fitting curves: ' + error.message);
                console.error('Error:', error);
            }
        }
    }

    handleResetClick() {
        // If prepping a regression, delete log about it. Eh. Not worth it.
        // if (this.isPreviewMode) {
        //     this.statusLog.removeChild(this.statusLog.lastChild);
        // }
        // Reset to initial state
        this.isPreviewMode = false;
        this.previewButton.textContent = 'Preview';
        this.previewButton.disabled = false;
        this.resetButton.disabled = true;

        Object.values(this.params).forEach(param => param.disabled = false);
        // this.points = this.points.groundTruth.concat(this.points.sampledPoints);
        this.updatePlot();
        // this.logStatus('Plot reset');
    }

    handleClearClick() {
        // Wipes the entry log.
        this.statusLog.replaceChildren();
    }

    logStatus(message) {
        // Add timestamped message to status log
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        const timestamp = new Date().toLocaleTimeString();
        entry.innerHTML = `<span class="timestamp">[${timestamp}]</span> ${message}`;
        this.statusLog.append(entry);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ParametricPlot();
});