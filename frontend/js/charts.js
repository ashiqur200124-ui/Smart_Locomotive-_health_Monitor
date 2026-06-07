// Chart visualization functions

// Draw risk distribution chart
function drawRiskChart() {
    const riskCategories = ['Low Risk', 'Medium Risk', 'High Risk', 'Critical'];
    const riskCounts = [5, 3, 2, 1];
    const colors = ['#27ae60', '#f39c12', '#e67e22', '#e74c3c'];
    
    const trace = {
        x: riskCategories,
        y: riskCounts,
        type: 'bar',
        marker: {
            color: colors
        }
    };
    
    const layout = {
        title: '',
        xaxis: { title: 'Risk Category' },
        yaxis: { title: 'Number of Locomotives' },
        responsive: true,
        plot_bgcolor: '#f9f9f9',
        paper_bgcolor: 'white',
        margin: { t: 20 }
    };
    
    Plotly.newPlot('riskChart', [trace], layout, { responsive: true });
}

// Draw health gauge
function drawHealthGauge() {
    const gaugeTrace = {
        type: "indicator",
        mode: "gauge+number+delta",
        value: 82,
        title: { text: "System Health" },
        delta: { reference: 80 },
        gauge: {
            axis: { range: [0, 100] },
            bar: { color: "#3498db" },
            steps: [
                { range: [0, 25], color: "#ffebee" },
                { range: [25, 50], color: "#fff3e0" },
                { range: [50, 75], color: "#f0f4ff" },
                { range: [75, 100], color: "#e8f5e9" }
            ],
            threshold: {
                line: { color: "red", width: 4 },
                thickness: 0.75,
                value: 90
            }
        }
    };
    
    const layout = {
        margin: { t: 20, r: 25, l: 25, b: 20 },
        paper_bgcolor: "white",
        font: { color: "#2c3e50" }
    };
    
    Plotly.newPlot('healthGauge', [gaugeTrace], layout, { responsive: true });
}

// Draw component risk chart
function drawComponentRiskChart(componentRisks) {
    const components = Object.keys(componentRisks);
    const risks = Object.values(componentRisks);
    
    // Determine colors based on risk level
    const colors = risks.map(risk => {
        if (risk > 75) return '#e74c3c';
        if (risk > 50) return '#f39c12';
        if (risk > 25) return '#f39c12';
        return '#27ae60';
    });
    
    const trace = {
        x: risks,
        y: components,
        type: 'bar',
        orientation: 'h',
        marker: { color: colors }
    };
    
    const layout = {
        title: '',
        xaxis: { title: 'Risk Score (%)', range: [0, 100] },
        responsive: true,
        plot_bgcolor: '#f9f9f9',
        paper_bgcolor: 'white',
        margin: { l: 100, t: 20 }
    };
    
    Plotly.newPlot('componentRiskChart', [trace], layout, { responsive: true });
}

// Draw failure probability chart
function drawFailureProbabilityChart(predictions) {
    const components = Object.keys(predictions);
    const probabilities = components.map(comp => predictions[comp].probability * 100);
    
    const trace = {
        x: components,
        y: probabilities,
        type: 'scatter',
        mode: 'markers+lines',
        marker: {
            size: 10,
            color: probabilities.map(p => p > 75 ? '#e74c3c' : p > 50 ? '#f39c12' : '#27ae60')
        },
        line: { color: '#3498db', width: 2 }
    };
    
    const layout = {
        title: '',
        xaxis: { title: 'Component' },
        yaxis: { title: 'Failure Probability (%)', range: [0, 100] },
        responsive: true,
        plot_bgcolor: '#f9f9f9',
        paper_bgcolor: 'white',
        margin: { t: 20 }
    };
    
    Plotly.newPlot('failureProbChart', [trace], layout, { responsive: true });
}

// Create time series chart for health monitoring
function drawHealthTrendChart(historicalData) {
    if (!historicalData || historicalData.length === 0) return;
    
    const timestamps = historicalData.map(d => new Date(d.timestamp).toLocaleTimeString());
    const healthScores = historicalData.map(d => d.health_score);
    const riskScores = historicalData.map(d => d.risk_score);
    
    const trace1 = {
        x: timestamps,
        y: healthScores,
        name: 'Health Score',
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: '#27ae60', width: 2 }
    };
    
    const trace2 = {
        x: timestamps,
        y: riskScores,
        name: 'Risk Score',
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: '#e74c3c', width: 2 }
    };
    
    const layout = {
        title: 'Health & Risk Score Trends',
        xaxis: { title: 'Time' },
        yaxis: { title: 'Score (%)' },
        hovermode: 'x unified',
        responsive: true
    };
    
    Plotly.newPlot('healthTrendChart', [trace1, trace2], layout, { responsive: true });
}

// Create alert timeline chart
function createAlertTimelineChart(alerts) {
    const alertTypes = {};
    
    alerts.forEach(alert => {
        if (!alertTypes[alert.alert_type]) {
            alertTypes[alert.alert_type] = 0;
        }
        alertTypes[alert.alert_type]++;
    });
    
    const types = Object.keys(alertTypes);
    const counts = Object.values(alertTypes);
    
    const trace = {
        labels: types,
        values: counts,
        type: 'pie',
        marker: {
            colors: ['#e74c3c', '#f39c12', '#3498db', '#27ae60', '#9b59b6']
        }
    };
    
    const layout = {
        title: 'Alert Distribution by Type',
        responsive: true
    };
    
    // Plotly.newPlot('alertChart', [trace], layout, { responsive: true });
}

// Create comparison chart for multiple locomotives
function createComparisonChart(locomotivesData) {
    if (!locomotivesData || locomotivesData.length === 0) return;
    
    const locoIds = locomotivesData.map(l => l.loco_id);
    const healthScores = locomotivesData.map(l => l.health_score || 100);
    const riskScores = locomotivesData.map(l => l.current_risk || 0);
    
    const trace1 = {
        x: locoIds,
        y: healthScores,
        name: 'Health Score',
        type: 'bar',
        marker: { color: '#27ae60' }
    };
    
    const trace2 = {
        x: locoIds,
        y: riskScores,
        name: 'Risk Score',
        type: 'bar',
        marker: { color: '#e74c3c' }
    };
    
    const layout = {
        title: 'Fleet Health & Risk Comparison',
        xaxis: { title: 'Locomotive' },
        yaxis: { title: 'Score (%)' },
        barmode: 'group',
        responsive: true
    };
    
    // Plotly.newPlot('comparisonChart', [trace1, trace2], layout, { responsive: true });
}

// Create maintenance schedule Gantt chart
function createMaintenanceGantt(maintenanceSchedule) {
    if (!maintenanceSchedule || maintenanceSchedule.length === 0) return;
    
    const data = maintenanceSchedule.map((item, index) => ({
        Task: item.component,
        Start: new Date(),
        Finish: new Date(new Date().getTime() + item.estimated_hours * 3600000),
        Resource: item.priority
    }));
    
    // Gantt chart implementation would require additional library
    console.log('Maintenance schedule data prepared:', data);
}

// Export chart as PNG
function exportChart(elementId, fileName) {
    Plotly.downloadImage(elementId, {
        format: 'png',
        width: 1200,
        height: 600,
        filename: fileName
    });
}

// Update all dashboard charts
function updateAllCharts() {
    drawRiskChart();
    drawHealthGauge();
}

console.log('Charts module loaded');
