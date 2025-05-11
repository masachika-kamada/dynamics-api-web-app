import msal
import uuid
import os

class Auth:
    CACHE_PATH = "msal_token_cache.bin"

    def __init__(self, client_id=None, authority=None, redirect_uri=None):
        self.client_id = client_id
        self.authority = authority
        self.redirect_uri = redirect_uri or "http://localhost:8501"
        # キャッシュ永続化
        self.token_cache = msal.SerializableTokenCache()
        if os.path.exists(self.CACHE_PATH):
            with open(self.CACHE_PATH, "rb") as f:
                self.token_cache.deserialize(f.read().decode("utf-8"))
        self.app = msal.PublicClientApplication(
            self.client_id,
            authority=self.authority,
            token_cache=self.token_cache
        )
        self.state = str(uuid.uuid4())

    def _save_cache(self):
        if self.token_cache.has_state_changed:
            with open(self.CACHE_PATH, "wb") as f:
                f.write(self.token_cache.serialize().encode("utf-8"))

    def get_authorization_url(self, scopes):
        # 認証URLを生成
        flow = self.app.initiate_auth_code_flow(
            scopes,
            redirect_uri=self.redirect_uri,
            state=self.state
        )
        return flow["auth_uri"], flow

    def acquire_token_silent(self, scopes):
        # サイレントでトークン再取得
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(scopes, account=accounts[0])
            self._save_cache()
            if result is None:
                print("Silent token acquisition failed: result is None")
                return None
            if "access_token" in result:
                return result["access_token"]
            else:
                print("Silent token acquisition failed:", result.get("error_description"))
                return None
        else:
            print("No accounts found for silent token acquisition.")
            return None

    def acquire_token_by_authorization_code(self, flow, code):
        # 認可コードからトークン取得
        result = self.app.acquire_token_by_auth_code_flow(flow, {"code": code})
        self._save_cache()
        if "access_token" in result:
            return result["access_token"]
        else:
            print("Token acquisition failed:", result.get("error_description"))
            return None

    def device_flow(self, scopes):
        # デバイスコードフローを開始
        flow = self.app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise Exception("Failed to create device flow. Error: %s" % flow)
        return flow

    def acquire_token_by_device_flow(self, flow):
        # デバイスコードフローでトークン取得
        result = self.app.acquire_token_by_device_flow(flow)
        self._save_cache()
        if "access_token" in result:
            print(f"{self.app.get_accounts()=}")
            return result["access_token"]
        else:
            print(f"{self.app.get_accounts()=}")
            print("Device code flow failed:", result.get("error_description"))
            return None
