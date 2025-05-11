import streamlit as st
from utils.auth import Auth
from utils.api import APIClient
from config import DEFAULT_CLIENT_ID, DEFAULT_AUTHORITY, DEFAULT_REDIRECT_URI
import json

st.set_page_config(page_title="Custom Postman-like API Client", layout="wide")


def init_session_state():
    if "requests" not in st.session_state:
        st.session_state["requests"] = [
            {
                "name": "Sample Request",
                "method": "GET",
                "url": "",
                "headers": "",
                "payload": "",
            }
        ]
    if "selected_request" not in st.session_state:
        st.session_state["selected_request"] = 0
    if "access_token" not in st.session_state:
        st.session_state["access_token"] = None
    if "auth_scopes" not in st.session_state:
        st.session_state["auth_scopes"] = ["user.read"]
    if "msal_flow" not in st.session_state:
        st.session_state["msal_flow"] = None
    if "client_id" not in st.session_state:
        st.session_state["client_id"] = DEFAULT_CLIENT_ID
    if "authority" not in st.session_state:
        st.session_state["authority"] = DEFAULT_AUTHORITY
    if "redirect_uri" not in st.session_state:
        st.session_state["redirect_uri"] = DEFAULT_REDIRECT_URI
    if "device_flow" not in st.session_state:
        st.session_state["device_flow"] = None
    if "device_flow_status" not in st.session_state:
        st.session_state["device_flow_status"] = None


def sidebar_auth_section():
    st.sidebar.title("認証")
    scope_input = st.sidebar.text_input(
        "スコープ (カンマ区切り)", value=",".join(st.session_state["auth_scopes"])
    )

    # 認証 (MSAL) ボタン
    if st.sidebar.button("認証 (MSAL)"):
        scopes = [s.strip() for s in scope_input.split(",") if s.strip()]
        st.session_state["auth_scopes"] = scopes
        auth = Auth(
            client_id=st.session_state["client_id"],
            authority=st.session_state["authority"],
            redirect_uri=st.session_state["redirect_uri"]
        )
        auth_url, _ = auth.get_authorization_url(scopes)
        st.sidebar.markdown(
            f'<a href="{auth_url}" target="_blank" rel="noopener noreferrer">こちらをクリックして認証を行ってください（新しいタブで開きます）</a>',
            unsafe_allow_html=True
        )
        st.sidebar.info("新しいタブで認証を完了してください。アクセストークン取得はデバイス認証で行ってください。")

    # デバイス認証 (推奨) ボタン
    if st.sidebar.button("デバイス認証 (推奨)"):
        scopes = [s.strip() for s in scope_input.split(",") if s.strip()]
        st.session_state["auth_scopes"] = scopes
        auth = Auth(
            client_id=st.session_state["client_id"],
            authority=st.session_state["authority"],
            redirect_uri=st.session_state["redirect_uri"]
        )
        try:
            flow = auth.device_flow(scopes)
            st.session_state["device_flow"] = flow
            st.session_state["device_flow_status"] = "pending"
            st.sidebar.info(
                f"下記のURLを新しいウィンドウで開き、コードを入力して認証してください。\n\n"
                f"認証URL: [こちらをクリック]({flow['verification_uri']})\n\n"
                f"ユーザーコード: `{flow['user_code']}`"
            )
        except Exception as e:
            st.session_state["device_flow"] = None
            st.session_state["device_flow_status"] = "error"
            st.sidebar.error(f"デバイス認証フローの開始に失敗しました: {e}")

    # デバイス認証フロー進行中
    if st.session_state.get("device_flow") and st.session_state.get("device_flow_status") == "pending":
        with st.sidebar:
            with st.spinner("認証完了を待っています...（認証が完了すると自動でトークンが取得されます）"):
                auth = Auth(
                    client_id=st.session_state["client_id"],
                    authority=st.session_state["authority"],
                    redirect_uri=st.session_state["redirect_uri"]
                )
                token = auth.acquire_token_by_device_flow(st.session_state["device_flow"])
                if token:
                    st.session_state["access_token"] = token
                    st.session_state["device_flow_status"] = "success"
                    st.success("アクセストークン取得成功")
                else:
                    st.session_state["access_token"] = None
                    st.session_state["device_flow_status"] = "error"
                    st.error("アクセストークン取得失敗")
                st.session_state["device_flow"] = None

    # アクセストークン表示
    if st.session_state["access_token"]:
        st.sidebar.code(st.session_state["access_token"], language="text")


