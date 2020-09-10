---
title: Reaction
description: 002 - リアクションで色々行う機能です
---

<command 
  name="vote"
  :aliases="['poll', 'vc', 'pc']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:vote バナナはおやつに入りますか Yes No', 'k:pc 集合時間は何時にしますか 0時 1時 2時 3時']">
<div>

  `k:vote <description> <option1> [option2] [option3] ...`

投票を作成する機能です

`description`で投票のお題を決めて以降の`option`で選択肢を入力します．

選択肢は1つ以上26個以下である必要があります．

</div>
</command>

<command 
  name="vote_list"
  :aliases="['poll_list', 'vl', 'pl']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:vote_list', 'k:vl']">
<div>

  `k:vote_list`

作成した投票の一覧が作成されます．

</div>
</command>

<command 
  name="vote_analyze"
  :aliases="['poll_analyze', 'va', 'pa']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:vote_analyze 6f7acf', 'k:va 6f7acf']"
  rate="2分あたり5回まで">
<div>

  `k:vote_analyze <ID>`

指定した投票IDの投票に関して分析を行います．

</div>
</command>
