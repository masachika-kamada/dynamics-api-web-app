import streamlit as st
from msal_streamlit_authentication import msal_authentication


login_token = msal_authentication(
    auth={
        "clientId": "62cefb99-b36e-4b15-8be0-11e3117978f7",
        "authority": "https://login.microsoftonline.com/organizations",
        "redirectUri": "http://localhost:8501",
        "postLogoutRedirectUri": "http://localhost:8501"
    }, # Corresponds to the 'auth' configuration for an MSAL Instance
    cache={
        "cacheLocation": "sessionStorage",
        "storeAuthStateInCookie": False
    }, # Corresponds to the 'cache' configuration for an MSAL Instance
    login_request={
        "scopes": ["https://orga15ed31f.crm7.dynamics.com/.default"] # ["aaaaaaa-bbbb-cccc-dddd-eeeeeeeeeee/.default"]
    }, # Optional
    logout_request={}, # Optional
    login_button_text="Login", # Optional, defaults to "Login"
    logout_button_text="Logout", # Optional, defaults to "Logout"
    class_name="css_button_class_selector", # Optional, defaults to None. Corresponds to HTML class.
    html_id="html_id_for_button", # Optional, defaults to None. Corresponds to HTML id.
    key="1" # Optional if only a single instance is needed
)
st.write("Recevied login token:", login_token)

if st.button("Go"):
    import requests
    import json


    url = "https://orga15ed31f.crm7.dynamics.com/api/data/v9.2/WhoAmI"
    headers = {
        "Authorization": f"Bearer {login_token["accessToken"]}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("WhoAmI 実行結果:")
        data = response.json()
        print(json.dumps(data, indent=4, ensure_ascii=False))
    else:
        print(f"WhoAmI 失敗: {response.status_code}")
        print(response.text)