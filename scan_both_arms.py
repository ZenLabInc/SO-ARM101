"""
2本のアームのポートとモーターIDを一括確認するスクリプト。
"""
import os

import scservo_sdk as scs

PORTS = [
    os.environ.get("SO_ARM_FOLLOWER_PORT"),
    os.environ.get("SO_ARM_LEADER_PORT"),
]
if not all(PORTS):
    raise SystemExit("SO_ARM_FOLLOWER_PORTとSO_ARM_LEADER_PORTを設定してください")

MOTOR_NAMES = {
    1: "shoulder_pan",
    2: "shoulder_lift",
    3: "elbow_flex",
    4: "wrist_flex",
    5: "wrist_roll",
    6: "gripper",
}

for port in PORTS:
    print(f"\n{'='*50}")
    print(f"ポート: {port}")
    print(f"{'='*50}")

    ph = scs.PacketHandler(0)
    port_handler = scs.PortHandler(port)

    if not port_handler.openPort():
        print("  接続失敗")
        continue

    port_handler.setBaudRate(1_000_000)

    found = []
    for motor_id in range(1, 8):
        model, comm, error = ph.ping(port_handler, motor_id)
        if comm == scs.COMM_SUCCESS:
            name = MOTOR_NAMES.get(motor_id, f"unknown_{motor_id}")
            found.append(motor_id)
            print(f"  ID {motor_id} ({name}): OK")

    print()
    if sorted(found) == list(range(1, len(found) + 1)) and len(found) == 6:
        print(f"  => 全6モーター検出 ✓")
    else:
        print(f"  => 検出: {found} （6台揃っていない場合は確認が必要）")

    port_handler.closePort()
