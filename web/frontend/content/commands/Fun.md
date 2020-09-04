---
title: Fun
description: 010 - ユーモラスなコマンド群です
---

<command 
  name="shellgei"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:shellgei echo Hello', 'k:shellgei \n```sh\nyes 高須クリニック\n```']"
  rate="10分あたり20回まで">
<div>

  `k:shellgei <source>`

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
  :usages="['k:translate JA Hello', 'k:translate DE 人民の人民による人民のための政治']"
  rate="2分あたり2回まで / 全サーバー合計10万字以下">
<div>

  `k:translate <target_lang> <text>`

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

<command 
  name="emocre"
  :aliases="['create_emoji']"
  :roles="[{name: 'サーバーOnly', color: 'green'}]"
  :usages="['k:emocre 完全;理解 red-accent-3 mincho-black', 'k:create_emoji わかる #3760f5 maru white']"
  rate="30秒あたり5回まで">
<div>

  `k:emocre <text> [color] [font] [bg_color]`

指定した文字から絵文字として使える128x128の画像を生成します．

文字は最大12文字まで指定可能です．デフォルトでは指定した文字は改行されませんが改行を示す文字"`;`"を`text`中に指定することで改行することができます．改行文字は12文字制限カウントには含まれません．

例:

`k:emocre 完全理解 red-accent-3 mincho-black`

![](https://cdn.discordapp.com/attachments/739863321590628474/750631514928054312/emoji.png)

`k:emocre 完全;理解 red-accent-3 mincho-black`

![](https://cdn.discordapp.com/attachments/739863321590628474/750631577633030144/emoji.png)


`color`と`bg_color`はそれぞれ文字と背景の色を指定します．

色の指定は[Vuetifyにおける色指定](https://vuetifyjs.com/ja/styles/colors/)を使用することが可能です．`red`や`blue-darken-2`などのように指定することで，文字色や背景色を指定することが可能です．

その他`#e95`や`#ff2e`，`#f35050`，`#e4e4e477`のように直接カラーコードを指定することも可能です．

`font`は文字のフォントを指定します．現在以下のフォントを使用可能です．

|引数名|フォント名|
|:--|:--|
|`gothic`|Noto Sans CJK jp Bold|
|`gothic-black`|Noto Sans CJK jp Black|
|`mincho`|Noto Serif CJK jp Bold|
|`mincho-black`|Noto Serif CJK jp Black|
|`maru`|Rounded M+ 1p Black|
|`851`|851チカラヅヨク|

</div>
</command>

