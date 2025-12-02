/**
 * NADAKKI AI - WordPress Integration
 * Conecta el panel WordPress con FastAPI (Render)
 * Archivo: nadakki-marketing-executor.js
 */

const NADAKKI_API = 'https://nadakki-ai-suite.onrender.com';

// 1. OBTENER LISTA DE AGENTES ACTUALIZADA
async function loadMarketingAgents() {
    try {
        console.log('🔄 Cargando agentes de marketing...');
        
        const response = await fetch(NADAKKI_API + '/api/v1/agents', {
            headers: {
                'X-Tenant-ID': getTenantID(),
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) throw new Error('Error al obtener agentes');
        
        const agents = await response.json();
        console.log('✅ Agentes cargados:', agents.length);
        
        updateAgentCounts(agents);
        return agents;
        
    } catch (error) {
        console.error('❌ Error:', error);
        showNotification('Error al cargar agentes', 'error');
    }
}

// 2. EJECUTAR AGENTE
async function executeAgent(agentName, inputData = {}) {
    try {
        console.log('🚀 Ejecutando agente: ' + agentName);
        
        const response = await fetch(
            NADAKKI_API + '/api/v1/agents/' + agentName,
            {
                method: 'POST',
                headers: {
                    'X-Tenant-ID': getTenantID(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    input: inputData,
                    timestamp: new Date().toISOString()
                })
            }
        );
        
        if (!response.ok) throw new Error('Error al ejecutar agente');
        
        const result = await response.json();
        console.log('✅ Resultado:', result);
        
        showResult(agentName, result);
        return result;
        
    } catch (error) {
        console.error('❌ Error:', error);
        showNotification('Error ejecutando ' + agentName, 'error');
    }
}

// 3. OBTENER ID DEL TENANT
function getTenantID() {
    const selector = document.querySelector('[data-tenant-id]');
    return selector ? selector.getAttribute('data-tenant-id') : 'default';
}

// 4. ACTUALIZAR CONTEOS DE AGENTES
function updateAgentCounts(agents) {
    const agentsByEcosystem = {};
    
    agents.forEach(agent => {
        const ecosystem = agent.ecosystem || 'Marketing';
        agentsByEcosystem[ecosystem] = (agentsByEcosystem[ecosystem] || 0) + 1;
    });
    
    Object.entries(agentsByEcosystem).forEach(([ecosystem, count]) => {
        const element = document.querySelector('[data-ecosystem="' + ecosystem + '"]');
        if (element) {
            element.textContent = count;
        }
    });
}

// 5. MOSTRAR RESULTADO EN MODAL
function showResult(agentName, result) {
    const modal = document.createElement('div');
    modal.className = 'nadakki-result-modal';
    modal.innerHTML = '<div class="nadakki-modal-content"><h3>✅ Resultado: ' + agentName + '</h3><pre>' + JSON.stringify(result, null, 2) + '</pre><button onclick="this.closest(\'.nadakki-result-modal\').remove()">Cerrar</button></div>';
    document.body.appendChild(modal);
    
    showNotification('Agente ' + agentName + ' ejecutado correctamente', 'success');
}

// 6. MOSTRAR NOTIFICACIÓN
function showNotification(message, type = 'info') {
    const notif = document.createElement('div');
    notif.className = 'nadakki-notification nadakki-' + type;
    notif.textContent = message;
    document.body.appendChild(notif);
    
    setTimeout(() => notif.remove(), 3000);
}

// 7. INICIALIZAR AL CARGAR LA PÁGINA
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Nadakki Marketing Executor Initialized');
    loadMarketingAgents();
});

// EXPORTAR FUNCIONES GLOBALES
window.nadakki = {
    executeAgent,
    loadMarketingAgents,
    getTenantID
};
