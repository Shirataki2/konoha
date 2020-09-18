---
title: Starboard
description: 015 -
---

<command 
  name="starboard enable"
  :roles="[{name: 'サーバー管理者', color: 'orange'}, {name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:starboard enable #starboard 5', 'k:starboard enable #お得情報']">
<div>

  `k:starboard enable <channel> [threshold=1]`

サーバーに対してスターボード機能を有効化させます．

スターボード機能とは，メッセージに対して一定数以上の⭐のリアクションが付いたメッセージを別のチャンネルへBotが代理投稿し，目立つ形で表示することができる機能です．

第二引数の`threshold`で掲載に必要な⭐のリアクションの数を指定します．何も指定しない場合には`1`個以上の⭐のリアクションがついたメッセージを掲載します．

</div>

</command>

<command 
  name="starboard disable"
  :roles="[{name: 'サーバー管理者', color: 'orange'}, {name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:starboard disable']">
<div>

  `k:starboard disable`

サーバーに対してスターボード機能を無効化させます．

</div>

</command>
