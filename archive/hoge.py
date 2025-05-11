from msal import PublicClientApplication
import streamlit as st
import uuid

CLIENT_ID    = "62cefb99-b36e-4b15-8be0-11e3117978f7"
AUTHORITY    = "https://login.microsoftonline.com/common"
REDIRECT_URI = "http://localhost:8501"

# MSAL 初期化
app = PublicClientApplication(
    client_id=CLIENT_ID,
    authority=AUTHORITY,
)

# 認可コードフロー開始
flow = app.initiate_auth_code_flow(
    scopes       = ["https://orga15ed31f.crm7.dynamics.com/.default"],
    redirect_uri = REDIRECT_URI,
    state        = str(uuid.uuid4())
)
auth_url = flow["auth_uri"]

st.markdown(
    f'<a href="{auth_url}" target="_blank">こちらを開いて認証</a>',
    unsafe_allow_html=True
)

# 1) ユーザーが認証を完了してリダイレクトされてきた後…
# 2) Streamlit で現在の URL のクエリパラメータを取得
#    （Streamlit 1.30.0 以降は st.query_params、以前は st.experimental_get_query_params）
query_params = st.query_params  # :contentReference[oaicite:0]{index=0}

# 3) その dict をそのまま MSAL に渡す
#    例： {"code": ["<認可コード>"], "state": ["<state>"]} の形
if st.button("認証"):
    # auth_code = query_params.get("code", [None])[0]
    # if auth_code:
    #     st.session_state["auth_code"] = auth_code
    # else:
    #     st.error("認可コードが取得できませんでした。")
    query_params = st.query_params()
    result = app.acquire_token_by_auth_code_flow(flow, query_params)  # :contentReference[oaicite:1]{index=1}

    if "access_token" in result:
        access_token = result["access_token"]
        st.success("認証成功しました！")
    else:
        st.error(f"認証に失敗しました: {result.get('error_description')}")
