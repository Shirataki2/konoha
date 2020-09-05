---
title: Global Chat
description: 030 - 他のサーバーの人と会話できちゃう機能です
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

グローバルチャットの登録を解除し，以降他のサーバーからのメッセージを自身しないように設定します．

</div>

</command>

<command 
  name="gc report"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['k:gc report @User', 'k:gc report 334017809090740224']">

<div>

  `k:gc report <ユーザー>`

指定したユーザーを報告します．

第一引数のユーザーは@Userのようにメンションをするか，ユーザーネームを入力するか，直接ユーザーIDを入力(開発者向け)するなどで入力することで特定ができます．

グローバルチャット内で何か不審な行動をしているユーザーがいた際に利用してください．

このコマンドを打つと，報告理由を申すように質問をしてきますがその際にはスクリーンショットのURLなど特定が容易になる資料等を載せてください．

</div>

</command>

