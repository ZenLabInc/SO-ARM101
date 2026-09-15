import os

import scservo_sdk as scs

port = os.environ.get("SO_ARM_PORT")
if not port:
    raise SystemExit("SO_ARM_PORTを設定してください。例: export SO_ARM_PORT=/dev/cu.usbmodemXXXXXXXX")
ph = scs.PacketHandler(0)
port_handler = scs.PortHandler(port)

if not port_handler.openPort():
    print("ポートを開けませんでした")
    exit(1)

port_handler.setBaudRate(1_000_000)

print("=== ID 1〜10をPingスキャン (baudrate=1,000,000) ===")
found = []
for motor_id in range(1, 11):
    model, comm, error = ph.ping(port_handler, motor_id)
    if comm == scs.COMM_SUCCESS:
        found.append((motor_id, model))
        print(f"  ID {motor_id}: 応答あり (model={model})")
    else:
        print(f"  - ID {motor_id}: 応答なし")

print()
if found:
    print(f"検出されたモーター ID: {[mid for mid, _ in found]}")
    if sorted([mid for mid, _ in found]) == list(range(1, len(found) + 1)):
        print("=> ID割り振りOK: 連番で揃っています")
    else:
        print("=> 警告: IDが連番ではありません。確認してください")
else:
    print("モーターが検出されませんでした")

port_handler.closePort()
