# acquire_token_interactive の仕組み

`acquire_token_interactive` は **デスクトップアプリやコマンドラインアプリ向け** の認証方式。
この関数は、実行しているマシン上で一時的なWebサーバ（例: `localhost:38989`）を立ち上げる。
認証URLのリダイレクト先（`redirect_uri`）はこの一時サーバ（例: `http://localhost:38989`）。
認証URLはそのマシンのローカル（localhost）でしかアクセスできない。

## どういうこと？

### 例1：自分のPCで実行

1. 自分のPCで `acquire_token_interactive` を実行。
2. コマンドラインに認証URLが表示される。
3. そのURLを自分のPCのブラウザで開く。
4. 認証が終わると、自分のPCの `localhost:38989` にリダイレクトされ、トークンが取得できる。

### 例2：別のPCからアクセス

1. サーバーAで `acquire_token_interactive` を実行。
2. サーバーAのコマンドラインに認証URLが表示される。
3. 自分のPC（サーバーAとは別）でそのURLを開く。
4. 認証が終わると、自分のPCの `localhost:38989` にリダイレクトされる。
5. でも、サーバーAの `localhost:38989` で待っているプログラムとは通信できないので、認証が完了しない。

## まとめ

- `acquire_token_interactive` は「実行しているマシン」専用の認証方式。
- 他のマシンのユーザーが同じ認証URLを使っても、認証は完了しない。
- Webアプリ（Streamlitなど）で「他のユーザーにも認証してもらいたい」場合は、「認証URLのリダイレクト先がWebアプリ自身（例: `http://your-web-app.com`）」になるようなフロー（Authorization Code Flow）を使う必要がある。

## 補足

- `acquire_token_interactive` は「自分専用の認証」で、他の人には使わせられない。
- Webアプリでみんなが使える認証リンクを出したい場合は、`initiate_auth_code_flow` を使う。
