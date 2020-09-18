---
title: Reminder
description: 005 -
---

<command 
  name="reminder init"
  :aliases="['rem init', 'rem i']"
  :roles="[{name: 'サーバー管理者', color: 'orange'}, {name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:rem i']">
<div>

  `k:reminder init`

サーバーに対して設定したリマインダーの通知送信先を設定します．

このコマンドが送られたチャンネルが送信先として設定されます．

</div>

</command>

<command 
  name="reminder create"
  :aliases="['rem create', 'rem c']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:rem c']">
<div>

  `k:reminder create`

新たなリマインダーを作成します．

このコマンドを実行するとまずイベントの名前が聞かれ，その後日時が聞かれます．これら2つの質問に回答することで新規リマインダーが作成されます．

</div>

</command>


<command 
  name="reminder list"
  :aliases="['rem list', 'rem l']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:rem l']">
<div>

  `k:reminder list`

未来に開催予定のリマインダーの一覧を表示します．

</div>

</command>


<command 
  name="reminder delete"
  :aliases="['rem delete', 'rem d']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:rem d 00004']">
<div>

  `k:reminder delete <id>`

指定したIDのリマインダーのを削除します．

</div>

</command>

