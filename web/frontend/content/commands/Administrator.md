---
title: Administrator
description: 999 - Botの管理用のコマンドです
---

<command 
name="reload"
:roles="[{name: 'Bot管理者', color: 'red'}]"
:usages="['k:reload']">
<div>

Botの機能拡張を再読み込みします

</div>
</command>

<command 
name="sql"
:roles="[{name: 'Bot管理者', color: 'red'}]"
:usages="[
  'k:sql SELECT * FROM guild;',
]">
<div>

SQL文をそのまま実行します．

データを獲得した場合は表の形式で描画されます．

</div>
</command>

<command 
name="error_log"
:aliases="['e']"
:roles="[{name: 'Bot管理者', color: 'red'}]"
:usages="[
  'k:error_log 91527c8535f12e9ef001447d',
  'k:e 91527c8535f12e9ef001447d',
]">
<div>

エラーIDから起こったエラーの詳細を得ます．

</div>
</command>

<command 
name="status"
:roles="[{name: 'Bot管理者', color: 'red'}]"
:usages="[
  'k:status',
]">
<div>

Botを稼働しているホストのパソコンの状態を表示します

CPU使用量/メモリ使用量/ストレージ使用量などが返されます

</div>
</command>
