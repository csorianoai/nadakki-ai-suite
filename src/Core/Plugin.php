<?php
declare(strict_types=1);

namespace Nadakki\Core;

final class Plugin {
    
    private static ?self $instance = null;
    private bool $booted = false;
    private array $institutions = [];
    
    private function __construct() {
        $this->loadInstitutions();
    }
    
    public static function getInstance(): self {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    public function boot(): void {
        if ($this->booted) return;
        $this->initializeHooks();
        $this->booted = true;
    }
    
    private function initializeHooks(): void {
        add_action('admin_menu', [$this, 'addAdminMenus']);
        add_action('rest_api_init', [$this, 'registerRestRoutes']);
    }
    
    public function addAdminMenus(): void {
        add_menu_page(
            'Nadakki AI Suite',
            'Nadakki AI',
            'manage_options',
            'nadakki-main',
            [$this, 'renderMainDashboard'],
            'dashicons-robot',
            30
        );
        
        add_submenu_page(
            'nadakki-main',
            'Institutions',
            'Institutions',
            'manage_options',
            'nadakki-institutions',
            [$this, 'renderInstitutions']
        );
        
        add_submenu_page(
            'nadakki-main',
            'Deploy New Institution',
            'New Institution',
            'manage_options',
            'nadakki-deploy',
            [$this, 'renderDeployment']
        );
    }
    
    public function renderMainDashboard(): void {
        $institution_count = count($this->institutions);
        echo '<div class="wrap">';
        echo '<h1>Nadakki AI Suite - Multi-Institution Platform</h1>';
        echo '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">';
        echo '<div style="background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">';
        echo '<h3>Active Institutions</h3>';
        echo '<p style="font-size: 2em; font-weight: bold; color: #2271b1; margin: 10px 0;">' . $institution_count . '</p>';
        echo '</div>';
        echo '<div style="background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">';
        echo '<h3>Total Modules</h3>';
        echo '<p style="font-size: 2em; font-weight: bold; color: #2271b1; margin: 10px 0;">6</p>';
        echo '</div>';
        echo '<div style="background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">';
        echo '<h3>AI Agents</h3>';
        echo '<p style="font-size: 2em; font-weight: bold; color: #2271b1; margin: 10px 0;">40+</p>';
        echo '</div>';
        echo '<div style="background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 20px; text-align: center;">';
        echo '<h3>Status</h3>';
        echo '<p style="font-size: 1.2em; color: #00a32a; font-weight: bold;">Operational</p>';
        echo '</div>';
        echo '</div>';
        echo '</div>';
    }
    
    public function renderInstitutions(): void {
        echo '<div class="wrap">';
        echo '<h1>Financial Institutions</h1>';
        echo '<p>Manage all registered financial institutions.</p>';
        echo '<table class="wp-list-table widefat fixed striped">';
        echo '<thead><tr><th>Institution ID</th><th>Name</th><th>Status</th><th>Type</th></tr></thead>';
        echo '<tbody>';
        
        if (empty($this->institutions)) {
            echo '<tr><td colspan="4">No institutions registered yet. <a href="admin.php?page=nadakki-deploy">Deploy your first institution</a></td></tr>';
        } else {
            foreach ($this->institutions as $inst) {
                echo '<tr>';
                echo '<td>' . esc_html($inst['id']) . '</td>';
                echo '<td>' . esc_html($inst['name']) . '</td>';
                echo '<td><span style="color: #00a32a; font-weight: bold;">Active</span></td>';
                echo '<td>' . esc_html($inst['type']) . '</td>';
                echo '</tr>';
            }
        }
        
        echo '</tbody></table>';
        echo '</div>';
    }
    
    public function renderDeployment(): void {
        if (isset($_POST['deploy_institution']) && wp_verify_nonce($_POST['nadakki_nonce'], 'deploy_institution')) {
            $this->handleDeployment();
        }
        
        echo '<div class="wrap">';
        echo '<h1>Deploy New Institution</h1>';
        echo '<form method="post" action="">';
        wp_nonce_field('deploy_institution', 'nadakki_nonce');
        echo '<table class="form-table">';
        echo '<tr><th scope="row">Institution ID</th><td><input type="text" name="institution_id" class="regular-text" required /></td></tr>';
        echo '<tr><th scope="row">Institution Name</th><td><input type="text" name="institution_name" class="regular-text" required /></td></tr>';
        echo '<tr><th scope="row">Institution Type</th><td>';
        echo '<select name="institution_type" required>';
        echo '<option value="commercial_bank">Commercial Bank</option>';
        echo '<option value="credit_union">Credit Union</option>';
        echo '<option value="microfinance">Microfinance Institution</option>';
        echo '<option value="fintech_startup">Fintech Startup</option>';
        echo '</select></td></tr>';
        echo '<tr><th scope="row">Country</th><td><input type="text" name="country" class="regular-text" value="US" required /></td></tr>';
        echo '<tr><th scope="row">Currency</th><td><input type="text" name="currency" class="regular-text" value="USD" required /></td></tr>';
        echo '<tr><th scope="row">Admin Email</th><td><input type="email" name="admin_email" class="regular-text" required /></td></tr>';
        echo '</table>';
        echo '<p class="submit"><input type="submit" name="deploy_institution" class="button-primary" value="Deploy Institution" /></p>';
        echo '</form>';
        echo '</div>';
    }
    
    private function handleDeployment(): void {
        $institution_id = sanitize_text_field($_POST['institution_id']);
        $institution_name = sanitize_text_field($_POST['institution_name']);
        $institution_type = sanitize_text_field($_POST['institution_type']);
        
        $institutions = get_option('nadakki_institutions', []);
        $institutions[$institution_id] = [
            'id' => $institution_id,
            'name' => $institution_name,
            'type' => $institution_type,
            'country' => sanitize_text_field($_POST['country']),
            'currency' => sanitize_text_field($_POST['currency']),
            'admin_email' => sanitize_email($_POST['admin_email']),
            'created_at' => current_time('mysql')
        ];
        update_option('nadakki_institutions', $institutions);
        
        echo '<div class="notice notice-success"><p>Institution "' . esc_html($institution_name) . '" deployed successfully!</p></div>';
        $this->loadInstitutions();
    }
    
    public function registerRestRoutes(): void {
        register_rest_route('nadakki/v1', '/institutions', [
            'methods' => 'GET',
            'callback' => [$this, 'getInstitutions'],
            'permission_callback' => '__return_true'
        ]);
        
        register_rest_route('nadakki/v1', '/health', [
            'methods' => 'GET',
            'callback' => [$this, 'healthCheck'],
            'permission_callback' => '__return_true'
        ]);
    }
    
    public function getInstitutions(): array {
        return [
            'success' => true,
            'institutions' => get_option('nadakki_institutions', []),
            'version' => NADAKKI_VERSION
        ];
    }
    
    public function healthCheck(): array {
        return [
            'status' => 'healthy',
            'version' => NADAKKI_VERSION,
            'timestamp' => current_time('c'),
            'institutions_count' => count(get_option('nadakki_institutions', []))
        ];
    }
    
    private function loadInstitutions(): void {
        $this->institutions = get_option('nadakki_institutions', []);
    }
    
    public function activate(): void {
        add_option('nadakki_version', NADAKKI_VERSION);
        add_option('nadakki_institutions', []);
        flush_rewrite_rules();
    }
    
    public function deactivate(): void {
        flush_rewrite_rules();
    }
}
