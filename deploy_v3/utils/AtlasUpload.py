"""
AtlasUpload.py — Post ExpeDRY test results to FUZE Atlas lab portal

Posts test data to the FUZE Atlas API at fuzeatlas.com.
Creates or updates a test run record linked to a test request.

Usage:
    from utils.AtlasUpload import post_test_results
    result = post_test_results(
        test_data={...},
        settings={...},
        test_request_id='abc123',  # optional — links to existing request
    )
"""

import json
import urllib.request
import urllib.error
from datetime import datetime


# ── Atlas API config ──
ATLAS_BASE_URL = 'https://fuzeatlas.com'
# API key for machine-to-machine auth — set this to a valid session token or API key
# For now we'll use a dedicated endpoint that accepts a device key
ATLAS_DEVICE_KEY = 'expedry-helios-v3'


def post_test_results(test_data, settings, test_request_id=None, brand_name=None, fabric_name=None):
    """
    Post test results to FUZE Atlas.

    Args:
        test_data: dict with keys:
            test_mode, start_weight, end_weight, weight_delta,
            max_weight, avg_temp, avg_humidity, duration_seconds,
            test_phase, data_points
        settings: dict with keys:
            wet_time, dry_time, humidity_setpoint,
            external_hum, internal_hum, heat_mode
        test_request_id: optional Atlas test request ID to link to
        brand_name: optional brand name for the test
        fabric_name: optional fabric identifier

    Returns:
        dict with 'ok' bool and 'id' or 'error'
    """
    payload = {
        'source': 'expedry-helios',
        'device_key': ATLAS_DEVICE_KEY,
        'timestamp': datetime.now().isoformat(),
        'test_mode': test_data.get('test_mode', 'Unknown'),
        'test_phase': test_data.get('test_phase', 'COMPLETE'),
        'duration_seconds': test_data.get('duration_seconds', 0),

        # Weight data
        'start_weight': test_data.get('start_weight', 0),
        'end_weight': test_data.get('end_weight', 0),
        'weight_delta': test_data.get('weight_delta', 0),
        'max_weight': test_data.get('max_weight', 0),

        # Environment data
        'avg_temp': test_data.get('avg_temp', 0),
        'avg_humidity': test_data.get('avg_humidity', 0),

        # Test settings from wizard
        'settings': {
            'wet_time_min': settings.get('wet_time', 0),
            'dry_time_min': settings.get('dry_time', 0),
            'humidity_setpoint': settings.get('humidity_setpoint', 0),
            'external_hum': settings.get('external_hum', False),
            'internal_hum': settings.get('internal_hum', False),
            'heat_mode': settings.get('heat_mode', 'Off'),
        },

        # Time-series data (sampled every interval)
        'data_points': test_data.get('data_points', []),

        # Optional linkage
        'test_request_id': test_request_id,
        'brand_name': brand_name,
        'fabric_name': fabric_name,
    }

    url = f'{ATLAS_BASE_URL}/api/expedry/upload'

    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'X-Device-Key': ATLAS_DEVICE_KEY,
            },
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            print(f'[ATLAS] Upload OK: {result}')
            return {'ok': True, 'data': result}
    except urllib.error.HTTPError as e:
        err = e.read().decode() if e.fp else str(e)
        print(f'[ATLAS] Upload error: {err}')
        return {'ok': False, 'error': err}
    except Exception as e:
        print(f'[ATLAS] Upload failed: {e}')
        return {'ok': False, 'error': str(e)}
