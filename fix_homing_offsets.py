"""
マルチターン値になったモーターのHoming_Offsetを直接書き込むことで
lerobot-calibrate が通るようにするスクリプト。

STS3215のHoming_Offsetは符号絶対値11bit (最大±2047) だが、
生の位置値を % 4096 してから計算することで回避する。

Present_Position = (raw_encoder % 4096) - Homing_Offset
を逆解きして、calibrate後に Present_Position ≒ 2047 になるように設定する。
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

ADDR_TORQUE_ENABLE  = 40
ADDR_LOCK           = 55
ADDR_HOMING_OFFSET  = 31  # 2byte, 符号絶対値 (bit11=符号)
ADDR_PRESENT_POS    = 56

ph = scs.PacketHandler(0)
port_handler = scs.PortHandler(port)

if not port_handler.openPort():
    print("ポートを開けませんでした")
    exit(1)
port_handler.setBaudRate(1_000_000)


def encode_sign_magnitude(value: int, sign_bit_index: int = 11) -> int:
    """符号絶対値エンコード（STS3215 Homing_Offset用）"""
    max_magnitude = (1 << sign_bit_index) - 1
    if abs(value) > max_magnitude:
        raise ValueError(f"値 {value} が範囲 ±{max_magnitude} を超えています")
    if value >= 0:
        return value
    else:
        return (1 << sign_bit_index) | abs(value)


print("=== Homing_Offset を直接書き込みでキャリブレーション準備 ===\n")

for motor_id, name in MOTOR_NAMES.items():
    raw_pos, comm, _ = ph.read2ByteTxRx(port_handler, motor_id, ADDR_PRESENT_POS)
    if comm != scs.COMM_SUCCESS:
        print(f"  ID {motor_id} ({name}): 読み取り失敗")
        continue

    # マルチターン値を単回転範囲に変換
    physical_pos = raw_pos % 4096
    # キャリブレーション後に Present_Position = 2047 にしたい
    homing_offset = physical_pos - 2047

    if abs(homing_offset) > 2047:
        print(f"  ID {motor_id} ({name}): offset={homing_offset} -> 物理的に端すぎて設定不可 (手動調整が必要)")
        continue

    # トルク無効 + Lock解除してから書き込み
    ph.write1ByteTxRx(port_handler, motor_id, ADDR_TORQUE_ENABLE, 0)
    ph.write1ByteTxRx(port_handler, motor_id, ADDR_LOCK, 0)

    encoded = encode_sign_magnitude(homing_offset)
    ph.write2ByteTxRx(port_handler, motor_id, ADDR_HOMING_OFFSET, encoded)

    # 書き込み後の Present_Position を再確認
    new_pos, _, _ = ph.read2ByteTxRx(port_handler, motor_id, ADDR_PRESENT_POS)
    print(f"  ID {motor_id} ({name}): raw={raw_pos} -> physical={physical_pos}, "
          f"offset={homing_offset:+d} -> 補正後 pos={new_pos}")

print()
print("=== 補正後の位置確認 ===")
ok_count = 0
for motor_id, name in MOTOR_NAMES.items():
    pos, comm, _ = ph.read2ByteTxRx(port_handler, motor_id, ADDR_PRESENT_POS)
    diff = pos - 2047
    ok = abs(diff) <= 100
    status = "OK (≈2047)" if ok else f"diff={diff:+d}"
    if ok:
        ok_count += 1
    print(f"  ID {motor_id} ({name}): pos={pos}  {status}")

port_handler.closePort()
print()
if ok_count == len(MOTOR_NAMES):
    print("全モーター準備完了。lerobot-calibrate を実行してください。")
else:
    print("一部のモーターが準備できていません。モーター電源を切って再試行してください。")
