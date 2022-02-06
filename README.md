# 何をするツールなのか
[ADDress](https://address.love/)のサイトから自分が予約している住宅をiCal形式で取得できるようにしています。

# 使い方
Dokcerなどのコンテナを走らせる環境が必要です。

```
docker build . -t address_ical
docker run -d -p 5000:5000 -e ADDRESS_USER=<ADDressのユーザ名> -e ADDRESS_PASSWORD=<ADDressのパスワード> address_ical:latest
```

iCalに対応しているカレンダーアプリでカレンダー登録をします。
上記のdocker runで動作させた場合は以下のURLかiCalのURLになります。

```
http://<docker host:5000/address.ics
```

# 注意点
認証情報は環境変数で渡すようにしているので外部からアクセスできるようにする場合は注意してください。
認証なしでカレンダー情報が公開されてしまいます。自宅などのPCやNASサーバで運用することをお勧めします。
