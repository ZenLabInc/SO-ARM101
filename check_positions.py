"""
各モーターの現在位置を読み取り専用で表示する診断スクリプト。
キャリブレーション前に各ジョイントが適切な中間位置にあるか確認するために使用。
設定済みのHoming_Offsetは変更しない。
"""
import os

import scservo_sdk as scs

port = os.environ.get("SO_ARM_PORT")
if not port:
    raise SystemExit("SO_ARM_PORTを設定してください。例: export SO_ARM_PORT=/dev/cu.usbmodemXXXXXXXX")
MOTOR_NAMES = {
    1: "shoulder_pan",
    2: "shoulder_lift",
    3: "elbow_flex",
    4: "wrist_flex",
    5: "wrist_roll",
    6: "gripper",
}
HALF_TURN = 2047   # STS3215 の中間値
MAX_OFFSET = 2047  # Homing_Offset レジスタの最大絶対値

ph = scs.PacketHandler(0)
port_handler = scs.PortHandler(port)

if not port_handler.openPort():
    print("ポートを開けませんでした")
    exit(1)
port_handler.setBaudRate(1_000_000)

addr_present_pos = 56
print(f"{'ID':>3} {'名前':<14} {'現在値':>6} {'中間(2047)との差':>16} {'キャリブ可否':>10}")
print("-" * 60)
for motor_id, name in MOTOR_NAMES.items():
    pos, comm, error = ph.read2ByteTxRx(port_handler, motor_id, addr_present_pos)
    if comm != scs.COMM_SUCCESS:
        print(f"  ID {motor_id} ({name}): 読み取り失敗")
        continue
    offset = pos - HALF_TURN
    ok = abs(offset) <= MAX_OFFSET
    status = "範囲内" if ok else "範囲外 <- 設定を確認"
    print(f"{motor_id:>3} {name:<14} {pos:>6}  offset={offset:>+6}  {status}")

print()
print("※ 表示値にはサーボに保存されたHoming_Offsetが反映される場合があります")
print("※ 範囲外の場合は電源を切り、公式手順と現在の設定を確認してください")

port_handler.closePort()
