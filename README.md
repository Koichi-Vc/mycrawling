# MyCrawling
現在作成中。


## 概要
企業のwebサイトから会社概要をスクレイピングし、DataFrameオブジェクトを生成します。
始めに、アクセスしたページ内で会社概要を探し、見つかった場合はスクレイピングをして終了し、見つからなかった場合は、サイト内のクローリングを開始します。


### 開発の経緯
プログラミングとパッケージ設計・開発、web技術の学習、スクレイピングを学習するにあたって、クローリングとスクレイピングの自動化パッケージをテーマとして制作しました。
名称をMyCrawlingとしたのは、将来的に会社概要だけでなくクローリングやスクレイピングを通して柔軟なデータ収集の自動化を目指して行くという意味を込めています。


### 課題
パッケージが持つ機能に対して設計が過剰になってしまい、それに伴ってデバッグが複雑になってしまった事が問題になりました。
次はより詳細な設計方法とシンプルに適切且つ保守性を意識した開発方法を学んで行きたいと考えています。

### 利用するにあたって
当パッケージはwebサイトへアクセスしスクレイピングやクローリングを行います。使用前に対象サイトの規約確認を厳守してください。またrobots.txtの確認もお願いします。
そして、スクレイピングやロボットによるアクセスを禁止しているサイトへは絶対に使用しないでください。


## インストール
※当パッケージは学習を兼ねたプロジェクトであり、現在開発中です。

### pipを使ったインストール
mainブランチをインストールする場合は以下を実行してください。※mainブランチは現在インストール可能なファイルはありません。

`pip install git+https://github.com/Koichi-Vc/mycrawling.git `

developブランチをインストールする場合は以下を実行してください

`pip install git+https://github.com/Koichi-Vc/mycrawling.git@develop`

### git cloneの場合

git cloneを使用する場合は以下を実行してください。

`git clone https://github.com/Koichi-Vc/mycrawling.git`

### インストール時の注意
requirements.txtに記載されたライブラリをインストールしてください。

[requirements.txtのダウンロードurl](https://github.com/Koichi-Vc/mycrawling/blob/develop/requirements.txt)

**インストール方法の例**

` pip install -r requirements.txt `


#### chromedriver-binaryについて
webドライバーとブラウザのバージョンは必ず一致する様にして下さい。
このプロジェクトでは、デフォルトでchromedriver-binaryの最新バージョンをインストールする仕様になっています

##### Ubuntu環境
Ubuntu環境でChromiumブラウザの最新バージョンとchromedriver-binaryの最新バージョンが一致しない問題に直面して居ります。


## クイックスタート

パッケージをデフォルト設定でスタートさせる場合はmain.pyを使用します。以下のコードを実行してください。

```
from mycrawling.main import Main
crawl_main = Main()
```
これによりデフォルトの設定内容が自動で読み込まれ各種オブジェクトが生成されます。
次に以下のコードを実行する事でスクレイピングを開始します。
続いて`start`に対象のサイトurlを渡します。

`result = crawl_main.start('https://example.com/')`


## 設定の反映
パッケージ全体の設定を反映させるにあたって、ユーザーがuser_settingsファイルを用意する事でデフォルトの設定をオーバーライド出来ます。
ユーザーによるセッティングファイルを自動生成する場合は、create_settins.pyをスクリプト実行します。

例:

`python -m mycrawling.conf.create_settings`

上記のコードを実行すると設定ファイルが生成されデフォルトの設定をオーバーライド出来る様になります。
設定内容を読み込むには、以下のコードを実行します。

```
from mycrawling.conf.data_setting import Ref_DataConfig
ref_dataconfig = Ref_DataConfig.ref_dataconfig_factory()
```


## 各種サブパッケージ紹介
現在作成中。


## サードパーティーライセンス
サードパーティライブラリのライセンスの全文は、Licenses/Third_Party_License.txtにあります。

- **Beautiful Soup4**
    - copyright
        - Copyright (c) Leonard Richardson
    - ライセンス情報ソースurl
        - [MIT License](https://github.com/deepin-community/beautifulsoup4/blob/master/LICENSE)


- **chromedriver-binary**
    - copyright
        - Copyright (c) 2017 Daniel Kaiser
    - ライセンス情報ソースurl
        - [MIT License](https://github.com/danielkaiser/python-chromedriver-binary/blob/master/LICENSE)


- **GiNZA**
    - copyright
        - Copyright (c) 2019 Megagon Labs
    - ライセンス情報ソースurl
        - [MIT License](https://github.com/megagonlabs/ginza/blob/master/LICENSE)

- **lxml**
    - copyright
        - Copyright (c) 2004 Infrae. All rights reserved.
    - ライセンス情報ソースurl
        - [BSD License](https://github.com/lxml/lxml/blob/master/doc/licenses/BSD.txt)

- **NumPy**
    - copyright
        - Copyright (c) 2005-2025, NumPy Developers. All rights reserved.
    - ライセンス情報ソースurl
        - [BSD License](https://github.com/numpy/numpy/blob/main/LICENSE.txt)


- **pandas**
    - copyright
        - Copyright (c) 2008-2011, AQR Capital Management, LLC, Lambda Foundry, Inc. and PyData Development Team
        All rights reserved.
        - Copyright (c) 2011-2025, Open source contributors.
    - ライセンス情報ソースurl
        - [BSD-3-Clause](https://github.com/pandas-dev/pandas/blob/main/LICENSE)


- **RapidFuzz**
    - copyright
        - Copyright © 2020-present Max Bachmann
        - Copyright © 2011 Adam Cohen
    - ライセンス情報ソースurl
        - [MIT License](https://github.com/rapidfuzz/RapidFuzz/blob/main/LICENSE)


- **Requests**
    - copyright
        - Copyright 2019 Kenneth Reitz
    - ライセンス情報ソースurl
        - [Apache License 2.0](https://github.com/psf/requests/blob/main/LICENSE)


- **Selenium**
    - copyright
        - Copyright 2025 Software Freedom Conservancy (SFC)
    - ライセンス情報ソースurl
        - [Apache License Version 2.0](https://github.com/SeleniumHQ/selenium/blob/trunk/LICENSE)


- **spaCy**
    - copyright
        - Copyright (c) 2024 ExplosionAI GmbH
    - ライセンス情報ソースurl
        - [MIT License](https://github.com/explosion/spacy-layout/blob/main/LICENSE)

