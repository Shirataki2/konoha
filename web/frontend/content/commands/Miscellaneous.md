---
title: Miscellaneous
description: 111 -
---

<command 
  name="echo"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['k:echo Hello, World!', 'k:echo @everyone']">
<div>

  `k:echo <text>`

オウム返しをします．

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
