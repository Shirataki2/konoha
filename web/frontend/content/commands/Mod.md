---
title: Mod
description: 006 -
---

<command 
  name="ban"
  :roles="[{name: 'BAN権限', color: 'red darken-3'}]"
  :usages="['k:ban @User', 'k:ban @User1 @User2']">
<div>

  `k:ban <user>...`

ユーザーをBANします．あなた，もしくはこのBotより高いロールのメンバーはBANすることはできません．

</div>
</command>

<command 
  name="unban"
  :roles="[{name: 'BAN権限', color: 'red darken-3'}]"
  :usages="['k:unban @User', 'k:unban @User1 @User2']">
<div>

  `k:unban <user>...`

ユーザーのBANを解除します．

</div>
</command>

<command 
  name="kick"
  :roles="[{name: 'KICK権限', color: 'orange darken-3'}]"
  :usages="['k:kick @User', 'k:kick @User1 @User2']">
<div>

  `k:kick <user>...`

ユーザーをサーバーから追放します．あなた，もしくはこのBotより高いロールのメンバーはキックすることはできません．

</div>
</command>

<command 
  name="tempban"
  :roles="[{name: 'BAN権限', color: 'red darken-3'}]"
  :usages="['k:tempban @User 10分', 'k:ban @User1 @User2 7days']">
<div>

  `k:tempban <user>... <duration>`

ユーザーを指定した期間BANします．期間は`1分`や`2時間`のように指定するか，`180`のように数字のみで秒数を指定することができます．


あなた，もしくはこのBotより高いロールのメンバーはBANすることはできません．

</div>
</command>
