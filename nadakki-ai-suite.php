<?php
/**
 * Plugin Name: Nadakki AI Suite - Multi-Institution Enterprise
 * Plugin URI: https://nadakki.com/ai-suite
 * Description: Enterprise AI suite designed for unlimited financial institutions with complete white-labeling and feature customization
 * Version: 2.0.1
 * Author: Nadakki AI
 * Requires at least: 6.0
 * Tested up to: 6.4
 * Requires PHP: 8.0
 * License: GPL v3 or later
 * Text Domain: nadakki-ai-suite
 * Network: true
 */

if (!defined('ABSPATH')) {
    exit;
}

define('NADAKKI_VERSION', '2.0.1');
define('NADAKKI_PLUGIN_FILE', __FILE__);
define('NADAKKI_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('NADAKKI_PLUGIN_URL', plugin_dir_url(__FILE__));
define('NADAKKI_PLUGIN_BASENAME', plugin_basename(__FILE__));

// ========================================
// PRODUCTION LOGGING - DÍA 3
// ========================================

class NadakkiProductionLogger {
    
    public static function generate_request_id() {
        return 'req_' . uniqid() . '_' . wp_generate_password(8, false);
    }
    
    public static function log_request($endpoint, $tenant_id, $request_id, $start_time, $response_data) {
        $end_time = microtime(true);
        $response_time_ms = round(($end_time - $start_time) * 1000, 2);
        
        $log_entry = [
            'timestamp' => current_time('mysql'),
            'request_id' => $request_id,
            'endpoint' => $endpoint,
            'tenant_id' => $tenant_id,
            'response_time_ms' => $response_time_ms,
            'success' => isset($response_data['quantum_similarity_score']) || isset($response_data['data']),
            'source' => $response_data['source'] ?? 'unknown',
            'score' => $response_data['quantum_similarity_score'] ?? null,
            'risk_level' => $response_data['risk_level'] ?? null
        ];
        
        error_log('NADAKKI_PROD: ' . wp_json_encode($log_entry));
        
        // Guardar métricas (últimas 1000)
        $metrics = get_option('nadakki_metrics', []);
        if (count($metrics) >= 1000) {
            $metrics = array_slice($metrics, -999);
        }
        $metrics[] = $log_entry;
        update_option('nadakki_metrics', $metrics);
        
        return $log_entry;
    }
    
    public static function get_slo_status() {
        $metrics = get_option('nadakki_metrics', []);
        
        if (empty($metrics)) {
            return [
                'status' => 'no_data',
                'message' => 'Insufficient data - run at least 20 evaluations'
            ];
        }
        
        $recent = array_slice($metrics, -100);
        $success_count = count(array_filter($recent, fn($m) => $m['success']));
        $success_rate = ($success_count / count($recent)) * 100;
        
        $times = array_column($recent, 'response_time_ms');
        $avg_time = array_sum($times) / count($times);
        
        sort($times);
        $p95_time = $times[(int)(0.95 * count($times))] ?? 0;
        
        return [
            'success_rate' => round($success_rate, 2),
            'avg_response_ms' => round($avg_time, 2),
            'p95_response_ms' => round($p95_time, 2),
            'total_requests' => count($recent),
            'slo_met' => $success_rate >= 99 && $p95_time <= 1000
        ];
    }
}

// Simple autoloader for our classes
spl_autoload_register(function($class) {
    if (strpos($class, 'Nadakki\\') === 0) {
        $file = NADAKKI_PLUGIN_DIR . 'src/' . str_replace(['Nadakki\\', '\\'], ['', '/'], $class) . '.php';
        if (file_exists($file)) {
            require_once $file;
        }
    }
});

// Initialize plugin
add_action('plugins_loaded', function() {
    try {
        if (class_exists('Nadakki\Core\Plugin')) {
            Nadakki\Core\Plugin::getInstance()->boot();
        }
    } catch (Exception $e) {
        error_log('Nadakki initialization failed: ' . $e->getMessage());
    }
});

// Activation hook
register_activation_hook(__FILE__, function() {
    if (class_exists('Nadakki\Core\Plugin')) {
        Nadakki\Core\Plugin::getInstance()->activate();
    }
    flush_rewrite_rules();
});

// Deactivation hook
register_deactivation_hook(__FILE__, function() {
    if (class_exists('Nadakki\Core\Plugin')) {
        Nadakki\Core\Plugin::getInstance()->deactivate();
    }
    flush_rewrite_rules();
});