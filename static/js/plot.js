class ParametricPlot {
    constructor() {
        this.isPreviewMode = false;
        this.points = null;
        this.baseLayout = {
            title: 'Lissajous Curve',
            showlegend: true,
            updatemenus: [{
                type: 'buttons',
                direction: 'right',
                showactive: true,
                x: 0.5,
                xanchor: 'center',
                y: 1.055,
                buttons: [{
                    label: 'X vs Y',
                    method: 'update',
                    args: [{'visible': [true, true, true, false, false, false, false, false, false]}, {'xaxis.title': 'X', 'yaxis.title': 'Y'}]
                }, {
                    label: 'T vs X',
                    method: 'update',
                    args: [{'visible': [false, false, false, true, true, true, false, false, false]}, {'xaxis.title': 'T', 'yaxis.title': 'X'}]
                }, {
                    label: 'T vs Y',
                    method: 'update',
                    args: [{'visible': [false, false, false, false, false, false, true, true, true]}, {'xaxis.title': 'T', 'yaxis.title': 'Y'}]
                }]
            }],
            legend: {
                x: 1,
                y: 1,
                xanchor: 'right',
                yanchor: 'top',
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
            bandwidthX: document.getElementById('bandwidthX'), // Band width for X.
            bandwidthY: document.getElementById('bandwidthY'), // Band width for Y.
        };

        this.setupEventListeners();
        Plotly.newPlot('plot', [], this.baseLayout);

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
                if (!(this.isPreviewMode || element.id.startsWith('bandwidth'))) {
                    this.fetchAndUpdatePlot();
                }
            });
        });

        // Button event listeners
        this.previewButton.addEventListener('click', () => this.handlePreviewClick());
        this.resetButton.addEventListener('click', () => this.handleResetClick());
        this.clearButton.addEventListener('click', () => this.handleClearClick());
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

        const getHoverText = (points) => points.map(p => 
            `T: ${p.t}<br>X: ${p.x}<br>Y: ${p.y}`
        );
        // console.log('Received data structure:', this.points);
        const data = [
            // X vs Y view
            {
                x: this.points.groundTruth.map(p => p.x),
                y: this.points.groundTruth.map(p => p.y),
                type: 'scatter',
                mode: 'lines',
                name: 'Ground Truth',
                line: {color: 'rgb(70, 70, 70)', width: 2, opacity: 0.3},
                hovertemplate: 'Ground Truth<br>%{text}<extra></extra>',
                text: getHoverText(this.points.groundTruth)
            },
            {
                x: this.points.predicted.map(p => p.x),
                y: this.points.predicted.map(p => p.y),
                type: 'scatter',
                mode: 'lines',
                name: 'Predicted',
                line: {color: '#2196F3', width: 3, dash: 'dash', opacity: 0.6},
                hovertemplate: 'Predicted<br>%{text}<extra></extra>',
                text: getHoverText(this.points.predicted)
            },
            {
                x: this.points.sampledPoints.filter(p => p.is_point).map(p => p.x),
                y: this.points.sampledPoints.filter(p => p.is_point).map(p => p.y),
                type: 'scatter',
                mode: 'markers',
                name: 'Samples',
                marker: {
                    size: 8,
                    color: this.points.sampledPoints.filter(p => p.is_point).map(p => p.color),
                    symbol: 'circle',
                    opacity: 0.7,
                    line: {color: 'white', width: 2}
                },
                hovertemplate: 'Samples<br>%{text}<extra></extra>',
                text: getHoverText(this.points.sampledPoints.filter(p => p.is_point))
            },

            // T vs X view
            {
                x: this.points.groundTruth.map(p => p.t),
                y: this.points.groundTruth.map(p => p.x),
                type: 'scatter',
                mode: 'lines',
                name: 'Ground Truth',
                line: {color: 'rgb(70, 70, 70)', width: 2, opacity: 0.3},
                visible: false
            },
            {
                x: this.points.predicted.map(p => p.t),
                y: this.points.predicted.map(p => p.x),
                type: 'scatter',
                mode: 'lines',
                name: 'Predicted',
                line: {color: '#2196F3', width: 3, dash: 'dash', opacity: 0.6},
                visible: false
            },
            {
                x: this.points.sampledPoints.filter(p => p.is_point).map(p => p.t),
                y: this.points.sampledPoints.filter(p => p.is_point).map(p => p.x),
                type: 'scatter',
                mode: 'markers',
                name: 'Samples',
                marker: {
                    size: 8,
                    color: this.points.sampledPoints.filter(p => p.is_point).map(p => p.color),
                    symbol: 'circle',
                    opacity: 0.7,
                    line: {color: 'white', width: 2}
                },
                visible: false
            },

            // T vs Y view
            {
                x: this.points.groundTruth.map(p => p.t),
                y: this.points.groundTruth.map(p => p.y),
                type: 'scatter',
                mode: 'lines',
                name: 'Ground Truth',
                line: {color: 'rgb(70, 70, 70)', width: 2, opacity: 0.3},
                visible: false
            },
            {
                x: this.points.predicted.map(p => p.t),
                y: this.points.predicted.map(p => p.y),
                type: 'scatter',
                mode: 'lines',
                name: 'Predicted',
                line: {color: '#2196F3', width: 3, dash: 'dash', opacity: 0.6},
                visible: false
            },
            {
                x: this.points.sampledPoints.filter(p => p.is_point).map(p => p.t),
                y: this.points.sampledPoints.filter(p => p.is_point).map(p => p.y),
                type: 'scatter',
                mode: 'markers',
                name: 'Samples',
                marker: {
                    size: 8,
                    color: this.points.sampledPoints.filter(p => p.is_point).map(p => p.color),
                    symbol: 'circle',
                    opacity: 0.7,
                    line: {color: 'white', width: 2}
                },
                visible: false
            }
        ];

        const currentData = document.getElementById('plot').data;
        const visibleState = currentData.map(trace => trace.visible);
        Plotly.react('plot', data, this.baseLayout);
        Plotly.update('plot', {visible: visibleState});
    }

    async handlePreviewClick() {
        if (!this.isPreviewMode) {
            // Enter preview mode
            this.isPreviewMode = true;
            this.previewButton.textContent = 'Run';
            this.resetButton.disabled = false;
            this.logStatus(`Regression parameters: K=${this.params.kernel.value}, bw_X=${this.params.bandwidthX.value}, bw_Y=${this.params.bandwidthY.value}.`);
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
                        'bandwidth_x': this.params.bandwidthX.value,
                        'bandwidth_y': this.params.bandwidthY.value,
                        'kernel': this.params.kernel.value})
                });
    
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
    
                const resp = await response.json()
                this.points = resp.points;
                this.updatePlot();
                this.logStatus(`Curves fitted and plotted. MSE = ${resp.mse}`);
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