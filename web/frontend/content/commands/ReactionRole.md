---
title: Reaction Role
description: 020 -
---

<command 
  name="role_panel new"
  :aliases="['rp new']"
  :roles="[{name: 'Role管理権限', color: 'cyan darken-1'}]"
  :usages="['k:rp new 好きな果物は？ 🍎 @リンゴ 🍇 @ぶどう', 'k:rp new どっちが好き？ 🍄 @きのこ 🎋 @たけのこ']">
<div>

  `k:role_panel new <description> <emoji1> <role1> [emoji2] [role2] ...`


新たにロールパネルを作成します．

リアクションをした際にそのリアクションをした相手に対して，指定したロールが付与されます．

一つのパネルに使用可能なロールの数は20個までです．

パネルの説明と，1対以上の絵文字とロールは必須です．

</div>

</command>

<command 
  name="role_panel simple"
  :aliases="['rp simple']"
  :roles="[{name: 'Role管理権限', color: 'cyan darken-1'}]"
  :usages="['k:rp simple 好きな果物は？ @リンゴ @ぶどう', 'k:rp simple @きのこ @たけのこ']">
<div>

  `k:role_panel simple [description] <role1> [role2] ...`


新たにロールパネルを作成します．

simpleの場合は選択肢として使用される絵文字がA,B,C...になります．

一つのパネルに使用可能なロールの数は20個までです．

パネルの説明は必須ではありません．

</div>

</command>

<command 
  name="role_panel num"
  :aliases="['rp num']"
  :roles="[{name: 'Role管理権限', color: 'cyan darken-1'}]"
  :usages="['k:rp num 好きな果物は？ @リンゴ @ぶどう', 'k:rp num @きのこ @たけのこ']">
<div>

  `k:role_panel num [description] <role1> [role2] ...`


新たにロールパネルを作成します．

numの場合は選択肢として使用される絵文字が1,2,3...になります．

一つのパネルに使用可能なロールの数は<u>**10**</u>個までです．

パネルの説明は必須ではありません．

</div>

</command>

<command 
  name="role_panel list"
  :aliases="['rp list']"
  :roles="[{name: 'Role管理権限', color: 'cyan darken-1'}]"
  :usages="['k:rp list']">
<div>

  `k:role_panel list`


作成したロールパネルの一覧を見ることができます．

</div>

</command>


<command 
  name="role_panel delete"
  :aliases="['rp delete']"
  :roles="[{name: 'Role管理権限', color: 'cyan darken-1'}]"
  :usages="['k:rp delete 3af86eab']">
<div>

  `k:role_panel delete <id>`


指定したIDのロールパネルを削除します．一覧から削除され，元のメッセージも削除されます．

</div>

</command>

<command 
  name="role_panel add"
  :aliases="['rp add']"
  :roles="[{name: 'Role管理権限', color: 'cyan darken-1'}]"
  :usages="['k:rp add 3af86eab 🍋 @レモン']">
<div>

  `k:role_panel add <id> <emoji> <role>`


指定したIDのロールパネルに，指定した絵文字を追加します．

たとえば下の使用例では，元のパネルが「🍎 @リンゴ 🍇 @ぶどう」の対でロールを付与するパネルであった場合，あらたに🍋が選択肢として追加され，「🍎 @リンゴ 🍇 @ぶどう 🍋 @レモン」のように更新されます．

</div>

</command>


<command 
  name="role_panel remove"
  :aliases="['rp remove']"
  :roles="[{name: 'Role管理権限', color: 'cyan darken-1'}]"
  :usages="['k:rp remove 3af86eab 🍎']">
<div>

  `k:role_panel remove <id> <emoji> <role>`


指定したIDのロールパネルから，指定した絵文字を削除します．

たとえば下の使用例では，元のパネルが「🍎 @リンゴ 🍇 @ぶどう」の対でロールを付与するパネルであった場合，🍎が選択肢から削除され，「🍇 @ぶどう」のように更新されます．

</div>

</command>
