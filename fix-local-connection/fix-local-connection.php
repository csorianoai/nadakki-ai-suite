<?php
/**
 * Plugin Name: Fix Local Connection
 * Plugin URI: https://nadakki.com
 * Description: Repara conexiones locales en WordPress - Soluciona cURL error 28 para localhost, 127.0.0.1 y IPs locales
 * Version: 1.0.0
 * Author: Nadakki AI
 * License: GPL v2 or later
 * Text Domain: fix-local-connection
 * Requires at least: 5.8
 * Requires PHP: 7.4
 */

if (!defined('ABSPATH')) exit;

class FixLocalConnection {
    
    private static $instance = null;
    
    public static function get_instance() {
        if (is_null(self::$instance)) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    private function __construct() {
        $this->init_hooks();
    }
    
    private function init_hooks() {
        add_filter('http_request_args', array($this, 'fix_local_requests'), 999, 2);
        add_filter('https_ssl_verify', '__return_false');
        add_filter('https_local_ssl_verify', '__return_false');
        add_filter('use_streams_transport', array($this, 'force_stream_transport'));
        add_action('admin_menu', array($this, 'add_admin_page'));
    }
    
    public function fix_local_requests($args, $url) {
        if ($this->is_local_url($url)) {
            $args['reject_unsafe_urls'] = false;
            $args['sslverify'] = false;
            $args['timeout'] = 15;
            $args['user-agent'] = 'WordPress/Local-Connection-Fixed';
        }
        return $args;
    }
    
    private function is_local_url($url) {
        $local_patterns = array(
            '/192\.168\.\d+\.\d+/',
            '/10\.\d+\.\d+\.\d+/',
            '/172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+/',
            '/localhost/',
            '/127\.0\.0\.1/',
            '/\.local/',
            '/0\.0\.0\.0/'
        );
        
        foreach ($local_patterns as $pattern) {
            if (preg_match($pattern, $url)) return true;
        }
        return false;
    }
    
    public function force_stream_transport($use_streams) {
        return true;
    }
    
    public function add_admin_page() {
        add_options_page(
            'Fix Local Connection',
            'Local Connection Fix',
            'manage_options',
            'fix-local-connection',
            array($this, 'render_admin_page')
        );
    }
    
    public function render_admin_page() {
        ?>
        <div class="wrap">
            <h1>🔧 Fix Local Connection</h1>
            <div class="card">
                <h2>Estado del Sistema</h2>
                <?php
                $test_url = 'http://192.168.1.110:3002/api/health';
                $response = wp_remote_get($test_url, array('timeout' => 10, 'sslverify' => false));
                
                if (is_wp_error($response)) {
                    echo '<p style="color: red;">❌ Error: ' . esc_html($response->get_error_message()) . '</p>';
                } else {
                    echo '<p style="color: green;">✅ Conectado - HTTP ' . wp_remote_retrieve_response_code($response) . '</p>';
                    echo '<p><strong>Respuesta:</strong> ' . wp_remote_retrieve_body($response) . '</p>';
                }
                ?>
                <p><strong>Plugin Activado:</strong> ✅ Funcionando</p>
                <p><strong>Tu IP Local:</strong> 192.168.1.110:3002</p>
            </div>
            <div class="card">
                <h3>🚀 Instrucciones Rápidas</h3>
                <ol>
                    <li>Activa este plugin</li>
                    <li>Ve a Nadakki Tenant Bridge</li>
                    <li>Guarda la configuración</li>
                    <li>¡Debería funcionar!</li>
                </ol>
            </div>
        </div>
        <?php
    }
}

FixLocalConnection::get_instance();
?>
