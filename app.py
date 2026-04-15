import datetime as dt
from pathlib import Path
import re
from zoneinfo import ZoneInfo

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "Icon.png"
PAGE_ICON = str(ICON_PATH) if ICON_PATH.exists() else "⏱️"
PUNE_TZ = ZoneInfo("Asia/Kolkata")


def now_pune() -> dt.datetime:
    # Keep a timezone-correct clock while preserving naive datetimes
    # used throughout the app's existing calculations.
    return dt.datetime.now(PUNE_TZ).replace(tzinfo=None)


st.set_page_config(
    page_title="EntryExit Insight",
    page_icon=PAGE_ICON,
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --accent-gold: #d4af72;
        --accent-gold-hover: #c49c5f;
        --accent-gold-soft: #f2ddbb;
        --card-topline: #1e3a8a;
    }

    .stApp {
        background: var(--background-color);
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2.2rem;
    }

    h1, h2, h3 {
        color: var(--text-color) !important;
        letter-spacing: 0.3px;
        font-weight: 700;
        text-wrap: balance;
    }

    h1 {
        font-size: 3rem !important;
        margin-bottom: 0.2rem;
        font-family: "Georgia", "Times New Roman", serif;
    }

    p, label, .stCaption {
        color: color-mix(in srgb, var(--text-color) 70%, transparent) !important;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(
            180deg,
            color-mix(in srgb, var(--secondary-background-color) 95%, transparent) 0%,
            color-mix(in srgb, var(--secondary-background-color) 85%, transparent) 100%
        );
        border: 1px solid color-mix(in srgb, var(--accent-gold) 22%, var(--text-color));
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 12px 26px color-mix(in srgb, black 20%, transparent);
        backdrop-filter: blur(2px);
        position: relative;
        overflow: hidden;
    }

    div[data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        inset: 0 0 auto 0;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, var(--card-topline) 50%, transparent 100%);
        opacity: 0.85;
    }

    div[data-testid="stMetricLabel"] {
        color: var(--muted) !important;
    }

    div[data-testid="stMetricValue"] {
        color: var(--text-color) !important;
        font-weight: 700 !important;
    }

    .stTextArea textarea {
        border: 1px solid color-mix(in srgb, var(--accent-gold) 22%, var(--text-color));
        border-radius: 12px;
        background: var(--secondary-background-color);
        color: var(--text-color);
        box-shadow: inset 0 1px 0 color-mix(in srgb, white 8%, transparent);
    }

    .stTextArea textarea:focus {
        border-color: var(--accent-gold) !important;
        box-shadow: 0 0 0 2px color-mix(in srgb, var(--accent-gold) 28%, transparent) !important;
    }

    .stButton > button {
        background: linear-gradient(180deg, #e2c18a 0%, var(--accent-gold) 100%);
        color: #1a1308;
        border-radius: 12px;
        border: 1px solid color-mix(in srgb, #fff 22%, var(--accent-gold));
        font-weight: 700;
        transition: all 0.15s ease;
        box-shadow: 0 10px 22px rgba(212, 175, 114, 0.28);
        opacity: 1 !important;
        min-height: 2.8rem;
    }

    .stButton > button:hover:not(:disabled) {
        background: linear-gradient(180deg, #edd2a5 0%, var(--accent-gold-hover) 100%);
        transform: translateY(-1px) scale(1.01);
        box-shadow: 0 14px 30px rgba(212, 175, 114, 0.34);
    }

    .stButton > button:disabled {
        background-color: #6f634f !important;
        color: #d7c9b2 !important;
        opacity: 0.7 !important;
        cursor: not-allowed;
        box-shadow: none;
    }

    .stMarkdown, .stText {
        color: var(--text-color);
    }

    hr {
        border-color: color-mix(in srgb, var(--accent-gold) 25%, transparent);
    }

    div[data-testid="stAlert"] {
        border: 1px solid color-mix(in srgb, var(--accent-gold) 28%, var(--text-color));
        border-radius: 12px;
        background: color-mix(in srgb, var(--secondary-background-color) 90%, transparent);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --card-topline: var(--accent-gold-soft);
        }

        .stApp {
            background:
                radial-gradient(circle at 14% -10%, rgba(212, 175, 114, 0.16), transparent 34%),
                radial-gradient(circle at 86% 0%, rgba(212, 175, 114, 0.10), transparent 32%),
                #090b12;
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, #10141f 0%, #0c111b 100%);
            border: 1px solid #3d3326;
            box-shadow: 0 16px 30px rgba(0, 0, 0, 0.42);
        }

        .stTextArea textarea {
            background: #0f1420;
            border-color: #3d3326;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def hms_to_seconds(hours: int, minutes: int, seconds: int) -> int:
    return (hours * 3_600) + (minutes * 60) + seconds


def format_short(total_seconds: int) -> str:
    total_seconds = max(total_seconds, 0)
    hours = total_seconds // 3_600
    minutes = (total_seconds % 3_600) // 60
    seconds = total_seconds % 60
    return f"{hours}h {minutes:02d}m {seconds:02d}s"


def format_clock(total_seconds: int) -> str:
    total_seconds = max(total_seconds, 0)
    hours = total_seconds // 3_600
    minutes = (total_seconds % 3_600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def extract_times(log_text: str) -> list[dt.datetime]:
    matches = re.findall(r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b", log_text)
    current_day = now_pune().date()
    points: list[dt.datetime] = []
    last_dt = None

    for item in matches:
        hh, mm = map(int, item.split(":"))
        candidate = dt.datetime.combine(current_day, dt.time(hh, mm))

        # If times roll back, assume next day.
        if last_dt and candidate < last_dt:
            current_day += dt.timedelta(days=1)
            candidate = dt.datetime.combine(current_day, dt.time(hh, mm))

        points.append(candidate)
        last_dt = candidate

    return points


def summarize_sessions(
    time_points: list[dt.datetime], current_time: dt.datetime | None = None
) -> dict:
    work_sessions: list[str] = []
    break_sessions: list[str] = []
    total_work = 0
    total_break = 0
    ongoing_work = 0
    ongoing_work_text = None

    for idx in range(len(time_points) - 1):
        start_dt = time_points[idx]
        end_dt = time_points[idx + 1]
        seconds = int((end_dt - start_dt).total_seconds())
        session_text = (
            f"{start_dt.strftime('%Y-%m-%d %H:%M')} -> "
            f"{end_dt.strftime('%Y-%m-%d %H:%M')} - {format_short(seconds)}"
        )

        if idx % 2 == 0:
            work_sessions.append(session_text)
            total_work += seconds
        else:
            break_sessions.append(session_text)
            total_break += seconds

    # Odd number of punches means user is currently in an active work session.
    if len(time_points) % 2 == 1:
        current_time = current_time or now_pune()
        if current_time < time_points[-1]:
            current_time += dt.timedelta(days=1)
        ongoing_work = int((current_time - time_points[-1]).total_seconds())
        ongoing_work_text = (
            f"{time_points[-1].strftime('%Y-%m-%d %H:%M')} -> "
            f"{current_time.strftime('%Y-%m-%d %H:%M')} - {format_short(ongoing_work)} "
            "(ongoing)"
        )

    return {
        "work_sessions": work_sessions,
        "break_sessions": break_sessions,
        "total_work": total_work,
        "total_break": total_break,
        "ongoing_work": max(ongoing_work, 0),
        "ongoing_work_text": ongoing_work_text,
    }


title_col1, title_col2 = st.columns([1, 12], vertical_alignment="center")
with title_col1:
    if ICON_PATH.exists():
        st.image(str(ICON_PATH), width=52)
    else:
        st.markdown("### ⏱️")
with title_col2:
    st.title("EntryExit Insight")
st.caption("Paste your biometric log data below to calculate work and break times.")
st.caption(f"Pune time (IST): {now_pune().strftime('%d-%b-%Y %I:%M:%S %p')}")

st.markdown("**Biometric Log Input**")
log_input = st.text_area(
    "Biometric Log Input",
    height=170,
    label_visibility="collapsed",
    placeholder="Biometric.\n01:55\nBiometric.\n01:56\nBiometric.\n01:58\n...",
)

calculate_clicked = st.button("Calculate Times", use_container_width=True)

if "biometric_result" not in st.session_state:
    st.session_state.biometric_result = None
if "biometric_points" not in st.session_state:
    st.session_state.biometric_points = None

if calculate_clicked:
    points = extract_times(log_input)
    if len(points) < 1:
        st.error("Please enter at least one valid time in HH:MM format.")
        st.session_state.biometric_result = None
        st.session_state.biometric_points = None
    else:
        st.session_state.biometric_points = points
        st.session_state.biometric_result = summarize_sessions(points)

@st.fragment(run_every="1s")
def render_live_dashboard() -> None:
    points = st.session_state.biometric_points
    if not points:
        return

    result = summarize_sessions(points, current_time=now_pune())
    target_work_seconds = hms_to_seconds(7, 30, 0)
    target_break_seconds = hms_to_seconds(1, 30, 0)
    total_work = result["total_work"] + result["ongoing_work"]
    total_break = result["total_break"]
    total_time = total_work + total_break
    remaining_work = max(target_work_seconds - total_work, 0)
    remaining_break = max(target_break_seconds - total_break, 0)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Work Time", format_clock(total_work))
    c2.metric("Total Break Time", format_clock(total_break))
    c3.metric("Total Time", format_clock(total_time))
    c4.metric("Remaining Work", format_clock(remaining_work))
    c5.metric("Remaining Break", format_clock(remaining_break))

    if result["ongoing_work_text"]:
        st.info(f"Active work session: {result['ongoing_work_text']}")

    if remaining_work > 0:
        st.success(f"You need to stay for: {format_clock(remaining_work)}")
    else:
        st.success(
            f"Target completed. Overtime: {format_clock(total_work - target_work_seconds)}"
        )


render_live_dashboard()

st.markdown("---")
st.markdown("#### Feedback")
st.text_area(
    "Share your feedback",
    label_visibility="collapsed",
    placeholder=(
        "If you want any aditional feature on this website, "
        "give it up in feedback."
    ),
)
