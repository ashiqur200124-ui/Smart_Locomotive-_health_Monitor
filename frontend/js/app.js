// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// Locomotives data
let locomotivesData = [];
let selectedLoco = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    setupNavigationListener();
    updateTimestamp();
    loadLocomotivesData();
    initializeDashboard();
    
    // Update timestamp every second
    setInterval(updateTimestamp, 1000);
});

// Update timestamp
function updateTimestamp() {
    const now = new Date();
    document.getElementById('timestamp').textContent = now.toLocaleTimeString();
}

// Setup navigation
function setupNavigationListener() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links and sections
            navLinks.forEach(l => l.classList.remove('active'));
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            
            // Add active class to clicked link and corresponding section
            this.classList.add('active');
            const sectionId = this.dataset.section;
            const section = document.getElementById(sectionId);
            if (section) {
                section.classList.add('active');
            }
            if (sectionId === 'map-section' && typeof refreshMap === 'function') {
                refreshMap();
            }
        });
    });
}

// Load locomotives data
async function loadLocomotivesData() {
    try {
        const response = await fetch(`${API_BASE_URL}/locomotives`);
        const data = await response.json();
        
        if (data.status === 'success') {
            locomotivesData = data.locomotives;
            updateDashboardMetrics();
            populateLocomotivesTable();
        }
    } catch (error) {
        console.error('Error loading locomotives:', error);
    }
}

// Initialize dashboard
function initializeDashboard() {
    updateDashboardMetrics();
    drawRiskChart();
    drawHealthGauge();
}

// Update dashboard metrics
function updateDashboardMetrics() {
    const totalLocos = locomotivesData.length;
    const avgHealth = locomotivesData.length > 0 
        ? (locomotivesData.reduce((sum, l) => sum + (l.health_score || 100), 0) / locomotivesData.length).toFixed(0)
        : 100;
    const criticalCount = locomotivesData.filter(l => l.current_risk > 75).length;
    
    document.getElementById('activeLoco').textContent = totalLocos;
    document.getElementById('avgHealth').textContent = avgHealth + '%';
    document.getElementById('criticalAlerts').textContent = criticalCount;
    const maintenanceDueCount = Math.ceil(totalLocos * 0.1);
    document.getElementById('maintenanceDue').textContent = maintenanceDueCount;

    renderMaintenanceSchedule();
}

// Render maintenance schedule cards in Maintenance section
function renderMaintenanceSchedule() {
    const container = document.getElementById('maintenanceContainer');
    container.innerHTML = '';

    if (!locomotivesData || locomotivesData.length === 0) {
        container.innerHTML = '<p>No locomotives available for maintenance scheduling.</p>';
        return;
    }

    // Build schedule based on oldest maintenance date and high risk locomotives
    const sortedByDue = locomotivesData
        .map(loco => {
            const lastMaint = new Date(loco.last_maintenance);
            const daysSince = Math.floor((new Date() - lastMaint) / (1000 * 60 * 60 * 24));
            return { ...loco, daysSince }; 
        })
        .sort((a, b) => b.daysSince - a.daysSince || b.current_risk - a.current_risk)
        .slice(0, 8);

    sortedByDue.forEach(loco => {
        const card = document.createElement('div');
        card.className = 'maintenance-item';
        card.innerHTML = `
            <h3>${loco.loco_id} - ${loco.name}</h3>
            <p><strong>Route:</strong> ${loco.route}</p>
            <p><strong>Status:</strong> ${loco.status}</p>
            <p><strong>Last maintenance:</strong> ${loco.last_maintenance} (${loco.daysSince} days ago)</p>
            <p><strong>Current risk:</strong> ${loco.current_risk}%</p>
            <p><strong>Health score:</strong> ${loco.health_score.toFixed(0)}%</p>
        `;
        container.appendChild(card);
    });
}

