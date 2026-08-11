# たちばな便り (Atashinchi Watch)

「あたしンち」のグッズ・イベント情報を見逃さないための個人用監視ツール。GitHub Actionsで定期的にサイトを巡回し、新着をLINEに通知する。

**現在の稼働状況**: 高確度モード（3サイト定点観測 + LINE通知）は本番稼働中。低確度モード（キーワード検索）は、想定していたGoogle Custom Search JSON APIが新規顧客の受付を停止しており（Bing Search APIも2025年8月に完全retire済み）利用できないため、`low_confidence.yml`のcronは無効化して見送り中。代替の検索API（Brave Search APIなど、要クレジットカード登録）を選定できたら`GOOGLE_API_KEY`/`GOOGLE_CSE_ID`相当のSecretsを差し替えて`gh workflow enable low_confidence.yml`で再開できる。

## 構成

- `scripts/common/` — 状態管理・LINE送信・クォータ管理・障害検知など共通ロジック
- `scripts/adapters/` — サイトごとのスクレイパー（けらえいこ公式 / シンエイ ONLINE STORE / shopぬい）
- `scripts/google_search.py` — Google Custom Searchによるキーワード検索（低確度モード）
- `scripts/site_generator.py` — `state/` のJSONから `docs/index.html` を生成
- `scripts/run_high_confidence.py` — 15分おきに実行（高確度モード）
- `scripts/run_low_confidence.py` — 1日1回実行（低確度モード + ダイジェスト送信）
- `state/` — 既読レジストリ・LINE送信数・サイト障害状態・ダイジェスト待ち行列（リポジトリにコミットして永続化、90日で自動プルーニング）
- `docs/` — GitHub Pagesで公開する生成済み静的サイト

## セットアップ

1. リポジトリをpublicで作成し、Settings → Actions → General → Workflow permissions を「Read and write permissions」に設定
2. LINE Developersで公式アカウント（Messaging API）を作成し、Channel Access Tokenと自分のuserIdを取得
3. Google Cloud ConsoleでCustom Search JSON APIを有効化し、API KeyとProgrammable Search EngineのCSE ID(cx)を取得
4. リポジトリSecretsに登録: `LINE_CHANNEL_ID` / `LINE_CHANNEL_SECRET` / `LINE_USER_ID` / `GOOGLE_API_KEY` / `GOOGLE_CSE_ID`
5. Settings → Pages → Source を `main` ブランチの `/docs` に設定

## ローカル開発

```bash
pip install -r requirements-dev.txt
pytest
DRY_RUN=1 python -m scripts.run_high_confidence
```

`DRY_RUN=1` の場合、LINEへの実送信は行わずログ出力のみとなる。
