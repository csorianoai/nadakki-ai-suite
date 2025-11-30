// File: api-connections.js - COPIAR A WORDPRESS THEME
const NADAKKI_API = {
    baseUrl: 'http://localhost:5000',
    endpoints: {
        evaluate: '/api/evaluate-credit',
        agentStatus: '/api/agents/status',
        tenantSwitch: '/api/tenant/switch',
        metrics: '/api/dashboard/metrics'
    },
    
    // Función principal de evaluación
    async evaluateCredit(data, tenantId) {
        const response = await fetch(${this.baseUrl}/api/evaluate-credit, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Tenant-ID': tenantId
            },
            body: JSON.stringify(data)
        });
        return await response.json();
    },
    
    // Cambio de tenant dinámico
    async switchTenant(tenantId) {
        const response = await fetch(${this.baseUrl}/api/tenant/switch, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({tenant_id: tenantId})
        });
        return await response.json();
    }
};

// Integración WordPress - COPIAR AL functions.php
function nadakki_dashboard_scripts() {
    wp_enqueue_script('nadakki-api', get_template_directory_uri() . '/js/api-connections.js', array(), '1.0.0', true);
    wp_localize_script('nadakki-api', 'nadakki_ajax', array(
        'ajax_url' => admin_url('admin-ajax.php'),
        'nonce' => wp_create_nonce('nadakki_nonce')
    ));
}
add_action('wp_enqueue_scripts', 'nadakki_dashboard_scripts');
