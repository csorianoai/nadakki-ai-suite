<?php
/**
 * Nadakki Monitor Integration v4.0
 * Autor: César Soriano
 * Fecha: 2025-10-24
 * Muestra el panel de monitoreo de Nadakki AI Suite dentro del dashboard WordPress.
 */

if (!defined('ABSPATH')) exit;

function nadakki_monitor_iframe_shortcode($atts) {
    if (!current_user_can('manage_options')) {
        return '<p style="color:red;">Acceso restringido. Solo los administradores pueden ver este panel.</p>';
    }

    $atts = shortcode_atts(array(
        'url' => 'http://127.0.0.1:8000/monitor',
        'height' => '850',
        'token' => 'nadakki-secure'
    ), $atts, 'nadakki_monitor');

    ob_start(); ?>
    <div style="border:2px solid #00aaff; border-radius:10px; overflow:hidden; box-shadow:0 0 15px rgba(0,0,0,0.3); margin-top:20px;">
        <iframe 
            src="<?php echo esc_url($atts['url']); ?>" 
            style="width:100%; height:<?php echo esc_attr($atts['height']); ?>px; border:none; background:#0d1117;"
            sandbox="allow-same-origin allow-scripts allow-forms"
            referrerpolicy="no-referrer"
            loading="lazy">
        </iframe>
    </div>
    <p style="font-size:12px; text-align:center; color:#aaa;">
        Conectado a <b>Nadakki AI Suite v4.0</b> • Token: <code><?php echo esc_html($atts['token']); ?></code>
    </p>
    <?php
    return ob_get_clean();
}
add_shortcode('nadakki_monitor', 'nadakki_monitor_iframe_shortcode');

function nadakki_monitor_admin_menu() {
    add_menu_page(
        'Nadakki Monitor',
        'Monitor Enterprise',
        'manage_options',
        'nadakki-monitor',
        'nadakki_monitor_admin_page',
        'dashicons-chart-line',
        3
    );
}
add_action('admin_menu', 'nadakki_monitor_admin_menu');

function nadakki_monitor_admin_page() {
    echo '<div class="wrap"><h1>Monitor Enterprise – Nadakki AI Suite v4.0</h1>';
    echo do_shortcode('[nadakki_monitor]');
    echo '</div>';
}
