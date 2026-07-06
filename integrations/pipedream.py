import requests


class PipedreamClient:
    def __init__(self, webhook_url: str, timeout: int = 20):
        self.webhook_url = webhook_url
        self.timeout = timeout

    def send(self, action: str, session_id: str, **payload):
        response = requests.post(
            self.webhook_url,
            json={
                "action": action,
                "session_id": session_id,
                **payload,
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        if not response.content:
            return {
                "ok": True,
                "status_code": response.status_code,
            }

        try:
            return response.json()
        except ValueError:
            return {
                "ok": True,
                "status_code": response.status_code,
                "response_text": response.text[:500],
            }