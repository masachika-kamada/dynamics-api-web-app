import uuid
import streamlit as st
from msal import PublicClientApplication

# ── 1. 定数設定 ──
CLIENT_ID    = "62cefb99-b36e-4b15-8be0-11e3117978f7"
AUTHORITY    = "https://login.microsoftonline.com/common"
REDIRECT_URI = "http://localhost:8501"
SCOPE        = ["https://orga15ed31f.crm7.dynamics.com/.default"]

# ── 2. MSAL アプリケーションの初期化 ──
app = PublicClientApplication(client_id=CLIENT_ID, authority=AUTHORITY)

# ── 3. 認可コードフローの開始 ──
if "auth_flow" not in st.session_state:
    # 初回のみ flow を作成してセッションに保存
    st.session_state.auth_flow = app.initiate_auth_code_flow(
        scopes       = SCOPE,
        redirect_uri = REDIRECT_URI,
        state        = str(uuid.uuid4())
    )

flow = st.session_state.auth_flow
auth_url = flow["auth_uri"]

st.markdown(
    f'<a href="{auth_url}" target="_blank">ここをクリックして認証を行う</a>',
    unsafe_allow_html=True
)

# ── 4. リダイレクト後のクエリパラメータ取得 ──
#    (A) 旧 API
# query_params = st.experimental_get_query_params()

#    (B) 新 API（括弧不要）
raw_qp = st.query_params

# ── 5. dict に変換して、値のリストから文字列を取り出す ──
#    MSAL は {"code":"xxx", "state":"yyy"} の形を期待
auth_response = {
    key: raw_qp[key][0]  # リストの先頭要素
    for key in ("code", "state")
    if key in raw_qp and raw_qp[key]
}

# ── 6. トークン取得 ──
if auth_response.get("code"):
    result = app.acquire_token_by_auth_code_flow(flow, auth_response)  # :contentReference[oaicite:0]{index=0}

    if "access_token" in result:
        st.success("認証成功！アクセストークンを取得しました。")
        access_token = result["access_token"]
        # ここで Web API 呼び出しなどへ利用
    else:
        st.error(f"認証エラー: {result.get('error_description')}")

