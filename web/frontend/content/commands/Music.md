---
title: Music
description: 800 - 音楽再生機能
---

<command 
  name="join"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!join']">

<div>

  `!join`

Botをボイスチャンネルへと入室させます．

コマンドを打った人のチャンネルへ入室するのであらかじめ，コマンドを打つ人はボイスチャンネルに入室している必要があります．

</div>

</command>

<command 
  name="leave"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!leave']">

<div>

  `!leave`

Botをボイスチャンネルから退出させます．

プレイリストに曲がある場合，すべて削除されます．

</div>

</command>

<command 
  name="volume"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!volume 100', '!volume 30']">

<div>

  `!volume <volume>`

再生音量を`0～300 %`までパーセントで指定して変更します．

</div>

</command>

<command 
  name="pause"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!pause']">

<div>

  `!pause`

音楽再生を一時停止します．

</div>

</command>

<command 
  name="resume"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!resume']">

<div>

  `!resume`

音楽再生を再開します．

</div>

</command>

<command 
  name="play"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!play 潮風']">

<div>

  `!play <曲名>`

音楽を検索し，プレイリストに挿入します．

</div>

</command>

<command 
  name="stop"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!stop']">

<div>

  `!stop`

音楽の再生を止め，プレイリストを空にします．

</div>

</command>

<command 
  name="skip"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!skip']">

<div>

  `!skip`

曲をスキップします．

</div>

</command>

<command 
  name="queue"
  :aliases="['playlist']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!queue']">

<div>

  `!queue`

プレイリストを表示します

</div>

</command>

<command 
  name="shuffle"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!shuffle']">

<div>

  `!shuffle`

プレイリストをシャッフルします

</div>

</command>

<command 
  name="remove"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!remove 2']">

<div>

  `!remove <index>`

プレイリストの`index`番目の曲を削除します．

指定方法は1オリジンです．(先頭の曲は0番目ではありません)

</div>

</command>

<command 
  name="loop"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!loop']">

<div>

  `!loop`

再生中の曲をループします

</div>

</command>

<command 
  name="loop_queue"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!loop_queue']">

<div>

  `!loop_queue`

プレイリスト中の曲をループします

</div>

</command>

<command 
  name="rec"
  :roles="[{name: 'サーバーOnly', color: 'green'},{name: 'メッセージ編集権限', color: 'purple'}]"
  :usages="['!rec']">

<div>

  `!rec`

ボイスチャットの録音を開始します．

最大30秒まで録音することが可能です．

</div>

</command>

<command 
  name="recstop"
  :roles="[{name: 'サーバーOnly', color: 'green'},{name: 'メッセージ編集権限', color: 'purple'}]"
  :usages="['!recstop']">

<div>

  `!recstop`

ボイスチャットの録音を終了します．

終了後録音したmp3ファイルが送信されます．

</div>

</command>

