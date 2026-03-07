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

add_filter( 'plugin_action_links_mystorey-connector/mystorey-connector.php', function( $links ) {
    $url = esc_url( admin_url( 'options-general.php?page=' . MYSTOREY_SETTINGS_PAGE ) );
    $links['settings'] = '<a href="' . $url . '">Settings</a>';
    return $links;
});

add_action( 'admin_enqueue_scripts', function( $hook ) {
    if ( $hook !== 'settings_page_mystorey-connector' ) return;

    wp_add_inline_style( 'wp-admin', '
        .ms-wrap { max-width: 780px; margin: 24px 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
        .ms-header { background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); border-radius: 12px; padding: 32px 36px; margin-bottom: 28px; color: #fff; }
        .ms-header-logo { font-size: 22px; font-weight: 800; letter-spacing: -0.5px; margin: 0 0 6px; }
        .ms-header-logo span { color: #c4b5fd; }
        .ms-header p { margin: 0; opacity: 0.85; font-size: 14px; line-height: 1.5; }
        .ms-steps { display: flex; flex-direction: column; gap: 20px; }
        .ms-step { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 24px 28px; box-shadow: 0 1px 3px rgba(0,0,0,.06); }
        .ms-step-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
        .ms-step-num { width: 32px; height: 32px; border-radius: 50%; background: #7c3aed; color: #fff; font-size: 14px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .ms-step-title { font-size: 15px; font-weight: 700; color: #111827; margin: 0; }
        .ms-step p { margin: 0 0 14px; color: #4b5563; font-size: 14px; line-height: 1.6; }
        .ms-step ol { margin: 0 0 14px 20px; color: #4b5563; font-size: 14px; line-height: 1.8; padding: 0; }
        .ms-field-label { font-size: 12px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
        .ms-copy-row { display: flex; align-items: center; gap: 8px; }
        .ms-code { background: #f3f4f6; border: 1px solid #e5e7eb; border-radius: 6px; padding: 8px 12px; font-family: ui-monospace, "Cascadia Code", monospace; font-size: 13px; color: #1f2937; flex: 1; word-break: break-all; }
        .ms-btn-copy { background: #7c3aed; color: #fff; border: none; border-radius: 6px; padding: 7px 14px; font-size: 12px; font-weight: 600; cursor: pointer; white-space: nowrap; transition: background .15s; }
        .ms-btn-copy:hover { background: #6d28d9; }
        .ms-btn-copy.copied { background: #059669; }
        .ms-btn-primary { display: inline-flex; align-items: center; gap: 6px; background: #7c3aed; color: #fff !important; border-radius: 8px; padding: 10px 20px; font-size: 14px; font-weight: 600; text-decoration: none !important; transition: background .15s; margin-top: 4px; }
        .ms-btn-primary:hover { background: #6d28d9 !important; }
        .ms-btn-secondary { display: inline-flex; align-items: center; gap: 6px; background: #f3f4f6; color: #374151 !important; border: 1px solid #d1d5db; border-radius: 8px; padding: 9px 18px; font-size: 14px; font-weight: 600; text-decoration: none !important; transition: background .15s; }
        .ms-btn-secondary:hover { background: #e5e7eb !important; }
        .ms-token-note { background: #ede9fe; border: 1px solid #c4b5fd; border-radius: 8px; padding: 14px 16px; font-size: 13px; color: #5b21b6; line-height: 1.6; }
        .ms-token-note a { color: #7c3aed; font-weight: 600; }
        .ms-footer { margin-top: 20px; padding: 16px 20px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; font-size: 13px; color: #6b7280; }
        .ms-footer a { color: #7c3aed; font-weight: 600; text-decoration: none; }
    ' );

    wp_add_inline_script( 'jquery-core', '
        function msCopy(text, btn) {
            navigator.clipboard.writeText(text).then(function() {
                btn.textContent = "Copied!";
                btn.classList.add("copied");
                setTimeout(function() {
                    btn.textContent = "Copy";
                    btn.classList.remove("copied");
                }, 2000);
            });
        }
    ' );
});

function mystorey_settings_page() {
    $site_url = get_site_url();
    $mcp_url  = MYSTOREY_MCP_URL;
    $dash_url = MYSTOREY_DASHBOARD_URL;
    $profile_url = admin_url( 'profile.php' ) . '#application-passwords-section';
    ?>
    <div class="ms-wrap">

        <!-- Header -->
        <div class="ms-header">
            <p class="ms-header-logo">My<span>Storey</span></p>
            <p>Connect this WordPress site to MyStorey so your AI assistant can write and publish content directly&nbsp;&mdash; no coding required.</p>
        </div>

        <div class="ms-steps">

            <!-- Step 1 -->
            <div class="ms-step">
                <div class="ms-step-header">
                    <div class="ms-step-num">1</div>
                    <h2 class="ms-step-title">Create an Application Password</h2>
                </div>
                <p>Application Passwords let MyStorey connect to WordPress securely without using your admin password. They are built into WordPress &mdash; no extra plugin needed.</p>
                <ol>
                    <li>Go to <strong>Users &rarr; Profile</strong> in your WordPress admin</li>
                    <li>Scroll to <strong>Application Passwords</strong></li>
                    <li>Enter a name like <code>MyStorey</code> and click <strong>Add New Application Password</strong></li>
                    <li>Copy the generated password &mdash; <strong>you will only see it once</strong></li>
                </ol>
                <a href="<?php echo esc_url( $profile_url ); ?>" class="ms-btn-secondary">
                    Open My Profile &rarr;
                </a>
            </div>

            <!-- Step 2 -->
            <div class="ms-step">
                <div class="ms-step-header">
                    <div class="ms-step-num">2</div>
                    <h2 class="ms-step-title">Register this site on MyStorey</h2>
                </div>
                <p>Open your MyStorey dashboard and add this site. Copy your WordPress URL below and paste it along with the Application Password you just created.</p>

                <div class="ms-field-label">Your WordPress URL</div>
                <div class="ms-copy-row" style="margin-bottom:20px;">
                    <div class="ms-code"><?php echo esc_html( $site_url ); ?></div>
                    <button class="ms-btn-copy" onclick="msCopy('<?php echo esc_js( $site_url ); ?>', this)">Copy</button>
                </div>

                <a href="<?php echo esc_url( $dash_url ); ?>" class="ms-btn-primary" target="_blank" rel="noopener">
                    Open MyStorey Dashboard &rarr;
                </a>
            </div>

            <!-- Step 3 -->
            <div class="ms-step">
                <div class="ms-step-header">
                    <div class="ms-step-num">3</div>
                    <h2 class="ms-step-title">Connect your AI assistant</h2>
                </div>
                <p>After registering your site you will get an <strong>MCP Token</strong> in your MyStorey dashboard. Paste the URL and token below into Claude.ai, ChatGPT, or any MCP-compatible AI:</p>

                <div class="ms-field-label">MCP Server URL</div>
                <div class="ms-copy-row" style="margin-bottom:20px;">
                    <div class="ms-code"><?php echo esc_html( $mcp_url ); ?></div>
                    <button class="ms-btn-copy" onclick="msCopy('<?php echo esc_js( $mcp_url ); ?>', this)">Copy</button>
                </div>

                <div class="ms-token-note">
                    Your <strong>MCP Token</strong> (used as the API key / Bearer token) is shown in your
                    <a href="<?php echo esc_url( $dash_url ); ?>" target="_blank" rel="noopener">MyStorey dashboard</a>
                    after you register this site.
                </div>
            </div>

        </div><!-- .ms-steps -->

        <div class="ms-footer">
            <strong>Need help?</strong> Visit
            <a href="<?php echo esc_url( MYSTOREY_URL . '/wordpress' ); ?>" target="_blank" rel="noopener">
                <?php echo esc_html( MYSTOREY_URL ); ?>/wordpress
            </a> for the full setup guide.
        </div>

    </div><!-- .ms-wrap -->
    <?php
}
