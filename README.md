# Dynamics API Web App

Postman のような Web API 実行のための Web アプリの作成を検討したが、技術的課題が多かった

MSAL 認証について

* acquire_token_interactive
  * Streamlit で実行すると、ホストしているマシンのコマンドラインに認証用 URL が表示された
  * このリンクを取得できなかったのと、認証はホスト側のマシンしか対応しないみたい
* initiate_auth_code_flow
  * `client_id = "51f81489-12ee-4a9e-aaae-a2591f45987d"` はマイクロソフトがサポートしているやつ？みたい
  * この client id は本当のアクセス？でないとダメみたいで、Web アプリ経由でエラー
  * これを避けるために Azure Portal から Entra のアプリ登録をして client id を発行する必要がある
  * 認証を進めると、code が発行されるが、それが URL のクエリパラメータとして取れる
  * そこからの変換とか諸々がうまくいかなかった
* initiate_device_flow
  * 上記 client id を作成して認証までできて、動作した
  * しかし、Azure で設定できる API のアクセス許可の中に <https://api.bap.microsoft.com> の利用をどう設定すればいいかわからず、Dynamics 365 環境への接続はできるけれど、PPAC の環境一覧取得のようなことはできなかった

streamlit 内での MSAL 認証について、以下のライブラリもあった

* <https://pypi.org/project/msal-streamlit-authentication/>
* ポップアップが表示されて UX 的には非常によかったが、scope 間での移動、サイレントでのトークンの取り直しが msal の app として取得しているわけではなかったのでサポートされておらずよくなかった

結論、デスクトップアプリならよさそう
