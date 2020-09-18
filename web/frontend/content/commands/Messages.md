---
title: Messages
description: 014 -
---

<command 
  name="expand"
  :roles="[{name: 'サーバー管理者', color: 'orange'}, {name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:expand on', 'k:expand off']">

<div>

  `k:expand <on もしくは off>`

メッセージの中にDiscordのメッセージへのリンクが含まれていた際にそのリンクを辿って，元のメッセージの内容を自動で投稿するかを指定します．

`on`にすると投稿が行われるようになります．デフォルトでは`off`の設定となっています．

</div>

</command>

<command 
  name="purge"
  :roles="[{name: 'メッセージ管理権限', color: 'purple'}, {name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:purge 10', 'k:purge 1000']">

<div>

  `k:purge <num>`

指定した件数のテキストチャンネルのメッセージを一括で消去します．

件数は最大1000件まで指定可能ですが，APIの制限上100件ずつ消去され，なおかつ14日以上前の投稿については削除されません．

</div>

</command>

<command 
  name="purge bot"
  :roles="[{name: 'メッセージ管理権限', color: 'purple'}, {name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:purge bot 10', 'k:purge bot 1000']">

<div>

  `k:purge bot <num>`

Botが投稿した，指定した件数のメッセージを一括で消去します．

件数は最大1000件まで指定可能ですが，APIの制限上100件ずつ消去され，なおかつ14日以上前の投稿については削除されません．

</div>

</command>


<command 
  name="purge user"
  :roles="[{name: 'メッセージ管理権限', color: 'purple'}, {name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:purge user 10', 'k:purge user 1000']">

<div>

  `k:purge user <num>`

Botではないユーザーが投稿した，指定した件数のメッセージを一括で消去します．

件数は最大1000件まで指定可能ですが，APIの制限上100件ずつ消去され，なおかつ14日以上前の投稿については削除されません．

</div>

</command>

