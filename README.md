# うちの仔

## 概要
PythonのフレームワークのDjangoを主に使用して作りました。

学習済みデータセットモデルを使用して、指定したクラスがある画像ファイルの検出をローカルフォルダ内から行います。

検出された画像ファイルは画面に表示され、好きなフォルダに移動させることができます。

## 使い方
| 最初の画面 |
| ----- |
| ![サンプル画像](https://github.com/user-attachments/assets/d3f422a4-d87b-42aa-b000-9d24ce21441d) |

| ホーム画面 | 結果 |
| ----- | ----- |
| ![ホーム画面 サンプル](https://github.com/user-attachments/assets/021cfebd-a722-45e7-abc2-5ba17923bf6e) | ![](static/images/sample1.png) |
| 検索履歴が無ければファイルを選択します。 | 表示された結果から探したいクラス名をクリックします。 |

| 指定クラスの画像検索画面 | 結果 |
| ----- | ----- |
| ![画像ファイルの検索画面](https://github.com/user-attachments/assets/cb3254f2-1133-47b1-905f-60eebcc3f96c) | ![](static/images/sample2.png) |
| 探したい画像フォルダを選びます。 | 移動させる画像にチェックを入れて移動先のフォルダを選ぶと移動します。移動した画像は画面から消えます。 |


## 使用技術
- Python 3.12.4
- Django 5.0.6
- ultralytics 8.2.27
- django-bootstrap5 24.2
- MySQL 8.0.31
- jQuery 3.7.1
- paginathing.js

## ライセンス
[AGPL-3.0 License](LICENSE)
