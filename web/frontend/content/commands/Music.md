---
title: Music
description: 004 - 音楽再生機能
---

<command 
  name="connect"
  :aliases="['join']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:connect', 'k:join #ボイスチャンネル']">

<div>

  `k:join [voice_channel]`

Botをボイスチャンネルへと入室させます．

引数にボイスチャンネルを指定しなかった場合，コマンドを打った人のチャンネルへ入室するのであらかじめ，コマンドを打つ人はボイスチャンネルに入室している必要があります．

</div>

</command>

<command 
  name="play"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:play 潮風']">

<div>

  `k:play <曲名>`

音楽を検索し，プレイリストに挿入します．

</div>

</command>

<command 
  name="stop"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:stop']">

<div>

  `k:stop`

Botをボイスチャンネルから退出させます．

プレイリストに曲がある場合，すべて削除されます．

</div>

</command>

<command 
  name="volume"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:volume 100', 'k:volume 30']">

<div>

  `k:volume <volume>`

再生音量を`0～100 %`までパーセントで指定して変更します．

</div>

</command>

<command 
  name="pause"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:pause']">

<div>

  `k:pause`

音楽再生を一時停止します．

</div>

</command>

<command 
  name="resume"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:resume']">

<div>

  `k:resume`

音楽再生を再開します．

</div>

</command>


<command 
  name="skip"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:skip']">

<div>

  `k:skip`

曲をスキップします．

</div>

</command>

<command 
  name="playlist"
  :aliases="['queue']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:playlist']">

<div>

  `k:playlist`

プレイリストを表示します

</div>

</command>

<command 
  name="shuffle"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:shuffle']">

<div>

  `k:shuffle`

プレイリストをシャッフルします

</div>

</command>

<command 
  name="remove"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:remove 2']">

<div>

  `k:remove <index>`

プレイリストの`index`番目の曲を削除します．

指定方法は1オリジンです．(先頭の曲は0番目ではありません)

</div>

</command>

<command 
  name="loop"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:loop']">

<div>

  `k:loop`

プレイリスト中の曲をループします

</div>

</command>

<command 
  name="loop_single_track"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:loop_single_track']">

<div>

  `k:loop_single_track`

再生中の曲をループします


</div>

</command>

<!-- <command 
  name="rec"
  :roles="[{name: 'サーバーOnly', color: 'green'},{name: 'メッセージ管理権限', color: 'purple'}]"
  :usages="['k:rec']">

<div>

  `k:rec`

ボイスチャットの録音を開始します．

最大30秒まで録音することが可能です．

</div>

</command>

<command 
  name="recstop"
  :roles="[{name: 'サーバーOnly', color: 'green'},{name: 'メッセージ管理権限', color: 'purple'}]"
  :usages="['k:recstop']">

<div>

  `k:recstop`

ボイスチャットの録音を終了します．

終了後録音したmp3ファイルが送信されます．

</div>

</command>
 -->
