---
title: Global Chat
description: 003 - 他のサーバーの人と会話できちゃう機能です
---

<command 
  name="gc register"
  :roles="[{name: 'サーバー管理者', color: 'orange'}, {name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:gc register #グローバルチャット', 'k:gc register']">

<div>

  `k:gc register [チャンネル名]`

引数に指定したチャンネルをグローバルチャットの送受信先に設定します．

他のサーバーがグローバルチャットチャンネルに登録したチャンネルに何か投稿した際，Botを通じて自分が所属するサーバーのグローバルチャットチャンネルへとメッセージが届きます．(逆も同様です)

</div>

</command>

<command 
  name="gc unregister"
  :roles="[{name: 'サーバー管理者', color: 'orange'}, {name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:gc unregister']">

<div>

  `k:gc unregister`

グローバルチャットの登録を解除し，以降他のサーバーからのメッセージを受信しないように設定します．

</div>

</command>

