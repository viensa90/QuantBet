// QuantBet Dashboard - JavaScript

const API_BASE = '/api';

// Estado
let snapshots = [];
let opportunities = [];
let status = {};

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    loadStatus();
    loadSnapshots();
    loadOpportunities();
    
    // Actualizar cada 30 segundos
    setInterval(() => {
        loadStatus();
        loadSnapshots();
        loadOpportunities();
    }, 30000);
});

// Cargar estado del sistema
async function loadStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        status = await response.json();
        
        document.getElementById('version').textContent = `v${status.version}`;
        document.getElementById('total-snapshots').textContent = status.total_snapshots;
        document.getElementById('total-decisions').textContent = status.total_decisions;
        document.getElementById('connector-type').textContent = status.connector_type.toUpperCase();
        
        const bankroll = status.bankroll || 0;
        document.getElementById('bankroll').textContent = `Bankroll: ${status.currency}${bankroll.toFixed(2)}`;
    } catch (error) {
        console.error('Error cargando estado:', error);
    }
}

// Cargar snapshots
async function loadSnapshots() {
    try {
        const response = await fetch(`${API_BASE}/snapshots?limit=20`);
        snapshots = await response.json();
        
        const tbody = document.getElementById('snapshots-body');
        
        if (snapshots.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No hay snapshots disponibles</td></tr>';
            return;
        }
        
        tbody.innerHTML = snapshots.map(s => `
            <tr>
                <td><strong>${s.event_name}</strong></td>
                <td>${s.source}</td>
                <td class="odds-${getOddsClass(s.odds.Local)}">${s.odds.Local || '-'}</td>
                <td class="odds-${getOddsClass(s.odds.Empate)}">${s.odds.Empate || '-'}</td>
                <td class="odds-${getOddsClass(s.odds.Visitante)}">${s.odds.Visitante || '-'}</td>
                <td>${formatDate(s.timestamp)}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error cargando snapshots:', error);
        document.getElementById('snapshots-body').innerHTML = 
            '<tr><td colspan="6" class="loading">Error cargando snapshots</td></tr>';
    }
}

// Cargar oportunidades
async function loadOpportunities() {
    try {
        const response = await fetch(`${API_BASE}/opportunities?limit=20`);
        opportunities = await response.json();
        
        const tbody = document.getElementById('opportunities-body');
        
        // Filtrar solo las aceptadas para el contador
        const accepted = opportunities.filter(o => o.accepted);
        document.getElementById('opportunities-count').textContent = accepted.length;
        
        if (opportunities.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No hay oportunidades disponibles</td></tr>';
            return;
        }
        
        tbody.innerHTML = opportunities.map(o => `
            <tr>
                <td><strong>${o.event_id}</strong></td>
                <td>${o.strategy}</td>
                <td>${o.score ? (o.score * 100).toFixed(2) + '%' : '-'}</td>
                <td>${o.stake ? '€' + o.stake.toFixed(2) : '-'}</td>
                <td class="${o.accepted ? 'accepted' : 'rejected'}">
                    ${o.accepted ? '✅ Aceptada' : '❌ Rechazada'}
                </td>
                <td>${formatDate(o.timestamp)}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error cargando oportunidades:', error);
        document.getElementById('opportunities-body').innerHTML = 
            '<tr><td colspan="6" class="loading">Error cargando oportunidades</td></tr>';
    }
}

// Helper: Clase CSS para cuotas
function getOddsClass(odds) {
    if (!odds) return 'low';
    if (odds >= 3.0) return 'high';
    if (odds >= 2.0) return 'medium';
    return 'low';
}

// Helper: Formatear fecha
function formatDate(isoDate) {
    const date = new Date(isoDate);
    return date.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}