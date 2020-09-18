---
title: Bot
description: 000 - Botに関する基本的な設定などです
---

<command 
  name="ping"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['k:ping']">
<div>

`k:ping`

通信遅延を計測します

**Websocket遅延**

Discordと双方向通信する際に使われる回線の遅延です

**API通信遅延**

Discordから情報を得るためのAPIサーバーの遅延です

**メッセージ送信遅延**

当BotからDIscordクライアントにメッセージを送信するのにかかる遅延です 

**データベース通信遅延**

当サービスの利用するデータベースからデータを得るためにかかる遅延です．

</div>
</command>

<command 
  name="invite"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['k:invite']">
<div>

`k:invite`

Botを招待するためのURLを表示します．

</div>
</command>

<command 
  name="timer"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['k:timer 180', 'k:timer 5時間']">
<div>

`k:timer <duration>`

指定した時間待つタイマーをセットします．

指定時間経過後にあなた宛てにメンションを送ります．

`duration`は`1分`や`2時間`のように指定するか，`180`のように数字のみで秒数を指定することができます．

</div>
</command>

<command 
  name="guild"
  :aliases="['server']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:guild', 'k:server']">
<div>

`k:guild`

サーバーの人数やチャンネル数などといった基本的な情報を表示します．

</div>
</command>

<command 
  name="user"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['k:user @Someone', 'k:user']">
<div>

`k:user [user]`

引数に指定したユーザー(指定しなかった場合は送信したユーザー)に関する情報を表示します．

</div>
</command>

<command 
  name="about"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['k:about']">
<div>

`k:about`

このBotに関する基本的な情報を返します．

</div>
</command>
