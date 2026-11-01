# muse-connector

Muse のカスタムコネクター `custom.github-muse-chan` 一式っす。
bot アカウント [muse-chan](https://github.com/muse-chan) として GitHub REST API を操作するためのドキュメントとヘルパーで、秘密情報は含まれていないっす。

## 中身

- `CONNECTOR.md` コネクターの操作ドキュメント
- `connector.yaml` コネクターの記述子
- `bin/github_muse.py` 汎用 GitHub API ヘルパー (どのエンドポイントでも叩けるので、トークンのスコープが広がっても作り直し不要)

## 別の環境で使う手順

1. この一式を `~/workspace/custom-connectors/custom.github-muse-chan/` に配置する
2. muse-chan の classic PAT (スコープ `repo` と `workflow`) を用意する
3. `credentials.request_api_access` で host `api.github.com`、配置 `bearer_header` として登録する
4. `python3 bin/github_muse.py me` が 200 で `muse-chan` を返せば接続完了

## 注意

- トークン自体はこのリポジトリに絶対に含めないこと
- fine-grained PAT は repository collaborator のリポジトリに使えないため、classic PAT を使うこと
