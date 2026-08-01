/**
 * QuantBet Dashboard - JavaScript con gráficos en tiempo real
 * Versión: 0.3.3
 */

// Configuración
const API_BASE = '/api/v1';
const REFRESH_INTERVAL = parseInt(document.querySelector('meta[name="refresh-interval"]')?.content || '5000');

// Instancias de gráficos
let strategyChart = null;
let trendChart = null;

/**
 * Inicializar gráficos
 */
function initCharts() {
    // Gráfico de estrategias (Doughnut)
    const strategyCtx = document.getElementById('strategyChart').getContext('2d');
    strategyChart = new Chart(strategyCtx, {
        type: 'doughnut',
        data: {
            labels: ['Arbitraje', 'Value Betting', 'Dutching'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(88, 166, 255, 0.8)',
                    'rgba(63, 185, 80, 0.8)',
                    'rgba(188, 140, 255, 0.8)'
                ],
                borderColor: [
                    'rgba(88, 166, 255, 1)',
                    'rgba(63, 185, 80, 1)',
                    'rgba(188, 140, 255, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f0f6fc',
                        padding: 12,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            },
            cutout: '60%'
        }
    });

    // Gráfico de tendencia (Line)
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Arbitraje',
                    data: [],
                    borderColor: 'rgba(88, 166, 255, 1)',
                    backgroundColor: 'rgba(88, 166, 255, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Value Betting',
                    data: [],
                    borderColor: 'rgba(63, 185, 80, 1)',
                    backgroundColor: 'rgba(63, 185, 80, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Dutching',
                    data: [],
                    borderColor: 'rgba(188, 140, 255, 1)',
                    backgroundColor: 'rgba(188, 140, 255, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: '#f0f6fc',
                        padding: 12,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#8b949e',
                        maxTicksLimit: 8
                    },
                    grid: {
                        color: 'rgba(48, 54, 61, 0.5)'
                    }
                },
                y: {
                    ticks: {
                        color: '#8b949e'
                    },
                    grid: {
                        color: 'rgba(48, 54, 61, 0.5)'
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Actualizar métricas
 */
async function updateMetrics() {
    try {
        const response = await fetch(`${API_BASE}/metrics`);
        const data = await response.json();
        
        // Actualizar tarjetas
        document.getElementById('total-opportunities').textContent = data.total_opportunities || 0;
        document.getElementById('active-markets').textContent = data.active_markets || 0;
        document.getElementById('arbitrage-count').textContent = data.strategies?.arbitrage || 0;
        document.getElementById('value-count').textContent = data.strategies?.value_betting || 0;
        
        // Actualizar gráfico de estrategias
        if (strategyChart) {
            strategyChart.data.datasets[0].data = [
                data.strategies?.arbitrage || 0,
                data.strategies?.value_betting || 0,
                data.strategies?.dutching || 0
            ];
            strategyChart.update();
        }
        
        // Actualizar timestamp
        const lastUpdate = document.getElementById('last-update');
        if (data.last_update) {
            const date = new Date(data.last_update);
            lastUpdate.textContent = `Actualizado: ${date.toLocaleTimeString()}`;
        }
    } catch (error) {
        console.error('Error actualizando métricas:', error);
    }
}

/**
 * Actualizar oportunidades
 */
async function updateOpportunities() {
    try {
        const response = await fetch(`${API_BASE}/opportunities?limit=10`);
        const data = await response.json();
        
        const tableBody = document.getElementById('opportunities-table');
        
        if (!data || data.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5">No hay oportunidades disponibles</td></tr>';
            return;
        }
        
        tableBody.innerHTML = data.map(opp => `
            <tr>
                <td><strong>${opp.event || 'Evento desconocido'}</strong></td>
                <td>${opp.sport || '-'}</td>
                <td>${opp.market_type || '-'}</td>
                <td><span class="badge badge-${opp.strategy}">${opp.strategy || 'desconocida'}</span></td>
                <td style="color: ${opp.profit_percent >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'}">
                    ${opp.profit_percent ? opp.profit_percent.toFixed(2) : '0.00'}%
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error actualizando oportunidades:', error);
    }
}

/**
 * Actualizar estado del sistema
 */
async function updateSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/system/status`);
        const data = await response.json();
        
        document.getElementById('db-status').textContent = 
            `${data.db_size_mb || 0} MB`;
        
        document.getElementById('connectors-status').textContent = 
            Object.entries(data.connectors || {})
                .map(([key, val]) => `${key}: ${val}`)
                .join(' | ');
        
        document.getElementById('models-status').textContent = 
            (data.models_loaded || []).join(', ');
    } catch (error) {
        console.error('Error actualizando estado del sistema:', error);
    }
}

/**
 * Actualizar tendencia (datos simulados para demo)
 */
function updateTrend() {
    // Para una demo real, esto vendría de un endpoint de tendencias
    // Por ahora, generamos datos aleatorios para mostrar el gráfico
    const now = new Date();
    const labels = [];
    const arbitrageData = [];
    const valueData = [];
    const dutchingData = [];
    
    for (let i = 0; i < 12; i++) {
        const date = new Date(now);
        date.setMinutes(date.getMinutes() - i * 5);
        labels.push(date.toLocaleTimeString());
        
        // Datos aleatorios para demo
        arbitrageData.push(Math.floor(Math.random() * 20) + 5);
        valueData.push(Math.floor(Math.random() * 25) + 10);
        dutchingData.push(Math.floor(Math.random() * 15) + 2);
    }
    
    if (trendChart) {
        trendChart.data.labels = labels.reverse();
        trendChart.data.datasets[0].data = arbitrageData.reverse();
        trendChart.data.datasets[1].data = valueData.reverse();
        trendChart.data.datasets[2].data = dutchingData.reverse();
        trendChart.update();
    }
}

/**
 * Actualizar todo
 */
async function updateDashboard() {
    await Promise.all([
        updateMetrics(),
        updateOpportunities(),
        updateSystemStatus()
    ]);
    updateTrend();
}

/**
 * Inicializar dashboard
 */
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar gráficos
    initCharts();
    
    // Primera actualización
    updateDashboard();
    
    // Actualizar periódicamente
    setInterval(updateDashboard, REFRESH_INTERVAL);
});