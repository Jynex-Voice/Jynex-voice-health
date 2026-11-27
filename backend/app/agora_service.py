import os
import time
from agora_token_builder import RtcTokenBuilder

Role_Publisher = 1

def generate_rtc_token(channel_name: str, uid: int = 0) -> dict:
    app_id = os.getenv("AGORA_APP_ID", "")
    app_certificate = os.getenv("AGORA_APP_CERTIFICATE", "")

    if not app_id or not app_certificate:
        return {
            "app_id": app_id,
            "token": "demo_token_missing_keys",
            "channel_name": channel_name,
            "uid": uid,
        }

    expiration_time_in_seconds = 3600
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expiration_time_in_seconds

    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channel_name, uid, Role_Publisher, privilege_expired_ts
    )

    return {
        "app_id": app_id,
        "token": token,
        "channel_name": channel_name,
        "uid": uid,
    }