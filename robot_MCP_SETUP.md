# robot_MCP セットアップ

`robot_MCP` をローカルで起動し、MCP対応クライアントからSO-ARM101を操作するための手順です。先にルートの[README](README.md)に沿ってPython環境、LeRobot、実機のポートを確認してください。

## 1. 個体設定

シリアルポート、ロボット種別、カメラ番号を環境変数で指定します。キャリブレーション値や実際のUSB識別子をコミットしないでください。

```sh
export SO_ARM_PORT=/dev/cu.usbmodemXXXXXXXX
export SO_ARM_ROBOT_TYPE=so101
export SO_ARM_CAMERA_INDEX=0
```

## 2. 読み取り確認

```sh
source .venv/bin/activate
cd robot_MCP
python check_positions.py
```

最初に現在位置が読めることを確認します。続いて `python keyboard_controller.py` を使い、小さい動作で方向と制限を確認してください。

## 3. MCPサーバーの確認

```sh
mcp dev mcp_robot_server.py
```

Inspectorでツール一覧と読み取り操作を確認します。動作ツールを呼ぶ前に、アームの周囲を空けてください。

## 4. デスクトップクライアントへ登録

[設定例](claude_desktop_config.example.json)の `command` と `args` を、クローン先の絶対パスへ置き換えます。

```json
{
  "mcpServers": {
    "so-arm101": {
      "command": "/absolute/path/to/SO-ARM101/.venv/bin/python",
      "args": [
        "/absolute/path/to/SO-ARM101/robot_MCP/mcp_robot_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

既存の設定に `mcpServers` がある場合は、`so-arm101` の項目だけを追加します。クライアントを再起動後、まず状態取得を試してください。

## 5. CLIエージェント

使用するプロバイダーのキーをリポジトリ直下の `.env` に保存します。

```dotenv
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
OPENAI_API_KEY=
```

MCPサーバーを起動してから、別のターミナルで `python robot_MCP/agent.py` を実行します。画像を含むリクエストは高額になる場合があるため、プロバイダー側の上限を設定してください。

## 問題があるとき

- ポートが開かない: 別アプリが使用していないか、データ対応USBケーブルかを確認
- カメラが開かない: OSのカメラ権限と `config.py` のindexを確認
- import error: venvが有効か、LeRobotと `robot_MCP/requirements.txt` を導入済みか確認
- 動作方向が違う: 直ちに電源を切り、キャリブレーションと設定を見直す

復旧スクリプトを試す前に、現在値とエラーを保存し、対象サーボの仕様を確認してください。
