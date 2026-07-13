import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
import os

# Initialize Firebase
cred_path = os.path.join(settings.BASE_DIR, 'firebase-key.json')
if os.path.exists(cred_path) and not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)


def send_push_notification(token, title, body, data=None):
    try:
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            token=token,
        )
        response = messaging.send(message)
        return {'success': True, 'message_id': response}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def send_multicast_notification(tokens, title, body, data=None):
    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            tokens=tokens,
        )
        response = messaging.send_each_for_multicast(message)
        return {
            'success': True,
            'success_count': response.success_count,
            'failure_count': response.failure_count,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}