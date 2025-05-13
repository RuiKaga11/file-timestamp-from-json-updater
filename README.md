# timestamp
## 元ソース（@sontyu09さん）
googleフォトからアーカイブ形式でダウンロードした写真のタイムスタンプを変更するプログラム。
手元のPCにgoogleフォトから移動するときにタイムスタンプがずれてしまったので作成しました。
調べたところ、クラウドからローカルにダウンロードした際のタイムスタンプ問題は解決できないようだった。
解決サービスもないので、同じように考えた方の既存のソースをもとに、Geminiに丸投げして、jpeg,mp4など対象範囲の拡大、フォルダごと行えるようにカスタマイズした。
元記事（https://qiita.com/sontyu09/items/cbccea6e645328d9c461）
元ソース（https://gitlab.com/sontyu/timestamp）
アーカイブ形式での一括ダウンロード方法は[こちら](https://support.google.com/accounts/answer/3024190?sjid=16825085842255200521-AP)を参考にしてください。

## 環境構築
`dokcer compose`にて環境構築を行う。


```sh
$ cd .env_files
$ docker compose up -d
```

## 解凍したアーカイブファイルの中身
[こちら](https://support.google.com/accounts/answer/3024190?sjid=16825085842255200521-AP)を参考にダウンロードしたアーカイブ形式のファイルを解凍したときの中身はこんな構造。

```sh
$ tree
.
├── Google フォト
│   ├── アルバム名
│   │   ├── IMG_2439.JPG
│   │   ├── IMG_2439.JPG.json
│   │   ├── IMG_2440.JPG
│   │   ├── IMG_2440.JPG.json
.
.
.
```
JPGのメタ情報を見てみると、ダウンロードした日が作成日になっている。

そこで、同じファイル名のjsonファイルの中身を見ると。

```.json
{
  "title": "jsonと同名のフォト名.mp4",
  "description": "",
  "imageViews": "0",
  "creationTime": {
    "timestamp": "1744731312",
    "formatted": "2025/04/15 15:35:12 UTC"
  },
  "photoTakenTime": {
    "timestamp": "1713678482",
    "formatted": "2024/04/21 5:48:02 UTC"
  },
  "geoData": {
    "latitude": 0.0,
    "longitude": 0.0,
    "altitude": 0.0,
    "latitudeSpan": 0.0,
    "longitudeSpan": 0.0
  },
  "url": "https://photos.google/photo/｛メタ名｝",
  "googlePhotosOrigin": {
    "mobileUpload": {
      "deviceType": "IOS_PHONE"
    }
  }
}
```

jsonファイルの中にメタデータが書き込まれているよう。
なのでjsonファイルから読み取ったデータをもとに写真(PNG)のメタデータを書き換える。


## 実行方法
`src/`内にある[timestamp.py](src/timestamp.py)を実行する。
引数に対象にしたい画像ファイル名を指定すると、指定した名前と同じjsonファイルを読み込んでメタ情報を書き換える。

vscodeのターミナルから以下を実行（私の環境）

python timestamp.py (適用したいディレクトリ（またはフォルダ）)  

ちゃんと作成日が変更された。
