// Main JavaScript for Ethical Hacking Portal

document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let currentSimulationId = null;
    let statusUpdateInterval = null;
    let attackDistributionChart = null;
    
    // DOM elements
    const attackForm = document.getElementById('attack-form');
    const startAttackBtn = document.getElementById('start-attack-btn');
    const stopAttackBtn = document.getElementById('stop-attack-btn');
    const statusContainer = document.getElementById('status-container');
    const statusPlaceholder = document.getElementById('status-placeholder');
    const recentLogsCard = document.getElementById('recent-logs-card');
    const recentLogs = document.getElementById('recent-logs');
    const attackDetailsCard = document.getElementById('attack-details-card');
    const attackDetailsContent = document.getElementById('attack-details-content');
    const attackTypesContainer = document.getElementById('attack-types-container');
    const datasetStatsContainer = document.getElementById('dataset-stats-container');
    
    // Status elements
    const statusProgress = document.getElementById('status-progress');
    const statusText = document.getElementById('status-text');
    const requestsSent = document.getElementById('requests-sent');
    const requestsBlocked = document.getElementById('requests-blocked');
    const blockRate = document.getElementById('block-rate');
    const duration = document.getElementById('duration');
    
    // Load attack types and dataset stats
    loadAttackTypes();
    loadDatasetStats();
    
    // Event listeners
    if (attackForm) {
        attackForm.addEventListener('submit', startAttack);
    }
    
    if (stopAttackBtn) {
        stopAttackBtn.addEventListener('click', stopAttack);
    }
    
    // Functions
    function startAttack(e) {
        e.preventDefault();
        
        // Get form values
        const targetUrl = document.getElementById('target-url').value;
        const attackType = document.getElementById('attack-type').value;
        const intensity = document.getElementById('attack-intensity').value;
        
        // Validate form
        if (!targetUrl || !attackType) {
            alert('Please fill in all required fields');
            return;
        }
        
        // Disable form and show stop button
        toggleFormState(true);
        
        // Show status container
        statusContainer.classList.remove('d-none');
        statusPlaceholder.classList.add('d-none');
        recentLogsCard.classList.remove('d-none');
        
        // Reset status
        statusProgress.style.width = '0%';
        statusText.textContent = 'Starting simulation...';
        requestsSent.textContent = '0';
        requestsBlocked.textContent = '0';
        blockRate.textContent = '0%';
        duration.textContent = '00:00';
        recentLogs.innerHTML = '';
        
        // Send request to start attack
        fetch('/simulate_attack', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                'target_url': targetUrl,
                'attack_type': attackType,
                'intensity': intensity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                toggleFormState(false);
                return;
            }
            
            // Store simulation ID
            currentSimulationId = data.simulation_id;
            
            // Update status
            statusText.textContent = data.message;
            
            // Start status updates
            startStatusUpdates();
            
            // Load attack details
            loadAttackDetails(attackType);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while starting the simulation');
            toggleFormState(false);
        });
    }
    
    function stopAttack() {
        if (!currentSimulationId) return;
        
        fetch(`/stop_simulation/${currentSimulationId}`)
            .then(response => response.json())
            .then(data => {
                statusText.textContent = data.message || 'Simulation stopped';
                clearInterval(statusUpdateInterval);
                toggleFormState(false);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while stopping the simulation');
            });
    }
    
    function startStatusUpdates() {
        // Clear any existing interval
        if (statusUpdateInterval) {
            clearInterval(statusUpdateInterval);
        }
        
        // Start new interval
        statusUpdateInterval = setInterval(() => {
            if (!currentSimulationId) return;
            
            fetch(`/simulation_status/${currentSimulationId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error('Error:', data.error);
                        clearInterval(statusUpdateInterval);
                        return;
                    }
                    
                    // Update status
                    updateStatus(data);
                    
                    // Check if simulation is complete
                    if (data.status === 'completed' || data.status === 'stopped' || data.status === 'error') {
                        clearInterval(statusUpdateInterval);
                        toggleFormState(false);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    clearInterval(statusUpdateInterval);
                });
        }, 1000);
    }
    
    function updateStatus(data) {
        // Update progress
        let progressPercent = 0;
        if (data.status === 'running') {
            progressPercent = Math.min(Math.floor(data.requests_sent / 50 * 100), 90);
        } else if (data.status === 'completed') {
            progressPercent = 100;
        } else if (data.status === 'stopped') {
            progressPercent = 100;
            statusProgress.classList.remove('bg-success');
            statusProgress.classList.add('bg-warning');
        } else if (data.status === 'error') {
            progressPercent = 100;
            statusProgress.classList.remove('bg-success');
            statusProgress.classList.add('bg-danger');
        }
        
        statusProgress.style.width = `${progressPercent}%`;
        
        // Update text
        statusText.textContent = `Status: ${data.status}`;
        requestsSent.textContent = data.requests_sent;
        requestsBlocked.textContent = data.requests_blocked;
        
        // Calculate block rate
        const rate = data.requests_sent > 0 ? Math.round((data.requests_blocked / data.requests_sent) * 100) : 0;
        blockRate.textContent = `${rate}%`;
        
        // Update duration
        duration.textContent = data.duration;
        
        // Update logs
        updateLogs(data.recent_logs);
    }
    
    function updateLogs(logs) {
        if (!logs || logs.length === 0) return;
        
        // Clear logs if there are too many
        if (recentLogs.children.length > 50) {
            recentLogs.innerHTML = '';
        }
        
        // Add new logs
        logs.forEach(log => {
            // Check if log already exists
            const logId = `log-${log.timestamp.replace(/[^a-zA-Z0-9]/g, '')}`;
            if (document.getElementById(logId)) return;
            
            const logItem = document.createElement('li');
            logItem.id = logId;
            logItem.className = 'list-group-item log-item blocked'; // Always add 'blocked' class
            
            // Always set status badge to blocked
            const statusBadge = '<span class="badge bg-danger">Blocked</span>';
            
            logItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <span>${log.url ? log.url.split('/').pop() || '/' : 'N/A'}</span>
                    ${statusBadge}
                </div>
                <div class="log-timestamp">${log.timestamp}</div>
            `;
            
            recentLogs.prepend(logItem);
        });
    }
    
    function toggleFormState(disabled) {
        const formElements = attackForm.elements;
        for (let i = 0; i < formElements.length; i++) {
            formElements[i].disabled = disabled;
        }
        
        if (disabled) {
            startAttackBtn.classList.add('d-none');
            stopAttackBtn.classList.remove('d-none');
        } else {
            startAttackBtn.classList.remove('d-none');
            stopAttackBtn.classList.add('d-none');
        }
    }
    
    function loadAttackTypes() {
        if (!attackTypesContainer) return;
        
        fetch('/dataset_stats')
            .then(response => response.json())
            .then(data => {
                const attackDistribution = data.attack_distribution || {};
                const attackTypes = Object.keys(attackDistribution);
                
                // Clear container
                attackTypesContainer.innerHTML = '';
                
                // Add attack types
                attackTypes.forEach(attackType => {
                    const count = attackDistribution[attackType];
                    const card = createAttackTypeCard(attackType, count);
                    attackTypesContainer.appendChild(card);
                });
                
                // Create attack distribution chart
                createAttackDistributionChart(attackDistribution);
            })
            .catch(error => {
                console.error('Error:', error);
                attackTypesContainer.innerHTML = '<p class="text-center text-danger">Error loading attack types</p>';
            });
    }
    
    function createAttackTypeCard(attackType, count) {
        const col = document.createElement('div');
        col.className = 'col-md-3 col-sm-6 mb-4';
        
        const iconClass = getAttackTypeIcon(attackType);
        const colorClass = `attack-${attackType.toLowerCase()}`;
        
        col.innerHTML = `
            <div class="card bg-black text-light attack-type-card" data-attack="${attackType}">
                <div class="card-body text-center">
                    <div class="attack-type-icon ${colorClass}">
                        <i class="${iconClass}"></i>
                    </div>
                    <h5>${attackType}</h5>
                    <p class="mb-0">${count} samples</p>
                </div>
            </div>
        `;
        
        // Add click event
        col.querySelector('.attack-type-card').addEventListener('click', () => {
            loadAttackDetails(attackType);
        });
        
        return col;
    }
    
    function getAttackTypeIcon(attackType) {
        const icons = {
            'neptune': 'fas fa-water',
            'smurf': 'fas fa-laugh-squint',
            'portsweep': 'fas fa-broom',
            'satan': 'fas fa-ghost',
            'ipsweep': 'fas fa-search',
            'nmap': 'fas fa-map',
            'normal': 'fas fa-check-circle',
            'back': 'fas fa-arrow-left',
            'teardrop': 'fas fa-tint',
            'pod': 'fas fa-bomb',
            'warezclient': 'fas fa-download'
        };
        
        return icons[attackType.toLowerCase()] || 'fas fa-bug';
    }
    
    function loadAttackDetails(attackType) {
        if (!attackDetailsCard || !attackDetailsContent) return;
        
        fetch(`/attack_details/${attackType}`)
            .then(response => response.json())
            .then(data => {
                // Show card
                attackDetailsCard.classList.remove('d-none');
                
                // Update content
                attackDetailsContent.innerHTML = `
                    <h5>${data.name}</h5>
                    <p>${data.description}</p>
                    <p><strong>Samples in dataset:</strong> ${data.count}</p>
                    <h6>Key Features:</h6>
                    <ul>
                        ${getFeaturesList(data.features)}
                    </ul>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
                attackDetailsContent.innerHTML = '<p class="text-center text-danger">Error loading attack details</p>';
            });
    }
    
    function getFeaturesList(features) {
        if (!features) return '';
        
        const keyFeatures = [
            'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
            'count', 'srv_count', 'serror_rate', 'rerror_rate'
        ];
        
        let html = '';
        keyFeatures.forEach(feature => {
            if (features[feature] !== undefined) {
                let value = features[feature];
                if (typeof value === 'number') {
                    value = value.toFixed(2);
                }
                html += `<li><strong>${feature}:</strong> ${value}</li>`;
            }
        });
        
        return html;
    }
    
    function loadDatasetStats() {
        if (!datasetStatsContainer) return;
        
        fetch('/dataset_stats')
            .then(response => response.json())
            .then(data => {
                // Update content
                datasetStatsContainer.innerHTML = `
                    <div class="row">
                        <div class="col-md-4">
                            <div class="dataset-stat">
                                <div class="dataset-stat-value">${data.total_records.toLocaleString()}</div>
                                <div>Total Records</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="dataset-stat">
                                <div class="dataset-stat-value">${Object.keys(data.attack_distribution || {}).length}</div>
                                <div>Attack Types</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="dataset-stat">
                                <div class="dataset-stat-value">${Object.keys(data.protocol_distribution || {}).length}</div>
                                <div>Protocols</div>
                            </div>
                        </div>
                    </div>
                `;
            })
            .catch(error => {
                console.error('Error:', error);
                datasetStatsContainer.innerHTML = '<p class="text-center text-danger">Error loading dataset statistics</p>';
            });
    }
    
    function createAttackDistributionChart(attackDistribution) {
        const chartCanvas = document.getElementById('attack-distribution-chart');
        if (!chartCanvas) return;
        
        // Prepare data
        const labels = Object.keys(attackDistribution);
        const data = labels.map(label => attackDistribution[label]);
        
        // Generate colors
        const colors = labels.map(label => getAttackTypeColor(label));
        
        // Create chart
        if (attackDistributionChart) {
            attackDistributionChart.destroy();
        }
        
        attackDistributionChart = new Chart(chartCanvas, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#fff'
                        }
                    }
                }
            }
        });
    }
    
    function getAttackTypeColor(attackType) {
        const colors = {
            'neptune': '#0dcaf0',
            'smurf': '#6f42c1',
            'portsweep': '#fd7e14',
            'satan': '#dc3545',
            'ipsweep': '#20c997',
            'nmap': '#0d6efd',
            'normal': '#198754',
            'back': '#6c757d',
            'teardrop': '#ffc107',
            'pod': '#d63384',
            'warezclient': '#adb5bd'
        };
        
        return colors[attackType.toLowerCase()] || '#6c757d';
    }
});

