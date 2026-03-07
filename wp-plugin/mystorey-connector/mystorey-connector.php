<?php
/**
 * Plugin Name: MyStorey – AI Content Control
 * Plugin URI: https://mystorey.io/wordpress
 * Description: Connect your WordPress site to MyStorey so you can control your content via Claude, ChatGPT, or any AI assistant. No coding required.
 * Version: 1.0.0
 * Author: MyStorey
 * Author URI: https://mystorey.io
 * License: GPL v2 or later
 * Text Domain: mystorey-connector
 */

if ( ! defined( 'ABSPATH' ) ) exit;

define( 'MYSTOREY_PLUGIN_VERSION', '1.0.0' );
define( 'MYSTOREY_SETTINGS_PAGE', 'mystorey-connector' );

// Add settings menu
add_action( 'admin_menu', function() {
    add_options_page(
        'MyStorey AI Connector',
        'MyStorey AI',
        'manage_options',
        MYSTOREY_SETTINGS_PAGE,
        'mystorey_settings_page'
    );
});

// Render settings page
function mystorey_settings_page() {
    $site_url = get_site_url();
    $mcp_url  = 'https://mystorey.io/mcp';
    $dashboard_url = 'https://mystorey.io/dashboard/wordpress';
    ?>
    <div class="wrap">
        <h1>MyStorey – AI Content Control</h1>
        <p>Connect this WordPress site to MyStorey so your AI assistant can write and publish content directly.</p>

        <hr/>

        <h2>Step 1: Create an Application Password</h2>
        <p>WordPress Application Passwords let MyStorey connect securely without using your admin password.</p>
        <ol>
            <li>Go to <strong>Users → Profile</strong> in your WordPress admin</li>
            <li>Scroll down to <strong>Application Passwords</strong></li>
            <li>Enter a name like <code>MyStorey</code> and click <strong>Add New Application Password</strong></li>
            <li>Copy the generated password — you will only see it once</li>
        </ol>
        <p>
            <a href="<?php echo esc_url( admin_url( 'profile.php' ) ); ?>#application-passwords-section" class="button button-secondary">
                Open My Profile →
            </a>
        </p>

        <hr/>

        <h2>Step 2: Register on MyStorey</h2>
        <p>Go to the MyStorey dashboard and add your WordPress site:</p>
        <table class="form-table">
            <tr>
                <th>Your WordPress URL</th>
                <td>
                    <code style="font-size:14px;background:#f0f0f0;padding:6px 10px;border-radius:4px;">
                        <?php echo esc_html( $site_url ); ?>
                    </code>
                    <p class="description">Copy this into the MyStorey registration form.</p>
                </td>
            </tr>
        </table>
        <p>
            <a href="<?php echo esc_url( $dashboard_url ); ?>" class="button button-primary" target="_blank">
                Open MyStorey Dashboard →
            </a>
        </p>

        <hr/>

        <h2>Step 3: Connect Your AI</h2>
        <p>After registering on MyStorey, you will receive an MCP URL and MCP Token. Paste them into your AI client:</p>
        <table class="form-table">
            <tr>
                <th>MCP URL</th>
                <td>
                    <code style="font-size:14px;background:#f0f0f0;padding:6px 10px;border-radius:4px;">
                        <?php echo esc_html( $mcp_url ); ?>
                    </code>
                </td>
            </tr>
            <tr>
                <th>MCP Token</th>
                <td><em>Available in your <a href="<?php echo esc_url( $dashboard_url ); ?>" target="_blank">MyStorey dashboard</a> after registering your site.</em></td>
            </tr>
        </table>

        <hr/>

        <p><strong>Need help?</strong> Visit <a href="https://mystorey.io/wordpress" target="_blank">mystorey.io/wordpress</a> for a full setup guide.</p>
    </div>
    <?php
}
