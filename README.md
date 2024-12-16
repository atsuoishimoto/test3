# aaaa

TEMPLATE: アプリケーションの簡単な説明を記載

# Description

TEMPLATE: このアプリケーションの目的・解決する課題を記載


# Documents

TEMPLATE: 以下について記載

* アプリケーションのアーキテクチャ図(DBや外部APIとの繋がりなど)
* 仕様・デザイン
* ディレクトリ構造
* 運用体制・手順



## 実行方法

```
poetry install

# (必要に応じて)
poetry run task migrate  # DBテーブル作成
poetry run task createsuperuser  # 管理ユーザ作成

# webサーバ起動
poetry run task runserver  # port8000で起動
```

docker を利用しても起動出来ます。 http://localhost:8080/ でアクセス。

```
docker-compose up
```

* アプリの前段にNginxがプロキシとして用意されています
* `/tmp` 以下にログが生成されます
* fluent (ポート10224) でアプリケーション固有のアクションログを送ります
* 必要に応じてdjangoの `--settings` オプションを指定してください
    * 手元開発: `bbbb.settings` (default)
    * 開発: `bbbb.settings.development`
    * 本番: `bbbb.settings.production`

データベースとしてMySQLを利用する場合は、次のコマンドで起動してください。

```
docker-compose -f docker-compose.mysql.yml up
```


#### Test

GitHub Actionsで走るテストは以下のコマンドで手元でも確認できます。

```
poetry run tox
```

事前に以下のコマンドでコードを整形して下さい。
```
poetry run task format
```

以下のコマンドはより強力なformatです。場合によっては破壊的変更となるのでご注意ください
```
poetry run task unsafe-format
```

次のコマンドで、使用されていないDjangoのsettings項目をチェックできます。

```
poetry run task check-settings
```


### Deploy

* GitHub ActionsによりAWS環境へ自動的にデプロイされます。
    * main: 開発環境
    * deployment/production: 本番環境
