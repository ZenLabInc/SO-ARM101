# SO-ARM101 local control and MCP experiments

[日本語](README.md)

An experimental workspace for setting up an SO-ARM101 robot arm on macOS or Linux, diagnosing its Feetech servos with LeRobot, and trying natural-language control through an MCP-compatible AI client.

This repository contains code that can move hardware and rewrite servo settings. Keep a person next to the arm, clear the workspace, start at low speed, and be ready to disconnect power.

## Included components

- Port, servo-ID, encoder-position, and mode diagnostics
- LeRobot as a Git submodule for calibration, teleoperation, recording, and training
- A vendored and modified copy of `robot_MCP`
- Keyboard and MCP control experiments
- Optional Claude, Gemini, and OpenAI agent clients

## Clone and install

Requires Python 3.12, Git, a supported SO-ARM101 setup, and data-capable USB cables.

```sh
git clone --recurse-submodules https://github.com/ZenLabInc/SO-ARM101.git
cd SO-ARM101
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "lerobot[feetech]"
python -m pip install -r robot_MCP/requirements.txt
```

LeRobot changes frequently. Check the current [official SO-101 guide](https://huggingface.co/docs/lerobot/so101) before configuring motors.

## Identify the ports

```sh
ls /dev/cu.usbmodem* 2>/dev/null || ls /dev/ttyACM* 2>/dev/null
export SO_ARM_PORT=/dev/cu.usbmodemXXXXXXXX
python scan_motors.py
python check_positions.py
```

For a leader/follower pair:

```sh
export SO_ARM_FOLLOWER_PORT=/dev/cu.usbmodemXXXXXXXX
export SO_ARM_LEADER_PORT=/dev/cu.usbmodemYYYYYYYY
python scan_both_arms.py
```

Identify ports by unplugging and reconnecting one controller at a time. Never copy another user's device path or calibration file.

## MCP setup

See [robot_MCP_SETUP.md](robot_MCP_SETUP.md). Verify position reads and keyboard control before connecting an AI client. Store optional provider keys in a local `.env` file, which is ignored by Git. Agent requests may send camera images and conversation text to the selected provider and may incur API charges.

## Safety

- Keep people, animals, cables, and fragile objects outside the workspace.
- Test one small movement at a time and keep power within reach.
- `reset_motor_mode.py` and `fix_homing_offsets.py` write persistent servo settings.
- Treat AI output as untrusted input and enforce movement limits in the robot tools.
- Keep calibration JSON, real device identifiers, local paths, and camera indexes out of commits.

## Source and licensing

- `lerobot/` references [Hugging Face LeRobot](https://github.com/huggingface/lerobot) and remains under its license.
- `robot_MCP/` is derived from [IliaLarchenko/robot_MCP](https://github.com/IliaLarchenko/robot_MCP) and retains the [Apache License 2.0](robot_MCP/LICENSE).
- Copyright for the root helper scripts and documentation is reserved unless separately stated.
