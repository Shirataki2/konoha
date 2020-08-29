---
title: Bot
description: 000 - Botに関する基本的な設定などです
---

<command 
  name="ping"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['!ping']">
<div>

`!ping`

通信遅延を計測します

**Websocket遅延**

Discordと双方向通信する際に使われる回線の遅延です

**API通信遅延**

Discordから情報を得るためのAPIサーバーの遅延です

**メッセージ送信遅延**

当BotからDIscordクライアントにメッセージを送信するのにかかる遅延です 

</div>
</command>


<command 
  name="?"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['@Konoha ?']">
<div>

`@Konoha ?`

サーバーでBotを呼び出す際のPrefixを確認できます

</div>
</command>

<command 
  name="prefix"
  :roles="[{name: 'サーバー管理者', color: 'orange'},{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!prefix $']">
<div>

`!prefix <new_prefix>`

サーバーでBotを呼び出す際のPrefixを変更します．

prefixは8文字以下である必要があります．

</div>
</command>

<command 
  name="invite"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['!invite']">
<div>

`!invite`

Botを招待するためのURLを表示します．

</div>
</command>

<command 
  name="timer"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['!timer 180']">
<div>

`!timer <seconds>`

指定した秒数待つタイマーをセットします．

秒数経過後にあなた宛てにメンションを送ります．

secondsは0以上10800以下である必要があります．

</div>
</command>

<command 
  name="guild"
  :aliases="['server']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!guild', '!server']">
<div>

`!guild`

サーバーの人数やチャンネル数などといった基本的な情報を表示します．

</div>
</command>

<command 
  name="user"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['!user @Someone', '!user']">
<div>

`!user [user]`

引数に指定したユーザー(指定しなかった場合は送信したユーザー)に関する情報を表示します．

</div>
</command>

<command 
  name="about"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['!about']">
<div>

`!about`

このBotに関する基本的な情報を返します．

</div>
</command>
