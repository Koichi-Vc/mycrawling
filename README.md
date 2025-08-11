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
requirements.txtに記載されたライブラリと、英語解析モデルのen_core_web_smをインストールしてください。

[requirements.txtのダウンロードurl](https://github.com/Koichi-Vc/mycrawling/blob/develop/requirements.txt)

**インストール方法の例**

` pip install -r requirements.txt `

**en_core_web_emのインストール**
`python -m spacy download en_core_web_sm`

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

### **conf**

パッケージを実行する為の設定を定義します。
#### create_setting.py
ユーザーが設定する為のファイルを生成します。

##### CreateSettingクラス
インスタンス化する事で、ユーザー設定用のファイルパスを定義して生成します。

#### data_setting.py

設定ファイルの内容を読み込みます。

##### Ref_DataConfigクラス
設定内容を読み込みパッケージ全体に反映させるためのクラス。内部でRetainSettingConfをインスタンス化する事でデフォルトの設定(ユーザー設定がある場合はオーバーライド)を読み込みます。

##### RetainSettingConfクラス
setting.pyから有効な設定変数を取得し、またsetting_fileにユーザーによる設定情報ファイル(.pyファイル)を渡す事で読み込み時に反映させる事もできます。

### crawlings
サイト内をクローリングする機能を提供します。

#### crawling.py
最初に受け取ったurlにアクセスし会社概要と推定されるコンテンツが見つからなかった場合に、サイト内のリンクをたどってクローリングをします。
最初のじてんでコンテンツが見つかった場合は、スクレイピングを実行してクローリングはせずに終了します。


### filters
Beautifulsoup.find_allで検索する際のフィルターを作成するパッケージ。
要素に対するフィルターから属性をターゲットにしたフィルターにも対応する様にしました。
またフィルターにかける前後に処理を追加できる機能もあります。

#### elements.py
要素検索に使うフィルターを作成するモジュールです。なおこのモジュールで作成できるフィルターは主に属性を対象にしており、タグ名はサポートしておりません。


##### ElementsFilterクラス
パラメータが受け取るものはBeautifulsoup.find_allが受け付ける引数に準じており、加えて、conditionではフィルター条件(and, orなど)をoperaterモジュールのメソッド等で指定します。またcriteria_valueには基準とする値を指定できます。

**パラメータ**
- attr : フィルター対象の要素から取得する属性を指定する。受け取った値はElementsFilter.get_attributeメソッドにて、element.get(self.attr)で取得される。

- criteria_value : フィルタリングを行う際の条件とする値を受け取ります。受け取った値はattrの値とconditionが受け取るメソッドで比較されます。

- condition: フィルタリングを実行する際の条件式となるメソッドを受け取ります。

- list_operator_type: 対象に対して複数の条件値でフィルタリングをする際の条件値リストを受け取ります。

- filter_method: デフォルトでは無く独自のメソッドを使用する場合はこの引数が受け取ります。



## サードパーティーライセンス
サードパーティライブラリのライセンスの全文は、third_party_license/Third_Party_License.txtにあります。

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

