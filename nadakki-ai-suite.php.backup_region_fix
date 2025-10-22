<?php
/**
 * Plugin Name: Nadakki AI Suite - Multi-Institution Enterprise
 * Plugin URI: https://nadakki.com/ai-suite
 * Description: Enterprise AI suite designed for unlimited financial institutions with complete white-labeling and feature customization
 * Version: 2.0.0
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

define('NADAKKI_VERSION', '2.0.0');
define('NADAKKI_PLUGIN_FILE', __FILE__);
define('NADAKKI_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('NADAKKI_PLUGIN_URL', plugin_dir_url(__FILE__));
define('NADAKKI_PLUGIN_BASENAME', plugin_basename(__FILE__));

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
