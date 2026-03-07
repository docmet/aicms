<?php
/**
 * Plugin Name: MyStorey – AI Content Control
 * Plugin URI: {{MYSTOREY_URL}}/wordpress
 * Description: Connect your WordPress site to MyStorey so you can control your content via Claude, ChatGPT, or any AI assistant. No coding required.
 * Version: 1.0.0
 * Author: MyStorey
 * Author URI: {{MYSTOREY_URL}}
 * License: GPL v2 or later
 * Text Domain: mystorey-connector
 * Update URI: {{MYSTOREY_URL}}/api/wordpress/plugin/update-check
 */

if ( ! defined( 'ABSPATH' ) ) exit;

define( 'MYSTOREY_PLUGIN_VERSION', '1.0.0' );
define( 'MYSTOREY_URL', '{{MYSTOREY_URL}}' );
define( 'MYSTOREY_MCP_URL', '{{MYSTOREY_URL}}/mcp' );
define( 'MYSTOREY_DASHBOARD_URL', '{{MYSTOREY_URL}}/dashboard/wordpress' );
define( 'MYSTOREY_SETTINGS_PAGE', 'mystorey-connector' );

add_action( 'admin_menu', function() {
    add_options_page(
        'MyStorey AI Connector',
        'MyStorey AI',
        'manage_options',
        MYSTOREY_SETTINGS_PAGE,
        'mystorey_settings_page'
    );
});

add_action( 'admin_enqueue_scripts', function( $hook ) {
    if ( $hook !== 'settings_page_mystorey-connector' ) return;
    wp_add_inline_script( 'jquery-core', '
        function mystoreyCopy(text, btn) {
            navigator.clipboard.writeText(text).then(function() {
                var orig = btn.textContent;
                btn.textContent = "Copied!";
                btn.style.background = "#00a32a";
                setTimeout(function() {
                    btn.textContent = orig;
                    btn.style.background = "";
                }, 2000);
            });
        }
    ' );
});

function mystorey_copy_button( $text, $label = 'Copy' ) {
    $esc = esc_attr( $text );
    return '<button type="button" class="button button-small"
        style="margin-left:8px;vertical-align:middle;"
        onclick="mystoreyCopy(\'' . $esc . '\', this)">' . esc_html( $label ) . '</button>';
}

function mystorey_settings_page() {
    $site_url = get_site_url();
    ?>
    <div class="wrap">
        <h1>MyStorey – AI Content Control</h1>
        <p>Connect this WordPress site to MyStorey so your AI assistant can write and publish content directly.</p>

        <hr/>

        <h2>Step 1 — Create an Application Password</h2>
        <p>Application Passwords let MyStorey connect to WordPress securely, without using your admin password.</p>
        <ol>
            <li>Go to <strong>Users → Profile</strong> in your WordPress admin</li>
            <li>Scroll to <strong>Application Passwords</strong></li>
            <li>Enter a name like <code>MyStorey</code> and click <strong>Add New Application Password</strong></li>
            <li>Copy the generated password — <strong>you will only see it once</strong></li>
        </ol>
        <p>
            <a href="<?php echo esc_url( admin_url( 'profile.php' ) ); ?>#application-passwords-section"
               class="button button-secondary">Open My Profile →</a>
        </p>

        <hr/>

        <h2>Step 2 — Register on MyStorey</h2>
        <p>Open the MyStorey dashboard and register this site. Use the values below:</p>

        <table class="form-table" role="presentation">
            <tr>
                <th scope="row">Your WordPress URL</th>
                <td>
                    <code style="font-size:13px;background:#f0f0f0;padding:6px 10px;border-radius:4px;">
                        <?php echo esc_html( $site_url ); ?>
                    </code>
                    <?php echo mystorey_copy_button( $site_url, 'Copy URL' ); ?>
                </td>
            </tr>
        </table>

        <p style="margin-top:16px;">
            <a href="<?php echo esc_url( MYSTOREY_DASHBOARD_URL ); ?>"
               class="button button-primary" target="_blank" rel="noopener">
                Open MyStorey Dashboard →
            </a>
        </p>

        <hr/>

        <h2>Step 3 — Connect Your AI</h2>
        <p>After registering your site on MyStorey you will receive an <strong>MCP Token</strong>.
           Paste the values below into Claude.ai, ChatGPT (Developer mode), or any MCP-compatible AI:</p>

        <table class="form-table" role="presentation">
            <tr>
                <th scope="row">MCP URL</th>
                <td>
                    <code style="font-size:13px;background:#f0f0f0;padding:6px 10px;border-radius:4px;">
                        <?php echo esc_html( MYSTOREY_MCP_URL ); ?>
                    </code>
                    <?php echo mystorey_copy_button( MYSTOREY_MCP_URL, 'Copy URL' ); ?>
                    <p class="description">Paste this as the MCP server URL in your AI client.</p>
                </td>
            </tr>
            <tr>
                <th scope="row">MCP Token</th>
                <td>
                    <em>Available in your
                        <a href="<?php echo esc_url( MYSTOREY_DASHBOARD_URL ); ?>" target="_blank" rel="noopener">
                            MyStorey dashboard
                        </a>
                        after registering this site.
                    </em>
                    <p class="description">Use this as the Bearer token / API key in your AI client.</p>
                </td>
            </tr>
        </table>

        <hr/>

        <p>
            <strong>Need help?</strong>
            Visit <a href="<?php echo esc_url( MYSTOREY_URL ); ?>/wordpress" target="_blank" rel="noopener">
                <?php echo esc_html( MYSTOREY_URL ); ?>/wordpress
            </a> for the full setup guide.
        </p>
    </div>
    <?php
}
