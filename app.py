
import json
import random
from datetime import date
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Spoken English Pro Quest",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

LEADERBOARD_FILE = Path("leaderboard.json")

QUESTIONS = [
    {
        "mode": "General",
        "type": "choose",
        "level": "Daily Speaking",
        "mission": "Choose the natural sentence.",
        "q": "Which sentence sounds natural?",
        "options": ["I am agree with you.", "I agree with you.", "I am agreed you.", "I agree to you."],
        "answer": "I agree with you.",
        "tip": "Say: I agree with you.",
    },
    {
        "mode": "General",
        "type": "choose",
        "level": "School Talk",
        "mission": "Fix the common grammar mistake.",
        "q": "Choose the correct sentence:",
        "options": ["She go to school.", "She goes to school.", "She going to school.", "She gone school."],
        "answer": "She goes to school.",
        "tip": "Use goes with he/she.",
    },
    {
        "mode": "General",
        "type": "order",
        "level": "Sentence Builder",
        "mission": "Arrange the words correctly.",
        "q": "Make a polite request:",
        "words": ["Can", "you", "help", "me", "please?"],
        "answer": "Can you help me please?",
        "tip": "This is useful in real conversation.",
    },
    {
        "mode": "General",
        "type": "choose",
        "level": "Conversation Reply",
        "mission": "Choose a natural reply.",
        "q": "Someone says: Thank you. What should you reply?",
        "options": ["You welcome.", "You are welcome.", "Welcome only.", "No thank."],
        "answer": "You are welcome.",
        "tip": "You can also say: No problem.",
    },
    {
        "mode": "General",
        "type": "order",
        "level": "Speaking Confidence",
        "mission": "Build a confident sentence.",
        "q": "Arrange the words:",
        "words": ["I", "want", "to", "improve", "my", "English"],
        "answer": "I want to improve my English",
        "tip": "Use want to + verb.",
    },
    {
        "mode": "IELTS",
        "type": "choose",
        "level": "IELTS Speaking Part 1",
        "mission": "Choose a better IELTS-style answer.",
        "q": "Question: Do you like reading books?",
        "options": [
            "Yes.",
            "Yes, I enjoy reading because it helps me learn new ideas.",
            "Reading good.",
            "I like book very much."
        ],
        "answer": "Yes, I enjoy reading because it helps me learn new ideas.",
        "tip": "IELTS answers should be clear and slightly extended.",
    },
    {
        "mode": "IELTS",
        "type": "choose",
        "level": "IELTS Fluency",
        "mission": "Choose the more fluent sentence.",
        "q": "Which answer is more fluent?",
        "options": [
            "In my opinion, technology makes learning easier and faster.",
            "Technology learning easy fast.",
            "I am think technology good.",
            "Technology is very very very good only."
        ],
        "answer": "In my opinion, technology makes learning easier and faster.",
        "tip": "Use linking phrases like: In my opinion.",
    },
    {
        "mode": "IELTS",
        "type": "order",
        "level": "IELTS Sentence Builder",
        "mission": "Build an IELTS-style sentence.",
        "q": "Arrange the words:",
        "words": ["I", "believe", "practice", "improves", "fluency"],
        "answer": "I believe practice improves fluency",
        "tip": "This is a clear opinion sentence.",
    },
    {
        "mode": "IELTS",
        "type": "choose",
        "level": "IELTS Grammar",
        "mission": "Avoid grammar mistakes.",
        "q": "Choose the correct sentence:",
        "options": [
            "People is using internet.",
            "People are using the internet.",
            "People using internet.",
            "People are use internet."
        ],
        "answer": "People are using the internet.",
        "tip": "People is plural, so use are.",
    },
    {
        "mode": "IELTS",
        "type": "choose",
        "level": "IELTS Vocabulary",
        "mission": "Choose a better vocabulary sentence.",
        "q": "Which sentence has better vocabulary?",
        "options": [
            "The city is good.",
            "The city is vibrant and full of opportunities.",
            "The city very nice.",
            "The city has many many things."
        ],
        "answer": "The city is vibrant and full of opportunities.",
        "tip": "Use stronger vocabulary, but keep it natural.",
    },
]

BADGES = [
    ("Starter Speaker", 100),
    ("Grammar Fighter", 300),
    ("Fluency Builder", 600),
    ("IELTS Explorer", 900),
    ("Confidence Champion", 1300),
    ("Spoken English Pro", 1800),
]

