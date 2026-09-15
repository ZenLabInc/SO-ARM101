"""
マルチターン状態になったモーターをPositionモードにリセットするスクリプト。

STS3215がマルチターン値（4095超）を返している場合、
Operating_ModeをPOSITION(0)に戻し、Homing_Offsetをリセットすることで
次のキャリブレーションが通るようにする。
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
ADDR_OPERATING_MODE = 33
ADDR_HOMING_OFFSET  = 31
ADDR_PRESENT_POS    = 56

ph = scs.PacketHandler(0)
port_handler = scs.PortHandler(port)

if not port_handler.openPort():
    print("ポートを開けませんでした")
    exit(1)
port_handler.setBaudRate(1_000_000)

print("=== 現在のOperating_Mode確認 ===")
for motor_id, name in MOTOR_NAMES.items():
    mode, comm, _ = ph.read1ByteTxRx(port_handler, motor_id, ADDR_OPERATING_MODE)
    pos, comm2, _ = ph.read2ByteTxRx(port_handler, motor_id, ADDR_PRESENT_POS)
    mode_name = {0: "POSITION", 1: "VELOCITY", 2: "PWM", 3: "STEP"}.get(mode, f"Unknown({mode})")
    print(f"  ID {motor_id} ({name}): mode={mode_name}, pos={pos}")

print()
print("=== POSITION モードにリセット＆Homing_Offsetをゼロに ===")
for motor_id, name in MOTOR_NAMES.items():
    # トルク無効 + Lock解除
    ph.write1ByteTxRx(port_handler, motor_id, ADDR_TORQUE_ENABLE, 0)
    ph.write1ByteTxRx(port_handler, motor_id, ADDR_LOCK, 0)
    # Operating_Mode = POSITION (0)
    ph.write1ByteTxRx(port_handler, motor_id, ADDR_OPERATING_MODE, 0)
    # Homing_Offset = 0
    ph.write2ByteTxRx(port_handler, motor_id, ADDR_HOMING_OFFSET, 0)
    print(f"  ID {motor_id} ({name}): -> POSITION mode, Homing_Offset=0")

print()
print("=== リセット後の位置確認 ===")
for motor_id, name in MOTOR_NAMES.items():
    pos, comm, _ = ph.read2ByteTxRx(port_handler, motor_id, ADDR_PRESENT_POS)
    offset_from_mid = pos - 2047
    ok = abs(offset_from_mid) <= 2047
    status = "OK" if ok else "NG <- 要調整"
    print(f"  ID {motor_id} ({name}): pos={pos}, offset={offset_from_mid:+d}  {status}")

port_handler.closePort()
print()
print("完了。問題がなければ lerobot-calibrate を再実行してください。")
