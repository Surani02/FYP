# Build onedir with:
#   pyinstaller --clean --noconfirm RL_Demo.spec
#
# Build onefile after onedir validation with:
#   set RL_DEMO_ONEFILE=1
#   pyinstaller --clean --noconfirm RL_Demo.spec
#
# The spec intentionally packages inference checkpoints only. Training
# archives, plots, CSV exports, and source caches are not needed by the UI.

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules


ROOT = Path(SPEC).parent


def checkpoint_datas():
    return [
        (str(path), str(path.relative_to(ROOT).parent))
        for path in ROOT.glob("**/*.pt")
        if ".venv" not in path.parts and "__pycache__" not in path.parts
    ]


streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all("streamlit")
_, _, gymnasium_hiddenimports = collect_all("gymnasium")

# PyInstaller does not infer Gymnasium environment packages from the runtime
# import graph automatically; these submodules provide the classic-control and
# Box2D environments used by the demo.
gym_hidden = list(dict.fromkeys(
    collect_submodules("gymnasium")
    + collect_submodules("gymnasium.envs")
    + collect_submodules("gymnasium.envs.classic_control")
    + collect_submodules("gymnasium.envs.box2d")
    + collect_submodules("gymnasium.envs.toy_text")
))

datas = [
    (str(ROOT / "web_demo" / "app.py"), "web_demo"),
    (str(ROOT / "web_demo" / ".streamlit" / "config.toml"), ".streamlit"),
    *checkpoint_datas(),
    *streamlit_datas,
]

hiddenimports = [
    *streamlit_hiddenimports,
    *gymnasium_hiddenimports,
    *gym_hidden,
    "web_demo.episode",
    "agents.networks",
    "agents.ppo_agent",
    "envs.gym_env",
    "modules.appraisal",
    "modules.behaviour_influence",
    "modules.cognitive_reward",
    "modules.cognitive_state",
    "modules.constraints",
    "modules.divergence",
    "demo",
    "train_full_model",
    "pygame",
    "box2d",
    "box2d.box2d",
    "gymnasium.envs.classic_control",
    "gymnasium.envs.box2d",
]

a = Analysis(
    ["web_demo/run.py"],
    pathex=[str(ROOT)],
    binaries=streamlit_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter",
        "pytest",
        "IPython",
        "jupyter",
        "notebook",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

if os.environ.get("RL_DEMO_ONEFILE") == "1":
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.datas,
        [],
        name="RL_Demo",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=True,
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="RL_Demo",
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=True,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        name="RL_Demo",
    )
