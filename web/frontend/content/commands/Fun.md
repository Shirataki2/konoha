---
title: Fun
description: 010 - ユーモラスなコマンド群です
---

<command 
  name="shellgei"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['!shellgei echo Hello', '!shellgei \n```sh\nyes 高須クリニック\n```']"
  rate="10分あたり20回まで">
<div>

  `!shellgei <source>`

シェルスクリプトを実行しちゃう危険なコマンド

基本的な仕様はシェル芸Botと同様です．

1. ネットワークインターフェースはローカルループバックのみ
2. 最大実行時間は20秒
3. 出力は最大500字/20行
4. 添付ファイルは`/media`にアップロードされる
5. `/images`フォルダ下に画像を保存した場合最大4枚まで送信される
6. 5MB以上の大きさのファイルは作成不可
7. メモリは256MBまで利用可能
8. シェル芸の[Dockerコンテナ](https://hub.docker.com/r/theoldmoon0602/shellgeibot)上で動かされます．なので，`rm -rf /`とかは効かないようになってるけど脆弱性は突かないであげてね！

</div>
</command>

<command 
  name="translate"
  :roles="[{name: '全員', color: 'blue'}]"
  :usages="['!translate JA Hello', '!translate DE 人民の人民による人民のための政治']"
  rate="2分あたり2回まで / 全サーバー合計10万字以下">
<div>

  `!translate <target_lang> <text>`

[DeepL API](https://www.deepl.com/)を利用して文章を翻訳します．

第一引数の`target_lang`は翻訳先の言語を以下の形式で指定します．

- "DE" - ドイツ語
- "EN-GB" - 英語（イギリス）
- "EN-US" - 英語（アメリカ）
- "EN" - 英語
- "FR" - フランス語
- "IT" - イタリア語
- "JA" - 日本語
- "ES" - スペイン語
- "NL" - オランダ語
- "PL" - ポーランド語
- "PT-PT" - ポルトガル語（ブラジルポルトガル語を除く）
- "PT-BR" - ポルトガル語（ブラジル）
- "PT" - ポルトガル語
- "RU" - ロシア語
- "ZH" - 中国語

</div>
</command>