def sidebar_request_manager():
    st.sidebar.title("リクエスト管理")
    request_names = [req["name"] for req in st.session_state["requests"]]
    selected = st.sidebar.radio(
        "リクエストを選択",
        range(len(request_names)),
        format_func=lambda i: request_names[i],
    )
    st.session_state["selected_request"] = selected

    if st.sidebar.button("新規リクエスト追加"):
        st.session_state["requests"].append(
            {
                "name": f"Request {len(st.session_state['requests']) + 1}",
                "method": "GET",
                "url": "",
                "headers": "",
                "payload": "",
            }
        )
        st.session_state["selected_request"] = len(st.session_state["requests"]) - 1

    if st.sidebar.button("選択中リクエスト削除"):
        idx = st.session_state["selected_request"]
        if len(st.session_state["requests"]) > 1:
            st.session_state["requests"].pop(idx)
            st.session_state["selected_request"] = max(0, idx - 1)
        else:
            st.warning("最低1つのリクエストが必要です。")


def request_editor(req):
    st.header("APIリクエスト編集")
    req["name"] = st.text_input("リクエスト名", value=req["name"])
    req["method"] = st.selectbox(
        "HTTPメソッド",
        ["GET", "POST", "PUT", "PATCH", "DELETE"],
        index=["GET", "POST", "PUT", "PATCH", "DELETE"].index(req["method"]),
    )
    req["url"] = st.text_input("エンドポイントURL", value=req["url"])

    # デフォルトヘッダーの自動セット
    if not req["headers"].strip():
        from utils.api import APIClient
        req["headers"] = json.dumps(APIClient().default_headers, ensure_ascii=False, indent=2)

    req["headers"] = st.text_area(
        "ヘッダー (JSON形式)", value=req["headers"], height=100
    )
    req["payload"] = st.text_area(
        "ペイロード (JSON形式)", value=req["payload"], height=150
    )


def main():
    init_session_state()
    sidebar_auth_section()
    sidebar_request_manager()
    req = st.session_state["requests"][st.session_state["selected_request"]]
    request_editor(req)
    api_execute_section(req)


def api_execute_section(req):
    st.subheader("APIリクエスト実行")
    if st.button("実行"):
        client = APIClient()
        try:
            headers = json.loads(req["headers"]) if req["headers"].strip() else {}
        except Exception as e:
            st.error(f"ヘッダーのJSONパースエラー: {e}")
            headers = {}
        try:
            payload = json.loads(req["payload"]) if req["payload"].strip() else None
        except Exception as e:
            st.error(f"ペイロードのJSONパースエラー: {e}")
            payload = None

        # エンドポイントURLからベースURLを抽出し、scopeを生成
        import re
        url = req["url"]
        base_url = ""
        match = re.match(r"(https://[^/]+)", url)
        if match:
            base_url = match.group(1)
        scope = f"{base_url}/.default" if base_url else None

        # サイレントでトークン再取得
        token = None
        if scope:
            from utils.auth import Auth
            auth = Auth(
                client_id=st.session_state["client_id"],
                authority=st.session_state["authority"],
                redirect_uri=st.session_state["redirect_uri"]
            )
            token = auth.acquire_token_silent([scope])
        # 失敗時はsession_stateのトークンを使う
        if not token:
            token = st.session_state["access_token"]

        result = client.request(
            method=req["method"],
            url=req["url"],
            token=token,
            headers=headers,
            data=payload,
        )
        st.write("**ステータスコード:**", result["status_code"], result["reason"])
        st.write("**レスポンスヘッダー:**")
        st.json(result["headers"])
        st.write("**レスポンスボディ:**")
        if isinstance(result["body"], (dict, list)):
            st.json(result["body"])
        else:
            st.code(result["body"], language="text")


if __name__ == "__main__":
    main()
