---
title: Economy
description: 040 -
---

<command 
  name="daily"
  rate="ユーザーあたり一日一度まで(日本時間朝4時にリセット)"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:daily']">

<div>

  `k:daily`

サーバー内疑似通貨のデイリーログインボーナスを貰えます．

リアルマネーには換算されませんが沢山ログインして稼ごう！！

</div>

</command>

<command 
  name="wallet"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:wallet']">

<div>

  `k:wallet`

サーバー内疑似通貨の所持量を表示します．

</div>

</command>
