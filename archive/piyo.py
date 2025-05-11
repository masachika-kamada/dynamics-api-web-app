# import uuid
# import streamlit as st
# from msal import PublicClientApplication

# CLIENT_ID    = "62cefb99-b36e-4b15-8be0-11e3117978f7"
# AUTHORITY    = "https://login.microsoftonline.com/common"
# REDIRECT_URI = "http://localhost:8501"
# SCOPE        = ["https://orga15ed31f.crm7.dynamics.com/.default"]
import streamlit as st
import msal
import uuid

class Auth:
    def __init__(self, client_id, authority, redirect_uri):
        self.client_id = client_id
        self.authority = authority
        self.redirect_uri = redirect_uri
        self.app = msal.PublicClientApplication(self.client_id, authority=self.authority)
        self.state = str(uuid.uuid4())

    def get_authorization_url(self, scopes):
        flow = self.app.initiate_auth_code_flow(
            scopes,
            redirect_uri=self.redirect_uri,
            state=self.state
        )
        return flow["auth_uri"], flow

# ここで自分のアプリ登録のclient_idを使うこと！
client_id = "62cefb99-b36e-4b15-8be0-11e3117978f7"
authority = "https://login.microsoftonline.com/organizations"
redirect_uri = "http://localhost:8501"

if "auth_flow" not in st.session_state:
    st.session_state["auth_flow"] = None

if st.button("認証 (MSAL)"):
    scopes = ["User.Read"]  # 例
    auth = Auth(client_id, authority, redirect_uri)
    auth_url, flow = auth.get_authorization_url(scopes)
    st.session_state["auth_flow"] = flow
    st.markdown(
        f'<a href="{auth_url}" target="_blank" rel="noopener noreferrer">こちらをクリックして認証を行ってください</a>',
        unsafe_allow_html=True
    )
    st.info("認証後、リダイレクトされたURLのcodeパラメータをコピーして、下の入力欄に貼り付けてください。")
    st.stop()

code = st.text_input("認証後のURLのcodeパラメータを貼り付けてください")
if code and st.session_state["auth_flow"]:
    result = msal.PublicClientApplication(client_id, authority=authority).acquire_token_by_auth_code_flow(
        st.session_state["auth_flow"],
        {"code": code}
    )
    st.write(result)