DAILY_CHALLENGES = [
    "Introduce yourself in 3 English sentences.",
    "Speak for 30 seconds about your school or work.",
    "Use this sentence today: I agree with you because...",
    "Describe your favorite food in English.",
    "Answer this IELTS question: Do you like your hometown?",
    "Practice 5 polite sentences: Can you..., Could you..., Please...",
    "Record yourself speaking for 1 minute in English.",
]

def load_leaderboard():
    if LEADERBOARD_FILE.exists():
        try:
            return json.loads(LEADERBOARD_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_leaderboard(data):
    LEADERBOARD_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def play_sound(kind="correct"):
    tones = {
        "correct": [523, 659, 784],
        "wrong": [220, 160],
        "badge": [392, 523, 659, 1046],
        "level": [330, 440, 660],
    }
    freqs = tones.get(kind, [440])
    js_freqs = json.dumps(freqs)
    components.html(
        f"""
        <script>
        const freqs = {js_freqs};
        const audio = new (window.AudioContext || window.webkitAudioContext)();
        freqs.forEach((freq, i) => {{
            const osc = audio.createOscillator();
            const gain = audio.createGain();
            osc.type = "sine";
            osc.frequency.value = freq;
            gain.gain.value = 0.045;
            osc.connect(gain);
            gain.connect(audio.destination);
            osc.start(audio.currentTime + i * 0.10);
            gain.gain.exponentialRampToValueAtTime(0.001, audio.currentTime + i * 0.10 + 0.18);
            osc.stop(audio.currentTime + i * 0.10 + 0.20);
        }});
        </script>
        """,
        height=0,
    )

def init():
    defaults = {
        "started": False,
        "player": "Student",
        "mode": "General",
        "index": 0,
        "score": 0,
        "xp": 0,
        "lives": 3,
        "streak": 0,
        "selected_words": [],
        "shuffled_words": [],
        "message": "",
        "message_type": "",
        "earned_badges": [],
        "answered": False,
        "sound": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def current_level_number():
    return (st.session_state.xp // 250) + 1

def progress_to_next_level():
    return (st.session_state.xp % 250) / 250

def available_questions():
    return [q for q in QUESTIONS if q["mode"] == st.session_state.mode]

def restart():
    player = st.session_state.player
    mode = st.session_state.mode
    sound = st.session_state.sound
    st.session_state.clear()
    init()
    st.session_state.player = player
    st.session_state.mode = mode
    st.session_state.sound = sound
    st.session_state.started = True

def check_badges():
    newly = []
    for badge, needed in BADGES:
        if st.session_state.xp >= needed and badge not in st.session_state.earned_badges:
            st.session_state.earned_badges.append(badge)
            newly.append(badge)
    return newly

def finish_game():
    board = load_leaderboard()
    board.append({
        "name": st.session_state.player,
        "mode": st.session_state.mode,
        "score": st.session_state.score,
        "xp": st.session_state.xp,
        "badges": len(st.session_state.earned_badges),
        "date": str(date.today()),
    })
    board = sorted(board, key=lambda x: x["score"], reverse=True)[:10]
    save_leaderboard(board)

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at top, rgba(44,201,255,.28), transparent 34%),
        linear-gradient(180deg,#07172d,#102f55 55%,#123d2b);
    color: white;
}
.block-container {padding-top: 1.2rem; max-width: 850px;}
.hero {
    background: linear-gradient(135deg, rgba(255,213,79,.18), rgba(64,196,255,.16));
    border: 1px solid rgba(255,255,255,.18);
    border-radius: 28px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 22px 60px rgba(0,0,0,.35);
}
.title {
    font-size: 44px;
    font-weight: 950;
    color: #ffd54f;
    text-shadow: 0 4px 20px rgba(0,0,0,.55);
}
.sub {color:#d8fbff; font-size:16px;}
.card {
    background: rgba(3,18,35,.78);
    border: 1px solid rgba(255,255,255,.18);
    border-radius: 24px;
    padding: 22px;
    box-shadow: 0 18px 45px rgba(0,0,0,.38);
    margin-top: 16px;
}
.stats {
    display:grid;
    grid-template-columns: repeat(4, 1fr);
    gap:10px;
    margin-top:15px;
}
.stat {
    background: rgba(0,0,0,.38);
    padding: 13px;
    border-radius: 17px;
    text-align:center;
    font-weight: 900;
}
.level {
    color:#ffd54f;
    font-weight:950;
    text-transform:uppercase;
    letter-spacing:.7px;
}
.question {font-size:25px; font-weight:950; margin:10px 0;}
.tip {
    background:rgba(255,255,255,.10);
    border-left:5px solid #40c4ff;
    padding:12px;
    border-radius:14px;
    color:#d8fbff;
    margin:12px 0;
}
.correct {
    background:rgba(67,160,71,.25);
    border:1px solid #69f0ae;
    padding:12px;
    border-radius:14px;
    color:#c8ffd6;
    font-weight:900;
}
.wrong {
    background:rgba(229,57,53,.25);
    border:1px solid #ff8a80;
    padding:12px;
    border-radius:14px;
    color:#ffd1d1;
    font-weight:900;
}
.badge {
    display:inline-block;
    background:linear-gradient(180deg,#ffd54f,#ff9800);
    color:#2b1600;
    padding:8px 12px;
    border-radius:20px;
    font-weight:950;
    margin:4px;
}
.mission {
    background:linear-gradient(135deg, rgba(124,77,255,.28), rgba(0,229,255,.18));
    border:1px solid rgba(255,255,255,.18);
    border-radius:18px;
    padding:14px;
    margin:10px 0;
}
div.stButton > button {
    width:100%;
    border-radius:16px;
    padding:13px;
    font-weight:900;
    color:white;
    background:linear-gradient(180deg,#1976d2,#0d47a1);
    border:none;
    box-shadow:0 7px 0 #062b66,0 12px 25px rgba(0,0,0,.25);
}
div.stButton > button:active {
    transform:translateY(4px);
    box-shadow:0 3px 0 #062b66;
}
@media(max-width: 650px){
    .stats {grid-template-columns: repeat(2, 1fr);}
    .title {font-size:34px;}
}
</style>
""", unsafe_allow_html=True)

init()

st.markdown("""
<div class="hero">
    <div class="title">🎮 Spoken English Pro Quest</div>
    <div class="sub">XP system • Levels • Badges • Daily Challenges • IELTS Mode • Leaderboard • Sounds • Animations</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Game Settings")
    st.session_state.player = st.text_input("Player name", st.session_state.player)
    st.session_state.mode = st.radio("Mode", ["General", "IELTS"], index=0 if st.session_state.mode == "General" else 1)
    st.session_state.sound = st.toggle("Sound effects", value=st.session_state.sound)
    st.info("For Streamlit Cloud, keep app.py and requirements.txt in your GitHub repo.")

daily = DAILY_CHALLENGES[date.today().toordinal() % len(DAILY_CHALLENGES)]

if not st.session_state.started:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🚀 Start Your Mission")
    st.markdown(f'<div class="mission">🔥 <b>Today’s Daily Challenge:</b><br>{daily}</div>', unsafe_allow_html=True)
    st.write("Choose correct answers, build sentences, earn XP, unlock badges, and climb the leaderboard.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎯 Start General / IELTS Game"):
            restart()
            st.rerun()
    with c2:
        if st.button("🏆 View Leaderboard"):
            st.session_state.started = "leaderboard"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🏅 Badges You Can Unlock")
    st.markdown("".join([f'<span class="badge">{b} · {xp} XP</span>' for b, xp in BADGES]), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

if st.session_state.started == "leaderboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## 🏆 Leaderboard")
    board = load_leaderboard()
    if board:
        st.dataframe(board, use_container_width=True, hide_index=True)
    else:
        st.info("No scores yet. Play first!")
    if st.button("⬅️ Back"):
        st.session_state.started = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

level_no = current_level_number()
progress = progress_to_next_level()

st.markdown(
    f"""
    <div class="stats">
        <div class="stat">⭐ Score<br>{st.session_state.score}</div>
        <div class="stat">⚡ XP<br>{st.session_state.xp}</div>
        <div class="stat">🎚️ Level<br>{level_no}</div>
        <div class="stat">🔥 Streak<br>{st.session_state.streak}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.progress(progress, text=f"Progress to Level {level_no + 1}")
st.markdown(f"**Lives:** {'❤️' * st.session_state.lives}{'🖤' * (3 - st.session_state.lives)}")

if st.session_state.lives <= 0:
    finish_game()
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## 💥 Game Over")
    st.write(f"Final Score: **{st.session_state.score}**")
    st.write(f"XP Earned: **{st.session_state.xp}**")
    st.write("Badges: " + (", ".join(st.session_state.earned_badges) if st.session_state.earned_badges else "No badges yet"))
    if st.button("🔁 Play Again"):
        restart()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

questions = available_questions()

if st.session_state.index >= len(questions):
    finish_game()
    if st.session_state.sound:
        play_sound("level")
    st.balloons()
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## 🏆 Mission Complete!")
    st.write(f"Final Score: **{st.session_state.score}**")
    st.write(f"Total XP: **{st.session_state.xp}**")
    st.markdown("### 🏅 Your Badges")
    if st.session_state.earned_badges:
        st.markdown("".join([f'<span class="badge">{b}</span>' for b in st.session_state.earned_badges]), unsafe_allow_html=True)
    else:
        st.info("Play again to unlock badges.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔁 Play Again"):
            restart()
            st.rerun()
    with c2:
        if st.button("🏆 Leaderboard"):
            st.session_state.started = "leaderboard"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

q = questions[st.session_state.index]

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown(f'<div class="level">{q["mode"]} · {q["level"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="mission">🎙️ <b>Speaking Mission:</b> {q["mission"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="question">{q["q"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="tip">💡 {q["tip"]}</div>', unsafe_allow_html=True)

if st.session_state.message:
    cls = "correct" if st.session_state.message_type == "correct" else "wrong"
    st.markdown(f'<div class="{cls}">{st.session_state.message}</div>', unsafe_allow_html=True)
    new_badges = check_badges()
    if new_badges:
        if st.session_state.sound:
            play_sound("badge")
        st.markdown("### 🎉 New Badge Unlocked!")
        st.markdown("".join([f'<span class="badge">{b}</span>' for b in new_badges]), unsafe_allow_html=True)
    if st.button("➡️ Next Mission"):
        st.session_state.index += 1
        st.session_state.selected_words = []
        st.session_state.shuffled_words = []
        st.session_state.message = ""
        st.session_state.message_type = ""
        st.rerun()
else:
    if q["type"] == "choose":
        for option in q["options"]:
            if st.button(option):
                if option == q["answer"]:
                    st.session_state.score += 100 + st.session_state.streak * 20
                    st.session_state.xp += 120 + st.session_state.streak * 15
                    st.session_state.streak += 1
                    st.session_state.message = "✅ Correct! Great speaking choice."
                    st.session_state.message_type = "correct"
                    if st.session_state.sound:
                        play_sound("correct")
                    st.balloons()
                else:
                    st.session_state.lives -= 1
                    st.session_state.streak = 0
                    st.session_state.xp = max(0, st.session_state.xp - 20)
                    st.session_state.message = f"❌ Wrong! Correct answer: {q['answer']}"
                    st.session_state.message_type = "wrong"
                    if st.session_state.sound:
                        play_sound("wrong")
                st.rerun()

    if q["type"] == "order":
        if not st.session_state.shuffled_words:
            st.session_state.shuffled_words = random.sample(q["words"], len(q["words"]))

        sentence = " ".join(st.session_state.selected_words) if st.session_state.selected_words else "Tap words below..."
        st.info("Your sentence: " + sentence)

        cols = st.columns(2)
        for i, word in enumerate(st.session_state.shuffled_words):
            if i not in [x[0] for x in st.session_state.selected_words]:
                with cols[i % 2]:
                    if st.button(word, key=f"word_{i}_{word}"):
                        st.session_state.selected_words.append((i, word))
                        st.rerun()

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Check Sentence"):
                made = " ".join([w for _, w in st.session_state.selected_words])
                if made == q["answer"]:
                    st.session_state.score += 120 + st.session_state.streak * 20
                    st.session_state.xp += 140 + st.session_state.streak * 15
                    st.session_state.streak += 1
                    st.session_state.message = "✅ Correct sentence! Excellent."
                    st.session_state.message_type = "correct"
                    if st.session_state.sound:
                        play_sound("correct")
                    st.balloons()
                else:
                    st.session_state.lives -= 1
                    st.session_state.streak = 0
                    st.session_state.xp = max(0, st.session_state.xp - 20)
                    st.session_state.message = f"❌ Wrong! Correct sentence: {q['answer']}"
                    st.session_state.message_type = "wrong"
                    if st.session_state.sound:
                        play_sound("wrong")
                st.rerun()
        with c2:
            if st.button("🧹 Clear"):
                st.session_state.selected_words = []
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📅 Daily Challenge")
st.markdown(f'<div class="mission">{daily}</div>', unsafe_allow_html=True)

st.markdown("### 🏅 Badges")
if st.session_state.earned_badges:
    st.markdown("".join([f'<span class="badge">{b}</span>' for b in st.session_state.earned_badges]), unsafe_allow_html=True)
else:
    st.write("No badge yet. Keep playing!")
st.markdown('</div>', unsafe_allow_html=True)
