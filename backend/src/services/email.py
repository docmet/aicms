"""Email service — transactional emails via SMTP.

Uses aiosmtplib for async sending. Works with Mailpit locally and
Mail-in-a-Box (or any SMTP server) in staging/production.

Usage:
    from src.services.email import EmailService
    await EmailService.send_welcome(user.email, user.email)
"""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from src.config import get_settings

logger = logging.getLogger(__name__)


async def _send(to: str, subject: str, html: str, text: str) -> None:
    settings = get_settings()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            start_tls=settings.smtp_tls,
        )
        logger.info("Email sent: %s → %s", subject, to)
    except Exception as exc:
        logger.error("Email send failed: %s", exc)
        # Non-fatal — don't raise, email is not critical path


class EmailService:
    @staticmethod
    async def send_welcome(to: str, name: str) -> None:
        """Welcome email after registration."""
        settings = get_settings()
        dashboard = f"{settings.frontend_url}/dashboard"
        mcp_url = f"{settings.frontend_url}/dashboard/mcp"

        html = f"""
        <div style="font-family:sans-serif;max-width:540px;margin:0 auto;padding:32px 16px;">
          <h1 style="font-size:24px;font-weight:700;color:#111;">Welcome to MyStorey!</h1>
          <p style="color:#555;">Hi {name},</p>
          <p style="color:#555;">Your account is ready. Build your first website by talking to your AI assistant.</p>
          <a href="{dashboard}" style="display:inline-block;margin:16px 0;background:#7c3aed;color:#fff;font-weight:600;padding:12px 24px;border-radius:8px;text-decoration:none;">
            Go to Dashboard
          </a>
          <p style="color:#555;font-size:14px;">
            To use AI tools, connect your MCP URL at
            <a href="{mcp_url}" style="color:#7c3aed;">{mcp_url}</a>.
          </p>
          <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
          <p style="color:#999;font-size:12px;">© 2026 MyStorey · hello@mystorey.io</p>
        </div>
        """

        text = f"""Welcome to MyStorey!

Your account is ready. Go to your dashboard:
{dashboard}

Connect your AI assistant at:
{mcp_url}
"""
        await _send(to, "Welcome to MyStorey!", html, text)

    @staticmethod
    async def send_plan_upgraded(to: str, plan: str) -> None:
        """Confirmation after successful plan upgrade."""
        settings = get_settings()
        plan_label = plan.capitalize()
        portal_url = f"{settings.frontend_url}/dashboard/billing?plan={plan}"

        html = f"""
        <div style="font-family:sans-serif;max-width:540px;margin:0 auto;padding:32px 16px;">
          <h1 style="font-size:24px;font-weight:700;color:#111;">You're on {plan_label}!</h1>
          <p style="color:#555;">Your MyStorey plan has been upgraded to <strong>{plan_label}</strong>. Thank you!</p>
          <a href="{settings.frontend_url}/dashboard" style="display:inline-block;margin:16px 0;background:#7c3aed;color:#fff;font-weight:600;padding:12px 24px;border-radius:8px;text-decoration:none;">
            Go to Dashboard
          </a>
          <p style="color:#555;font-size:14px;">
            To manage or cancel your subscription, visit
            <a href="{portal_url}" style="color:#7c3aed;">your billing settings</a>.
          </p>
          <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
          <p style="color:#999;font-size:12px;">© 2026 MyStorey · hello@mystorey.io</p>
        </div>
        """

        text = f"""You're on {plan_label}!

Your MyStorey plan has been upgraded to {plan_label}. Thank you!

Dashboard: {settings.frontend_url}/dashboard
Manage subscription: {portal_url}
"""
        await _send(to, f"You're now on MyStorey {plan_label}", html, text)

    @staticmethod
    async def send_plan_limit_reached(to: str, plan: str, limit: int) -> None:
        """Notification when user hits their site creation limit."""
        settings = get_settings()
        upgrade_url = f"{settings.frontend_url}/dashboard/billing?plan=pro"

        html = f"""
        <div style="font-family:sans-serif;max-width:540px;margin:0 auto;padding:32px 16px;">
          <h1 style="font-size:24px;font-weight:700;color:#111;">Site limit reached</h1>
          <p style="color:#555;">
            You've reached the limit of <strong>{limit} site{'' if limit == 1 else 's'}</strong>
            on the {plan.capitalize()} plan.
          </p>
          <p style="color:#555;">Upgrade to create more sites.</p>
          <a href="{upgrade_url}" style="display:inline-block;margin:16px 0;background:#7c3aed;color:#fff;font-weight:600;padding:12px 24px;border-radius:8px;text-decoration:none;">
            Upgrade Plan
          </a>
          <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
          <p style="color:#999;font-size:12px;">© 2026 MyStorey · hello@mystorey.io</p>
        </div>
        """

        text = f"""Site limit reached

You've reached the limit of {limit} site(s) on the {plan.capitalize()} plan.

Upgrade to create more sites: {upgrade_url}
"""
        await _send(to, "MyStorey: site limit reached", html, text)

    @staticmethod
    async def send_page_published(to: str, site_name: str, page_title: str, public_url: str) -> None:
        """Confirmation when a page is published."""
        html = f"""
        <div style="font-family:sans-serif;max-width:540px;margin:0 auto;padding:32px 16px;">
          <h1 style="font-size:24px;font-weight:700;color:#111;">Page published!</h1>
          <p style="color:#555;">
            <strong>{page_title}</strong> on <strong>{site_name}</strong> is now live.
          </p>
          <a href="{public_url}" style="display:inline-block;margin:16px 0;background:#7c3aed;color:#fff;font-weight:600;padding:12px 24px;border-radius:8px;text-decoration:none;">
            View live page
          </a>
          <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
          <p style="color:#999;font-size:12px;">© 2026 MyStorey · hello@mystorey.io</p>
        </div>
        """

        text = f"""Page published!

{page_title} on {site_name} is now live:
{public_url}
"""
        await _send(to, f"Published: {page_title}", html, text)

    @staticmethod
    async def send_verification_email(to: str, token: str) -> None:
        """Email address confirmation link sent on registration."""
        settings = get_settings()
        verify_url = f"{settings.frontend_url}/verify-email?token={token}"

        html = f"""
        <div style="font-family:sans-serif;max-width:540px;margin:0 auto;padding:32px 16px;">
          <h1 style="font-size:24px;font-weight:700;color:#111;">Confirm your email</h1>
          <p style="color:#555;">Thanks for signing up for MyStorey! Click the button below to confirm your email address and activate your account.</p>
          <a href="{verify_url}" style="display:inline-block;margin:20px 0;background:#7c3aed;color:#fff;font-weight:600;padding:12px 28px;border-radius:8px;text-decoration:none;">
            Confirm email address
          </a>
          <p style="color:#999;font-size:13px;">This link expires in 24 hours. If you didn't sign up for MyStorey, ignore this email.</p>
          <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
          <p style="color:#999;font-size:12px;">© 2026 MyStorey · hello@mystorey.io</p>
        </div>
        """

        text = f"""Confirm your MyStorey email

Click the link below to confirm your email address:
{verify_url}

This link expires in 24 hours. If you didn't sign up, ignore this email.
"""
        await _send(to, "Confirm your MyStorey email", html, text)

    @staticmethod
    async def send_contact_notification(
        to: str,
        site_name: str,
        visitor_name: str,
        visitor_email: str,
        subject: str | None,
        message: str,
    ) -> None:
        """Notify site owner of a new contact form submission."""
        subject_line = f"New message on {site_name}"
        display_subject = subject or "(no subject)"

        html = f"""
        <div style="font-family:sans-serif;max-width:540px;margin:0 auto;padding:32px 16px;">
          <h1 style="font-size:22px;font-weight:700;color:#111;">New contact form submission</h1>
          <p style="color:#555;">You received a new message on <strong>{site_name}</strong>.</p>
          <table style="width:100%;border-collapse:collapse;margin:16px 0;">
            <tr><td style="padding:8px 0;color:#999;width:100px;">From</td><td style="padding:8px 0;color:#111;">{visitor_name} &lt;{visitor_email}&gt;</td></tr>
            <tr><td style="padding:8px 0;color:#999;">Subject</td><td style="padding:8px 0;color:#111;">{display_subject}</td></tr>
          </table>
          <div style="background:#f5f5f5;border-radius:8px;padding:16px;margin:16px 0;">
            <p style="color:#333;margin:0;white-space:pre-wrap;">{message}</p>
          </div>
          <p style="color:#555;font-size:14px;">Reply directly to this email or visit your <a href="#" style="color:#7c3aed;">MyStorey dashboard</a> to view all submissions.</p>
          <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
          <p style="color:#999;font-size:12px;">© 2026 MyStorey · hello@mystorey.io</p>
        </div>
        """

        text = f"""New contact form submission on {site_name}

From: {visitor_name} <{visitor_email}>
Subject: {display_subject}

{message}
"""
        await _send(to, subject_line, html, text)

    @staticmethod
    async def send_password_reset(to: str, token: str) -> None:
        """Password reset link."""
        settings = get_settings()
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"

        html = f"""
        <div style="font-family:sans-serif;max-width:540px;margin:0 auto;padding:32px 16px;">
          <h1 style="font-size:24px;font-weight:700;color:#111;">Reset your password</h1>
          <p style="color:#555;">We received a request to reset your MyStorey password. Click below to choose a new one.</p>
          <a href="{reset_url}" style="display:inline-block;margin:20px 0;background:#7c3aed;color:#fff;font-weight:600;padding:12px 28px;border-radius:8px;text-decoration:none;">
            Reset password
          </a>
          <p style="color:#999;font-size:13px;">This link expires in 1 hour. If you didn't request a reset, ignore this email — your password won't change.</p>
          <hr style="border:none;border-top:1px solid #eee;margin:24px 0;" />
          <p style="color:#999;font-size:12px;">© 2026 MyStorey · hello@mystorey.io</p>
        </div>
        """

        text = f"""Reset your MyStorey password

Click the link below to reset your password:
{reset_url}

This link expires in 1 hour. If you didn't request a reset, ignore this email.
"""
        await _send(to, "Reset your MyStorey password", html, text)
