import json
import requests


class APIClient:
    def __init__(self):
        # デフォルトヘッダー
        self.default_headers = {
            "Content-Type": "application/json",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
        }

    def request(self, method, url, token=None, headers=None, data=None):
        # ヘッダーをマージ
        req_headers = self.default_headers.copy()
        if headers:
            req_headers.update(headers)
        if token:
            req_headers["Authorization"] = f"Bearer {token}"

        # dataがdictの場合はjson化
        if isinstance(data, dict):
            data = json.dumps(data)

        response = requests.request(method, url, headers=req_headers, data=data)
        try:
            resp_json = response.json()
        except Exception:
            resp_json = response.text

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": resp_json,
            "ok": response.ok,
            "reason": response.reason,
        }
