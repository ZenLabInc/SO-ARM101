# SO-ARM101 ローカル制御・MCP実験

[English](README.en.md)

低価格ロボットアーム SO-ARM101 をmacOSからセットアップし、LeRobotによる診断・テレオペレーションと、MCP対応AIクライアントからの自然言語操作を試すための実験リポジトリです。

このリポジトリには実機を動かすコードが含まれます。最初は電源を切った状態で配線と可動域を確認し、非常停止できる人がアームのそばにいる状態で低速から試してください。

## できること

- SO-ARM101のUSBポートとサーボIDの確認
- エンコーダ位置とモーターモードの診断
- LeRobotの公式CLIを使ったキャリブレーション、テレオペレーション、記録
- `robot_MCP` を使ったキーボード操作とMCP経由の自然言語操作
- Claude、Gemini、OpenAI対応エージェントの実験

## 構成

| パス | 内容 |
|---|---|
| `lerobot/` | Hugging Face LeRobotのGit submodule |
| `robot_MCP/` | Ilia Larchenko氏のrobot_MCPを元にしたApache-2.0コードとSO-ARM101対応変更 |
| `scan_motors.py` | 1本のアームに接続されたサーボIDを確認 |
| `scan_both_arms.py` | リーダー・フォロワー両方を確認 |
| `check_positions.py` | 現在位置を読み取り、キャリブレーション前の状態を確認 |
| `reset_motor_mode.py` | モードと原点オフセットを変更する復旧用スクリプト |
| `fix_homing_offsets.py` | 原点オフセットを直接修正する復旧用スクリプト |
| `robot_MCP_SETUP.md` | MCPの設定と確認手順 |

## 必要なもの

- SO-ARM101。リーダーとフォロワーの2本構成を推奨
- データ通信対応USBケーブル
- macOSまたはLinux
- Python 3.12
- Git
- 実機を安全に置ける平らな作業台

手順はLeRobotの更新で変わることがあります。実行前に[公式SO-101ガイド](https://huggingface.co/docs/lerobot/so101)も確認してください。

## 1. クローン

```sh
git clone --recurse-submodules https://github.com/ZenLabInc/SO-ARM101.git
cd SO-ARM101
```

通常の `git clone` を実行済みなら、次でLeRobotを取得できます。

```sh
git submodule update --init --recursive
```

## 2. Python環境

venvまたはcondaでPython 3.12の環境を用意します。以下はvenvの例です。

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "lerobot[feetech]"
python -m pip install -r robot_MCP/requirements.txt
```

LeRobotの依存関係は大きく、初回導入には時間と空き容量が必要です。

## 3. USBポートを確認

```sh
ls /dev/cu.usbmodem* 2>/dev/null || ls /dev/ttyACM* 2>/dev/null
```

macOSでは通常 `/dev/cu.*`、Linuxでは通常 `/dev/ttyACM*` を使用します。抜き差し前後の差分で、リーダーとフォロワーを特定してください。

診断スクリプトには環境変数でポートを渡します。

```sh
export SO_ARM_PORT=/dev/cu.usbmodemXXXXXXXX
python scan_motors.py
python check_positions.py
```

2本を確認する場合:

```sh
export SO_ARM_FOLLOWER_PORT=/dev/cu.usbmodemXXXXXXXX
export SO_ARM_LEADER_PORT=/dev/cu.usbmodemYYYYYYYY
python scan_both_arms.py
```

## 4. LeRobotで初期設定

モーターID設定とキャリブレーションはアームを動かします。公式ガイドに従い、対象ポートを取り違えないよう1本ずつ実行してください。

```sh
lerobot-setup-motors \
  --robot.type=so101_follower \
  --robot.port="$SO_ARM_FOLLOWER_PORT"

lerobot-calibrate \
  --robot.type=so101_follower \
  --robot.port="$SO_ARM_FOLLOWER_PORT" \
  --robot.id=my_follower
```

リーダー側は `--teleop.type=so101_leader` を使います。コマンド引数はインストールしたLeRobot版の `--help` でも確認してください。

## 5. MCPを使う

詳細は [robot_MCP_SETUP.md](robot_MCP_SETUP.md) を参照してください。まず `robot_MCP/check_positions.py` とキーボード操作を試し、可動方向と制限を確認してからAIクライアントへ接続します。

LLM対応エージェントを使う場合は、必要なAPIキーを `.env` に置きます。`.env` はGit管理されません。APIへ画像と会話が送信され、各社の利用料金が発生する場合があります。

## 安全上の注意

- 人、動物、壊れ物から十分に離して実行してください。
- 初回はアームを固定せず、いつでも電源を切れる状態で小さく動かしてください。
- `reset_motor_mode.py` と `fix_homing_offsets.py` はサーボの設定値を書き換えます。診断用ではありません。
- キャリブレーションJSON、USB識別子、カメラ番号は個体・PCごとに異なります。公開リポジトリへ追加しないでください。
- AIの指示をそのまま安全な動作とみなさず、MCPツール側の移動量制限と人による監視を併用してください。

## 検証

実機なしで構文だけ確認する場合:

```sh
python -m compileall -q \
  scan_motors.py scan_both_arms.py check_positions.py \
  reset_motor_mode.py fix_homing_offsets.py robot_MCP
```

`robot_MCP/tests/` は依存パッケージを導入後に実行できます。実機試験では一度に一つの操作を行い、使用したLeRobot版、ポート、キャリブレーション、結果をローカルに記録してください。

## 出典とライセンス

- `lerobot/` は[Hugging Face LeRobot](https://github.com/huggingface/lerobot)をGit submoduleとして参照し、同プロジェクトのライセンスに従います。
- `robot_MCP/` は[IliaLarchenko/robot_MCP](https://github.com/IliaLarchenko/robot_MCP)を元にしており、同ディレクトリの[Apache License 2.0](robot_MCP/LICENSE)に従います。
- ルートの補助スクリプトと文書には、別途明示された場合を除き著作権が留保されています。
