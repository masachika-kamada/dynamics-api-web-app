import streamlit as st
import msal
import uuid
import urllib.parse

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

client_id = "62cefb99-b36e-4b15-8be0-11e3117978f7"
authority = "https://login.microsoftonline.com/organizations"
redirect_uri = "http://localhost:8501"
scopes = ["User.Read"]

if "auth_flow" not in st.session_state:
    st.session_state["auth_flow"] = None
if "step" not in st.session_state:
    st.session_state["step"] = "start"

if st.session_state["step"] == "start":
    if st.button("認証 (MSAL)"):
        auth = Auth(client_id, authority, redirect_uri)
        auth_url, flow = auth.get_authorization_url(scopes)
        st.session_state["auth_flow"] = flow
        st.session_state["step"] = "wait_code"
        st.markdown(
            f'<a href="{auth_url}" target="_blank" rel="noopener noreferrer">こちらをクリックして認証を行ってください</a>',
            unsafe_allow_html=True
        )
        st.info("認証後、リダイレクトされたURLのcodeパラメータをコピーして、下の入力欄に貼り付けてください。")
        st.stop()

if st.session_state["step"] == "wait_code":
    code_input = st.text_input("認証後のURLのcodeパラメータを貼り付けてください")
    # codeだけ抽出
    def extract_code(text):
        if text.startswith("http"):
            parsed = urllib.parse.urlparse(text)
            qs = urllib.parse.parse_qs(parsed.query)
            return qs.get("code", [""])[0]
        else:
            return text
    code = extract_code(code_input)
    if code:
        result = msal.PublicClientApplication(client_id, authority=authority).acquire_token_by_auth_code_flow(
            st.session_state["auth_flow"],
            {"code": code}
        )
        st.write(result)
        st.session_state["step"] = "done"
