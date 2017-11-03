# HIKAKIN_SYM

ヒカキンシンメトリーBot  

## about
[@HIKAKIN_SYM](https://twitter.com/@HIKAKIN_SYM)は、ヒカキン動画のサムネイルに含まれる顔の位置を[Cloud Vision API](https://cloud.google.com/vision/?hl=ja)を使って認識し、シンメトリーさせ投稿するBotです。<br>
@SYM_HIKAKINをリスペクトしていますが作成者は異なり無関係です。<br>
ライセンスについては`LISENCE`をご覧ください。

## technologies
- Python3
- Cloud Vision API (Google Cloud Platform)

## updates
2017/1/1: 1.0 公開<br>
- 整えられるだけコードを整えて公開

2017/1/1: 2.0 OpenCV対応<br>
- **OpenCVを用いた顔検出も行えるようになりました。** MCVA(Microsoft Computer Vision API)を用いて顔を検出できなかった場合、より検出閾値の広い顔検出として利用することができます。しかし、完全に誤検出を防ぎたい場合はオフにすると良いです。

2017/2/11: 3.0 使用WebAPI変更<br>
- 顔認識に使用するWebAPIを**Computer Vision API**から**FaceAPI**に変更しました。より高度な検出を期待できるため、実験的に稼働Botの`use_cv`を`false`にしました。

2017/4/23: 4.0 ディレクトリ構造を変更<br>
- ディレクトリ構造を大幅に変更し、 `plugins` の内容のみを公開するようにしました。その他、小さな変更も加えました。

2017/11/2: 5.0 再開<br>
- 諸事情により止めていたBotをリファクタリングしたり使用APIを変更したりして再稼働しました。
- リポジトリを変更しました。[旧リポジトリ](https://github.com/HIKAKIN-SYM/Bot_TBFW)
- 顔検出を`Face API/OpenCV`から`Cloud Vision API`に変更しました。
- データベースをMySQLからSQLiteに変更しました。
- 依存BotフレームワークをTBFW後続の[PyChroner](https://github.com/NephyProject/PyChroner)に変更しました。

## setup
リポジトリを`PyChroner`の`plugins`内にcloneしてください。<br>
```bash
git clone git@github.com:HIKAKIN-SYM/Bot.git hikakin_sym
cd hikakin_sym
pip3 install -r requirements.txt
```
`config.json`/`secret`に必要なパラメータは以下のとおりです。

```json
{
    "hikakin_sym": {
      "youtube_key": "hogepiyo",
      "cloudvision_key": "hogepiyo"
    }
}
```