
import random
import time
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Flappy Streamlit Native",
    page_icon="🐥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -----------------------------
# STYLE
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#071a2f,#08385c 55%,#0a572e);
}
.block-container {
    max-width: 560px;
    padding-top: 1rem;
}
.title {
    text-align:center;
    font-size:42px;
    font-weight:950;
    color:#ffd54f;
    text-shadow:0 4px 20px rgba(0,0,0,.45);
}
.subtitle {
    text-align:center;
    color:#d9fbff;
    margin-bottom:12px;
}
.game-box {
    background: linear-gradient(180deg,#68d8ff 0%,#c7f6ff 62%,#55b947 63%,#8b5a2b 75%);
    border-radius:28px;
    padding:16px;
    min-height:560px;
    box-shadow:0 30px 90px rgba(0,0,0,.55), inset 0 0 0 3px rgba(255,255,255,.20);
    position:relative;
    overflow:hidden;
}
.sky-line {
    font-size:22px;
    line-height:1.05;
    white-space:pre;
    font-family:monospace;
    letter-spacing:1px;
}
.bird {
    color:#ffca28;
    font-size:27px;
    filter: drop-shadow(0 4px 5px rgba(0,0,0,.35));
}
.pipe {
    color:#0f8f35;
    font-weight:900;
    text-shadow:1px 1px 0 #06451a;
}
.coin {
    color:#ffd54f;
    font-size:21px;
}
.shield {
    color:#80f2ff;
    font-size:21px;
}
.hud {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:8px;
    margin:12px 0;
}
.pill {
    background:rgba(0,0,0,.42);
    color:white;
    border-radius:16px;
    padding:10px;
    text-align:center;
    font-weight:900;
}
.panel {
    background:rgba(2,16,32,.70);
    border:1px solid rgba(255,255,255,.25);
    border-radius:22px;
    padding:18px;
    color:white;
    text-align:center;
    margin-top:12px;
}
.big {
    font-size:30px;
    font-weight:950;
    color:#ffd54f;
}
div.stButton > button {
    width:100%;
    border-radius:18px;
    padding:14px;
    font-size:18px;
    font-weight:950;
    color:white;
    background:linear-gradient(180deg,#1976d2,#0d47a1);
    border:none;
    box-shadow:0 7px 0 #062b66,0 12px 25px rgba(0,0,0,.25);
}
div.stButton > button:active {
    transform:translateY(4px);
    box-shadow:0 3px 0 #062b66;
}
.small-note {
    color:#d9fbff;
    text-align:center;
    font-size:13px;
    opacity:.9;
}
</style>
""", unsafe_allow_html=True)

ROWS = 16
COLS = 18
BIRD_COL = 4
GROUND_ROW = ROWS - 2

# -----------------------------
# STATE
# -----------------------------
def init_state():
    defaults = {
        "running": False,
        "game_over": False,
        "bird_row": 7,
        "velocity": 0,
        "pipes": [],
        "items": [],
        "score": 0,
        "coins": 0,
        "best": 0,
        "shield": 0,
        "tick": 0,
        "speed_delay": 0.34,
        "message": "Tap Start to play",
        "auto": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def reset_game():
    st.session_state.running = True
    st.session_state.game_over = False
    st.session_state.bird_row = 7
    st.session_state.velocity = 0
    st.session_state.pipes = []
    st.session_state.items = []
    st.session_state.score = 0
    st.session_state.coins = 0
    st.session_state.shield = 0
    st.session_state.tick = 0
    st.session_state.speed_delay = 0.34
    st.session_state.message = "Fly carefully!"
    add_pipe()

def flap():
    if st.session_state.game_over or not st.session_state.running:
        reset_game()
    else:
        st.session_state.velocity = -2
        st.session_state.message = "Flap!"

def add_pipe():
    gap_size = 5
    gap_start = random.randint(2, GROUND_ROW - gap_size - 1)
    pipe = {
        "col": COLS - 1,
        "gap_start": gap_start,
        "gap_end": gap_start + gap_size,
        "passed": False,
    }
    st.session_state.pipes.append(pipe)

    if random.random() < 0.75:
        item_type = "shield" if random.random() < 0.20 else "coin"
        st.session_state.items.append({
            "col": COLS - 1,
            "row": random.randint(gap_start + 1, gap_start + gap_size - 1),
            "type": item_type,
        })

def step_game():
    if not st.session_state.running or st.session_state.game_over:
        return

    st.session_state.tick += 1

    # Gravity
    st.session_state.velocity += 1
    st.session_state.velocity = min(st.session_state.velocity, 2)
    st.session_state.bird_row += st.session_state.velocity

    # Move pipes/items
    for p in st.session_state.pipes:
        p["col"] -= 1
    for item in st.session_state.items:
        item["col"] -= 1

    # Spawn pipe
    if not st.session_state.pipes or st.session_state.pipes[-1]["col"] < COLS - 7:
        add_pipe()

    # Remove old
    st.session_state.pipes = [p for p in st.session_state.pipes if p["col"] >= -1]
    st.session_state.items = [i for i in st.session_state.items if i["col"] >= -1]

    # Score
    for p in st.session_state.pipes:
        if not p["passed"] and p["col"] < BIRD_COL:
            p["passed"] = True
            st.session_state.score += 1
            st.session_state.best = max(st.session_state.best, st.session_state.score)

    # Collect item
    for item in st.session_state.items:
        if item["col"] == BIRD_COL and item["row"] == st.session_state.bird_row:
            if item["type"] == "coin":
                st.session_state.coins += 1
                st.session_state.score += 1
                st.session_state.message = "Coin collected!"
            else:
                st.session_state.shield = 5
                st.session_state.message = "Shield activated!"
            item["col"] = -99

    st.session_state.items = [i for i in st.session_state.items if i["col"] >= -1]

    # Shield countdown
    if st.session_state.shield > 0 and st.session_state.tick % 2 == 0:
        st.session_state.shield -= 1

    # Collision top/bottom
    if st.session_state.bird_row < 0 or st.session_state.bird_row >= GROUND_ROW:
        hit()

    # Pipe collision
    for p in st.session_state.pipes:
        if p["col"] == BIRD_COL:
            if not (p["gap_start"] <= st.session_state.bird_row <= p["gap_end"]):
                hit()

    # Difficulty
    if st.session_state.score > 0 and st.session_state.score % 8 == 0:
        st.session_state.speed_delay = max(0.20, 0.34 - st.session_state.score * 0.004)

def hit():
    if st.session_state.shield > 0:
        st.session_state.shield = 0
        st.session_state.message = "Shield saved you!"
        # Remove dangerous pipe near bird
        st.session_state.pipes = [p for p in st.session_state.pipes if p["col"] != BIRD_COL]
        return

    st.session_state.game_over = True
    st.session_state.running = False
    st.session_state.message = "Game Over!"

def make_grid():
    grid = [[" " for _ in range(COLS)] for _ in range(ROWS)]

    # Clouds
    for c in range(2, COLS, 7):
        r = (st.session_state.tick + c) % 5
        if r < 3:
            grid[r][c] = "☁"

    # Pipes
    for p in st.session_state.pipes:
        col = p["col"]
        if 0 <= col < COLS:
            for r in range(GROUND_ROW):
                if not (p["gap_start"] <= r <= p["gap_end"]):
                    grid[r][col] = "█"

    # Items
    for item in st.session_state.items:
        col, row = item["col"], item["row"]
        if 0 <= col < COLS and 0 <= row < GROUND_ROW:
            grid[row][col] = "◎" if item["type"] == "coin" else "◌"

    # Bird
    br = st.session_state.bird_row
    if 0 <= br < GROUND_ROW:
        grid[br][BIRD_COL] = "🐥" if st.session_state.shield == 0 else "🛡"

    # Ground
    for c in range(COLS):
        grid[GROUND_ROW][c] = "▰"
        grid[GROUND_ROW + 1][c] = "▱"

    return grid

def render_game():
    grid = make_grid()
    html_lines = []
    for row in grid:
        line = ""
        for cell in row:
            if cell == "🐥":
                line += '<span class="bird">🐥</span>'
            elif cell == "🛡":
                line += '<span class="shield">🛡</span>'
            elif cell == "█":
                line += '<span class="pipe">█</span>'
            elif cell == "◎":
                line += '<span class="coin">●</span>'
            elif cell == "◌":
                line += '<span class="shield">◌</span>'
            elif cell == "☁":
                line += "☁"
            else:
                line += cell
        html_lines.append(line)

    return "<br>".join(html_lines)

init_state()

st.markdown('<div class="title">🐥 Flappy Streamlit Native</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Pure Python + Streamlit game. No Pygame. No JavaScript engine.</div>', unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="hud">
        <div class="pill">Score<br>{st.session_state.score}</div>
        <div class="pill">Best<br>{st.session_state.best}</div>
        <div class="pill">Coins<br>{st.session_state.coins}</div>
        <div class="pill">Shield<br>{st.session_state.shield}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="game-box">
        <div class="sky-line">{render_game()}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="panel">
        <div class="big">{st.session_state.message}</div>
        <p>Click <b>Flap</b> to fly. Avoid pipes, collect coins, and use shield power-ups.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("🐥 FLAP"):
        flap()
        step_game()
        st.rerun()

with c2:
    if st.button("▶️ START / RESTART"):
        reset_game()
        st.rerun()

with c3:
    if st.button("⏭️ STEP"):
        step_game()
        st.rerun()

st.markdown('<div class="small-note">Mobile friendly: use FLAP button. Streamlit Cloud friendly.</div>', unsafe_allow_html=True)

# Optional auto-run mode
with st.expander("⚙️ Auto Play Settings"):
    st.session_state.auto = st.checkbox("Auto run animation", value=st.session_state.auto)
    st.write("Auto mode refreshes the app. For best control, use FLAP manually.")

if st.session_state.auto and st.session_state.running and not st.session_state.game_over:
    time.sleep(st.session_state.speed_delay)
    step_game()
    st.rerun()
