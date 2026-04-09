"""
EmailReport.py — Send ExpeDRY test reports via Resend API

Uses the same Resend account as FUZE Atlas (notifications@fuzeatlas.com).
Sends an HTML email with test summary, parameters, and results.

Usage:
    from utils.EmailReport import send_test_report
    send_test_report(
        to='andrew@fuzebiotech.com',
        test_data={...},
        settings={...},
    )
"""

import json
import urllib.request
import urllib.error
from datetime import datetime


# ── Resend config (same as FUZE Atlas) ──
RESEND_API_KEY = 're_gLkzMrbs_M2Df9uTdMAwC9yG124Z1nQam'
RESEND_FROM = 'FUZE Atlas <notifications@fuzeatlas.com>'
FUZE_COLOR = '#00b4c3'


def send_test_report(to, test_data, settings, cc=None):
    """
    Send an ExpeDRY test report email via Resend.

    Args:
        to: recipient email (str or list)
        test_data: dict with keys:
            test_mode, start_weight, end_weight, weight_delta,
            max_weight, avg_temp, avg_humidity, duration_seconds,
            test_phase (final), data_points (list of tuples)
        settings: dict with keys:
            wet_time, dry_time, humidity_setpoint,
            external_hum, internal_hum, heat_mode
        cc: optional CC email(s)

    Returns:
        dict with 'ok' bool and 'id' or 'error'
    """
    subject = f'ExpeDRY Test Report — {test_data.get("test_mode", "Unknown")} — {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    html = _build_html(test_data, settings)

    payload = {
        'from': RESEND_FROM,
        'to': [to] if isinstance(to, str) else to,
        'subject': subject,
        'html': html,
    }
    if cc:
        payload['cc'] = [cc] if isinstance(cc, str) else cc

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            'https://api.resend.com/emails',
            data=data,
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return {'ok': True, 'id': result.get('id')}
    except urllib.error.HTTPError as e:
        err = e.read().decode() if e.fp else str(e)
        print(f'[EMAIL] Resend error: {err}')
        return {'ok': False, 'error': err}
    except Exception as e:
        print(f'[EMAIL] Send failed: {e}')
        return {'ok': False, 'error': str(e)}


def _build_html(test_data, settings):
    """Build HTML email body matching FUZE Atlas email style."""
    mode = test_data.get('test_mode', 'Unknown')
    start_w = test_data.get('start_weight', 0)
    end_w = test_data.get('end_weight', 0)
    delta = test_data.get('weight_delta', 0)
    max_w = test_data.get('max_weight', 0)
    avg_temp = test_data.get('avg_temp', 0)
    avg_humid = test_data.get('avg_humidity', 0)
    duration = test_data.get('duration_seconds', 0)
    phase = test_data.get('test_phase', 'COMPLETE')
    num_points = len(test_data.get('data_points', []))

    wet_time = settings.get('wet_time', 0)
    dry_time = settings.get('dry_time', 0)
    setpoint = settings.get('humidity_setpoint', 0)
    ext_hum = 'ON' if settings.get('external_hum') else 'OFF'
    int_hum = 'ON' if settings.get('internal_hum') else 'OFF'
    heat = settings.get('heat_mode', 'Off')

    duration_str = f'{duration // 60}m {duration % 60}s'

    # Delta color
    if abs(delta) < 0.1:
        delta_color = '#6b7280'
    elif delta > 0:
        delta_color = '#059669'
    else:
        delta_color = '#dc2626'

    return f'''
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
      <div style="text-align: center; padding: 20px 0; border-bottom: 3px solid {FUZE_COLOR};">
        <h1 style="margin: 0; color: {FUZE_COLOR}; font-size: 24px;">FUZE Atlas</h1>
        <p style="margin: 4px 0 0; color: #6b7280; font-size: 14px;">ExpeDRY Test System</p>
      </div>

      <div style="padding: 24px 0;">
        <h2 style="color: #1a1a2e; margin: 0 0 16px;">{mode} Test Report</h2>
        <p style="color: #6b7280; font-size: 14px; margin: 0 0 20px;">
          {datetime.now().strftime('%B %d, %Y at %I:%M %p')} &middot; Duration: {duration_str} &middot; Status: <strong>{phase}</strong>
        </p>

        <!-- Test Settings -->
        <div style="background: #f9fafb; border-left: 4px solid {FUZE_COLOR}; padding: 16px; margin: 0 0 20px; border-radius: 0 8px 8px 0;">
          <p style="margin: 0 0 4px; font-weight: 600; color: #1a1a2e;">Test Parameters</p>
          <table style="width: 100%; font-size: 14px; color: #4b5563;">
            <tr><td style="padding: 2px 8px;">Wet Cycle:</td><td><strong>{wet_time} min</strong> @ {setpoint}% RH</td></tr>
            <tr><td style="padding: 2px 8px;">Dry Cycle:</td><td><strong>{dry_time} min</strong></td></tr>
            <tr><td style="padding: 2px 8px;">External Humidity:</td><td>{ext_hum}</td></tr>
            <tr><td style="padding: 2px 8px;">Internal Humidity:</td><td>{int_hum}</td></tr>
            <tr><td style="padding: 2px 8px;">Column Heat:</td><td>{heat}</td></tr>
          </table>
        </div>

        <!-- Weight Results -->
        <div style="background: #f0fdf4; border-left: 4px solid {delta_color}; padding: 16px; margin: 0 0 20px; border-radius: 0 8px 8px 0;">
          <p style="margin: 0 0 4px; font-weight: 600; color: #1a1a2e;">Weight Results</p>
          <table style="width: 100%; font-size: 14px; color: #4b5563;">
            <tr><td style="padding: 2px 8px;">Start Weight:</td><td><strong>{start_w:.3f} g</strong></td></tr>
            <tr><td style="padding: 2px 8px;">End Weight:</td><td><strong>{end_w:.3f} g</strong></td></tr>
            <tr><td style="padding: 2px 8px;">Delta:</td><td style="color: {delta_color}; font-weight: 700; font-size: 18px;">{delta:+.3f} g</td></tr>
            <tr><td style="padding: 2px 8px;">Max Weight:</td><td>{max_w:.3f} g</td></tr>
          </table>
        </div>

        <!-- Environment -->
        <div style="background: #f9fafb; padding: 16px; margin: 0 0 20px; border-radius: 8px; border: 1px solid #e5e7eb;">
          <p style="margin: 0 0 4px; font-weight: 600; color: #1a1a2e;">Environment</p>
          <table style="width: 100%; font-size: 14px; color: #4b5563;">
            <tr><td style="padding: 2px 8px;">Avg Temperature:</td><td><strong>{avg_temp:.1f} °C</strong></td></tr>
            <tr><td style="padding: 2px 8px;">Avg Humidity:</td><td><strong>{avg_humid:.1f}% RH</strong></td></tr>
            <tr><td style="padding: 2px 8px;">Data Points:</td><td>{num_points}</td></tr>
          </table>
        </div>
      </div>

      <div style="border-top: 1px solid #e5e7eb; padding: 16px 0; text-align: center; color: #9ca3af; font-size: 12px;">
        FUZE Biotech &mdash; ExpeDRY Test System &mdash; fuzeatlas.com
      </div>
    </div>
    '''
