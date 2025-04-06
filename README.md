# read-fidelity-pdf.py


Fidelity からダウンロードした複数の Statement PDF ファイルを一括で読んで配当と売買取引の情報を CSV 出力するプログラム。引数に Statement PDF ファイルのあるフォルダを指定。

実行例:
```
$ python3 read-fidelity-pdf.py ~/docs/Fidelity
種類,日付,名前,価格,税金
配当,2023/08/31,FIDELITY GOVERNMENT CASH RESERVES,4.28,0.0
配当,2024/09/30,ABC COM,29.68,2.97
配当,2023/11/30,FIDELITY GOVERNMENT CASH RESERVES,3.94,0.0

種類,日付,名前,量,価格,総コスト,取引コスト,総額,損益
買付,2025/03/18,ABC COM RSU####,2.000,188.67000,,,3773.34,
売却,2025/03/19,ABC COM,2.000,9.99,288.16,0.1,279.88,-8.27
```
事前に pypdf のインストールが必要:
```
$ pip3 install pypdf
```
おすすめポイント:
- 確定申告の時に1つづつ Statement PDF ファイルを読まなくてよい。
- Statement PDF は配当や売買の情報が「月/日」の日付だけどPDFのページヘッダにある年情報を加えてるので「年/月/日」で配当や売買のレコードを扱える。