// Populate locomotives table
function populateLocomotivesTable() {
    const tbody = document.getElementById('locosTableBody');
    tbody.innerHTML = '';
    
    locomotivesData.forEach(loco => {
        const risk = loco.current_risk || 0;
        const health = loco.health_score || 100;
        const riskClass = risk > 75 ? 'risk-high' : risk > 50 ? 'risk-medium' : 'risk-low';
        const riskText = risk > 75 ? 'HIGH' : risk > 50 ? 'MEDIUM' : 'LOW';
        
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><strong>${loco.loco_id}</strong></td>
            <td>${loco.name}</td>
            <td>${loco.type}</td>
            <td>${loco.route}</td>
            <td>${parseInt(loco.mileage).toLocaleString()} km</td>
            <td>
                <div class="health-bar">
                    <div class="health-fill" style="width: ${health}%"></div>
                </div>
                <small>${health.toFixed(0)}%</small>
            </td>
            <td><span class="status-badge status-${loco.status.toLowerCase()}">${loco.status}</span></td>
            <td><span class="${riskClass}">${riskText}</span></td>
            <td>
                <button class="btn btn-small btn-primary" onclick="viewLocomotiveDetails('${loco.loco_id}')">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// View locomotive details
function viewLocomotiveDetails(locoId) {
    const loco = locomotivesData.find(l => l.loco_id === locoId);
    if (!loco) return;
    
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
        <h3>Locomotive Details: ${loco.name}</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.5rem;">
            <div>
                <p><strong>ID:</strong> ${loco.loco_id}</p>
                <p><strong>Type:</strong> ${loco.type}</p>
                <p><strong>Route:</strong> ${loco.route}</p>
                <p><strong>Owner:</strong> ${loco.owner}</p>
            </div>
            <div>
                <p><strong>Mileage:</strong> ${parseInt(loco.mileage).toLocaleString()} km</p>
                <p><strong>Status:</strong> <span class="status-badge status-${loco.status.toLowerCase()}">${loco.status}</span></p>
                <p><strong>Last Maintenance:</strong> ${loco.last_maintenance}</p>
                <p><strong>Health Score:</strong> ${(loco.health_score || 100).toFixed(0)}%</p>
            </div>
        </div>
        <button class="btn btn-primary" style="margin-top: 1.5rem;" onclick="analyzeLocoFromModal('${loco.loco_id}')">
            Analyze Health
        </button>
    `;
    
    document.getElementById('locoModal').style.display = 'block';
}

// Close modal
function closeModal() {
    document.getElementById('locoModal').style.display = 'none';
}

// Analyze locomotive from modal
function analyzeLocoFromModal(locoId) {
    document.getElementById('analyzeLocoId').value = locoId;
    document.getElementById('analyzeLocoId').dispatchEvent(new Event('change'));
    closeModal();
};

// Perform analysis
async function performAnalysis() {
    const locoId = document.getElementById('analyzeLocoId').value;
    const sensorData = {
        temperature: parseFloat(document.getElementById('tempInput').value),
        vibration: parseFloat(document.getElementById('vibrationInput').value),
        pressure: parseFloat(document.getElementById('pressureInput').value),
        oil_quality: parseFloat(document.getElementById('oilQualityInput').value),
        mileage: parseFloat(document.getElementById('mileageInput').value),
        latitude: parseFloat(document.getElementById('latInput').value),
        longitude: parseFloat(document.getElementById('lonInput').value)
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/health/${locoId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(sensorData)
        });
        
        const data = await response.json();
        displayAnalysisResults(data);
    } catch (error) {
        console.error('Analysis error:', error);
        alert('Error performing analysis');
    }
}

// Display analysis results
function displayAnalysisResults(data) {
    const resultsDiv = document.getElementById('analysisResults');
    
    if (data.status === 'success') {
        // Update result cards
        document.getElementById('riskScoreResult').textContent = data.risk_analysis.risk_score;
        document.getElementById('riskCategoryResult').textContent = data.risk_analysis.risk_category;
        document.getElementById('healthScoreResult').textContent = data.health_status.health_score.toFixed(1) + '%';
        document.getElementById('reliabilityResult').textContent = data.health_status.predicted_reliability.toFixed(1) + '%';
        
        // Update recommendations
        const recList = document.getElementById('recommendationsList');
        recList.innerHTML = '';
        data.risk_analysis.recommendations.forEach(rec => {
            const li = document.createElement('li');
            li.textContent = rec;
            recList.appendChild(li);
        });
        
        // Draw charts
        drawComponentRiskChart(data.risk_analysis.component_risks);
        drawFailureProbabilityChart(data.failure_predictions);
        
        // Show results
        resultsDiv.style.display = 'block';
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }
}

// Filter alerts
function filterAlerts() {
    const severity = document.getElementById('alertSeverityFilter').value;
    const alertBoxes = document.querySelectorAll('.alert-box');
    
    alertBoxes.forEach(box => {
        if (!severity || box.className.includes(severity.toLowerCase())) {
            box.style.display = 'block';
        } else {
            box.style.display = 'none';
        }
    });
}

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('locoModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// Search and filter functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchLocos');
    const [statusFilter, queryValue] = [document.getElementById('statusFilter'), null];
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterTable();
        });
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            filterTable();
        });
    }
});

function filterTable() {
    const searchValue = document.getElementById('searchLocos').value.toLowerCase();
    const statusValue = document.getElementById('statusFilter').value;
    
    const rows = document.querySelectorAll('#locosTableBody tr');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        let searchMatch = true;
        let statusMatch = true;
        
        if (searchValue) {
            searchMatch = Array.from(cells).slice(0, 4).some(cell => 
                cell.textContent.toLowerCase().includes(searchValue)
            );
        }
        
        if (statusValue) {
            statusMatch = cells[6].textContent.includes(statusValue);
        }
        
        row.style.display = searchMatch && statusMatch ? '' : 'none';
    });
}

console.log('App initialized successfully');
