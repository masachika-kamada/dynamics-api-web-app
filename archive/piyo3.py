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

if st.button("認証 (MSAL)"):
    scopes = ["User.Read"]  # 例: 必要なスコープに変更
    client_id = "62cefb99-b36e-4b15-8be0-11e3117978f7"
    authority = "https://login.microsoftonline.com/organizations"
    redirect_uri = "http://localhost:8501"
    auth = Auth(client_id, authority, redirect_uri)
    auth_url, flow = auth.get_authorization_url(scopes)
    print(f"{auth_url=}")
    print(f"{flow=}")
    st.session_state["auth_flow"] = flow
    st.markdown(f'<a href="{auth_url}" target="_blank">認証リンク</a>', unsafe_allow_html=True)
    st.stop()

code = st.text_input("認証後のURLのcodeパラメータを貼り付けてください")

if st.button("認証"):
    if code and st.session_state.get("auth_flow"):
        result = msal.PublicClientApplication(client_id, authority=authority).acquire_token_by_auth_code_flow(
            st.session_state["auth_flow"],
            {"code": code, "state": st.session_state["auth_flow"]["state"]}
        )
        if "access_token" in result:
            st.success("認証成功！")
            access_token = result["access_token"]
            st.write(f"アクセストークン: {access_token}")
        else:
            st.error(f"認証失敗: {result.get('error_description')}")
    else:
        st.error("認証コードが無効です。もう一度やり直してください。")
