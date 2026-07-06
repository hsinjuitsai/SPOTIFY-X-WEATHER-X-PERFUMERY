import os
import sys
from pathlib import Path

import streamlit as st

# 讓 app/ 可以讀取專案根目錄下的 integrations/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from integrations.airtable import AirtableResults
from integrations.pipedream import PipedreamClient


# ==================================================
# 1. 設定讀取
# ==================================================

def get_setting(name, default=None):
    try:
        return st.secrets[name]
    except (KeyError, FileNotFoundError):
        return os.getenv(name, default)


PIPEDREAM_URL = get_setting("PIPEDREAM_WEBHOOK_URL")
FEEDBACK_URL = get_setting("PIPEDREAM_FEEDBACK_URL")
SESSION_ID = get_setting("SCENT_SESSION_ID", "gigi-main")
POLL_SECONDS = int(get_setting("POLL_SECONDS", 60))


CAPSULES = {
    "slot_a": "Spice Market",
    "slot_b": "Amber Wood",
    "slot_c": "Jaffa Clementine",
    "slot_d": "Floral Musk",
}


# ==================================================
# 2. 外部服務
# ==================================================

@st.cache_resource
def get_services():
    if not PIPEDREAM_URL:
        raise RuntimeError(
            "尚未在 secrets.toml 設定 PIPEDREAM_WEBHOOK_URL"
        )

    airtable_token = get_setting("AIRTABLE_TOKEN")

    airtable_base_id = get_setting(
        "AIRTABLE_BASE_ID",
        get_setting("BASE_ID"),
    )

    airtable_table_name = get_setting(
        "AIRTABLE_TABLE_NAME",
        get_setting("TABLE_NAME"),
    )

    if not airtable_token:
        raise RuntimeError("尚未設定 AIRTABLE_TOKEN")

    if not airtable_base_id:
        raise RuntimeError("尚未設定 AIRTABLE_BASE_ID")

    if not airtable_table_name:
        raise RuntimeError("尚未設定 AIRTABLE_TABLE_NAME")

    pipedream = PipedreamClient(PIPEDREAM_URL)

    airtable = AirtableResults(
        airtable_token,
        airtable_base_id,
        airtable_table_name,
    )

    return pipedream, airtable


# ==================================================
# 3. Streamlit 頁面設定
# ==================================================

st.set_page_config(
    page_title="Scent To YOU",
    page_icon="🌿",
    layout="centered",
)


# ==================================================
# 4. 原始 UI 樣式
# ==================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500'
        '&family=Inter:wght@200;300;400&display=swap'
    );

    .stApp {
        background-color: #F5F4F0;
    }

    .mag-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 400;
        text-align: center;
        width: 100%;
        display: block;
        margin-top: 2rem;
        margin-bottom: 0.5rem;
        color: #2C2C2C;
    }

    .mag-subtitle {
        font-family: 'Inter', sans-serif;
        font-weight: 200;
        text-transform: uppercase;
        letter-spacing: 4px;
        font-size: 0.7rem;
        text-align: center;
        width: 100%;
        color: #8C867A;
        margin-bottom: 3rem;
    }

    .slot-label {
        font-family: 'Inter', sans-serif;
        font-weight: 300;
        font-size: 0.9rem;
        letter-spacing: 1px;
    }

    .status-text {
        text-align: center;
        color: #8C867A;
        font-family: 'Inter', sans-serif;
        font-weight: 200;
        font-style: italic;
        letter-spacing: 1px;
    }

    .stButton > button {
        background-color: transparent;
        border: 1px solid #2C2C2C;
        border-radius: 0;
        color: #2C2C2C;
        display: block;
        margin: 0 auto;
        padding: 10px 20px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .stButton > button:hover {
        background-color: #2C2C2C;
        color: #F5F4F0;
        border-color: #2C2C2C;
    }

    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E5;
        border-radius: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 5. Session State
# ==================================================

if "page" not in st.session_state:
    st.session_state.page = "init"

if "active" not in st.session_state:
    st.session_state.active = False

if "baseline_id" not in st.session_state:
    st.session_state.baseline_id = None

if "last_record_id" not in st.session_state:
    st.session_state.last_record_id = None

if "spotify_active" not in st.session_state:
    st.session_state.spotify_active = True

if "position_active" not in st.session_state:
    st.session_state.position_active = True

if "exclusions" not in st.session_state:
    st.session_state.exclusions = "None"


# ==================================================
# 6. UI 函式
# ==================================================

def render_header(title, subtitle):
    st.markdown(
        f'<div class="mag-title">{title}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="mag-subtitle">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def render_scent_bar(label, value, color):
    try:
        safe_value = int(float(value or 0))
    except (TypeError, ValueError):
        safe_value = 0

    safe_value = max(0, min(100, safe_value))

    # 使用 st.html，避免 HTML 被 Markdown 當成程式碼。
    st.html(
        f"""
        <div style="text-align:center; margin-bottom:20px;">
            <p style="
                font-family:'Inter';
                font-size:0.65rem;
                color:#8C867A;
                letter-spacing:1px;
                margin-bottom:10px;
                height:30px;
            ">
                {label}
            </p>

            <div style="
                background-color:#E0E0E0;
                height:150px;
                width:8px;
                margin:0 auto;
                border-radius:4px;
                position:relative;
            ">
                <div style="
                    background-color:{color};
                    height:{safe_value}%;
                    width:8px;
                    border-radius:4px;
                    position:absolute;
                    bottom:0;
                    transition:height 1s ease;
                ">
                </div>
            </div>

            <p style="
                font-family:'Inter';
                font-weight:300;
                font-size:0.9rem;
                margin-top:10px;
            ">
                {safe_value}%
            </p>
        </div>
        """
    )


def render_result_card(fields):
    current_song = fields.get(
        "current_song",
        "Unknown",
    )

    ai_scent = fields.get(
        "AI_Scent",
        "Thinking...",
    )

    ai_reasoning = fields.get(
        "AI_Reasoning",
        "Analyzing atmosphere...",
    )

    st.html(
        f"""
        <div style="
            background-color:#FFFFFF;
            padding:40px;
            border:1px solid #E5E5E5;
            text-align:center;
            margin-top:20px;
        ">
            <p style="
                font-family:'Inter';
                font-weight:200;
                letter-spacing:2px;
                color:#8C867A;
                font-size:0.7rem;
                margin-bottom:20px;
            ">
                NOW PLAYING: {current_song}
            </p>

            <h2 style="
                font-family:'Playfair Display';
                font-weight:400;
                font-size:2.2rem;
                color:#2C2C2C;
                margin-bottom:15px;
            ">
                {ai_scent}
            </h2>

            <p style="
                font-family:'Inter';
                font-style:italic;
                color:#5F8670;
                font-size:1rem;
                line-height:1.6;
            ">
                “{ai_reasoning}”
            </p>
        </div>
        """
    )


def render_feedback(latest_record, fields):
    # 尚未設定 Feedback Workflow 時，不顯示回饋區。
    if not FEEDBACK_URL:
        return

    with st.expander("Experience Feedback"):
        feedback_score = st.slider(
            "這次香氛體驗評分",
            min_value=1,
            max_value=5,
            value=3,
        )

        feedback_comment = st.text_area(
            "其他感受（選填）",
            placeholder="例如：木質香可以再淡一點。",
        )

        if st.button(
            "Submit Feedback",
            use_container_width=True,
        ):
            try:
                feedback_client = PipedreamClient(
                    FEEDBACK_URL
                )

                feedback_client.send(
                    "feedback",
                    SESSION_ID,
                    decision_id=latest_record["id"],
                    score=feedback_score,
                    comment=feedback_comment,
                    song=fields.get(
                        "current_song",
                        "Unknown",
                    ),
                    scent=fields.get(
                        "AI_Scent",
                        "Unknown",
                    ),
                    ratios={
                        "slot_a": fields.get(
                            "slot_a_val",
                            0,
                        ),
                        "slot_b": fields.get(
                            "slot_b_val",
                            0,
                        ),
                        "slot_c": fields.get(
                            "slot_c_val",
                            0,
                        ),
                        "slot_d": fields.get(
                            "slot_d_val",
                            0,
                        ),
                    },
                )

                st.success("感謝你的回饋。")

            except Exception as error:
                st.error(
                    f"回饋送出失敗：{error}"
                )


# ==================================================
# 7. 第一頁：初始化
# ==================================================

if st.session_state.page == "init":
    render_header(
        "Scent To YOU",
        "Automated Craft // Tailored Atmosphere",
    )

    st.markdown(
        "<br><br>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("*Spotify Connection*")

    with col2:
        spotify_on = st.toggle(
            "Spotify",
            value=st.session_state.spotify_active,
            key="spotify_toggle",
            label_visibility="collapsed",
        )

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    col3, col4 = st.columns([3, 1])

    with col3:
        st.markdown("*Your Position*")

    with col4:
        position_on = st.toggle(
            "Position",
            value=st.session_state.position_active,
            key="position_toggle",
            label_visibility="collapsed",
        )

    st.markdown(
        "<br><br><br>",
        unsafe_allow_html=True,
    )

    if st.button(
        "Initialize Connection",
        use_container_width=True,
    ):
        if not spotify_on or not position_on:
            st.warning(
                "請確認已開啟 Spotify 連線與位置權限。"
            )

        else:
            st.session_state.spotify_active = spotify_on
            st.session_state.position_active = position_on
            st.session_state.page = "inventory"
            st.rerun()


# ==================================================
# 8. 第二頁：膠囊清點
# ==================================================

elif st.session_state.page == "inventory":
    render_header(
        "Inventory",
        "Synchronized // Capsules Detected",
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    for slot_key, scent_name in CAPSULES.items():
        display_label = (
            slot_key
            .replace("_", " ")
            .title()
        )

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown(
                (
                    "<p class='slot-label'>"
                    f"{display_label}"
                    "</p>"
                ),
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                (
                    "<p style='font-style:italic;"
                    "color:#5F8670;'>"
                    f"{scent_name}"
                    "</p>"
                ),
                unsafe_allow_html=True,
            )

        st.divider()

    exclusions = st.text_input(
        "SCENT EXCLUSION",
        value=st.session_state.exclusions,
        help="多個排除成分請使用逗號分隔。",
    )

    if st.button(
        "Start Your Automated Experience",
        use_container_width=True,
    ):
        try:
            pipedream, airtable = get_services()

            # 記錄開始前 Airtable 最新資料。
            # Dashboard 不會誤把舊紀錄當成新結果。
            current_record = airtable.latest()

            if current_record:
                st.session_state.baseline_id = (
                    current_record["id"]
                )
            else:
                st.session_state.baseline_id = None

            st.session_state.exclusions = exclusions

            # 第一次 Start 建立 Session 開始時間。
            pipedream.send(
                "init",
                SESSION_ID,
                slots=CAPSULES,
                exclusions=exclusions,
            )

            st.session_state.active = True
            st.session_state.page = "dashboard"

            st.success("Connection Successful")
            st.rerun()

        except Exception as error:
            st.error(
                f"Connection Failed：{error}"
            )


# ==================================================
# 9. 第三頁：Atmosphere Dashboard
# ==================================================

elif st.session_state.page == "dashboard":
    render_header(
        "Atmosphere",
        "Live Resonance // AI Scent Projection",
    )

    @st.fragment(run_every=POLL_SECONDS)
    def live_dashboard():
        if not st.session_state.active:
            st.info("目前體驗已停止。")
            return

        try:
            pipedream, airtable = get_services()

            # 每次 Poll 都使用相同 Session ID。
            # Pipedream Data Store 應保存第一次開始時間。
            pipedream.send(
                "poll",
                SESSION_ID,
            )

            latest_record = airtable.latest()

        except Exception as error:
            st.warning(
                f"等待服務連線：{error}"
            )
            return

        if not latest_record:
            st.markdown(
                "<br><br><br>",
                unsafe_allow_html=True,
            )

            st.markdown(
                (
                    '<div class="mag-subtitle">'
                    "Waiting for resonance..."
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                (
                    '<div class="status-text">'
                    "系統已就緒。請在 Spotify 開始播放，"
                    "AI 將即時投影專屬香氣。"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            return

        latest_id = latest_record.get("id")

        # 最新資料仍是開始前的舊資料。
        if latest_id == st.session_state.baseline_id:
            st.markdown(
                "<br><br><br>",
                unsafe_allow_html=True,
            )

            st.markdown(
                (
                    '<div class="mag-subtitle">'
                    "Waiting for resonance..."
                    "</div>"
                ),
                unsafe_allow_html=True,
            )

            st.markdown(
                (
                    '<div class="status-text">'
                    "正在監測 Spotify，等待新的香氛決策……"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )
            return

        fields = latest_record.get(
            "fields",
            {},
        )

        st.session_state.last_record_id = latest_id

        st.markdown(
            "<br>",
            unsafe_allow_html=True,
        )

        colors = [
            "#5F8670",
            "#D2B48C",
            "#81A1C1",
            "#2C2C2C",
        ]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            render_scent_bar(
                str(
                    fields.get(
                        "slot_a_name",
                        "Slot A",
                    )
                    or "Slot A"
                ).upper(),
                fields.get(
                    "slot_a_val",
                    0,
                ),
                colors[0],
            )

        with col2:
            render_scent_bar(
                str(
                    fields.get(
                        "slot_b_name",
                        "Slot B",
                    )
                    or "Slot B"
                ).upper(),
                fields.get(
                    "slot_b_val",
                    0,
                ),
                colors[1],
            )

        with col3:
            render_scent_bar(
                str(
                    fields.get(
                        "slot_c_name",
                        "Slot C",
                    )
                    or "Slot C"
                ).upper(),
                fields.get(
                    "slot_c_val",
                    0,
                ),
                colors[2],
            )

        with col4:
            render_scent_bar(
                str(
                    fields.get(
                        "slot_d_name",
                        "Slot D",
                    )
                    or "Slot D"
                ).upper(),
                fields.get(
                    "slot_d_val",
                    0,
                ),
                colors[3],
            )

        render_result_card(fields)

        st.markdown(
            "<br>",
            unsafe_allow_html=True,
        )

        render_feedback(
            latest_record,
            fields,
        )

    live_dashboard()

    st.markdown(
        "<br><br>",
        unsafe_allow_html=True,
    )

    col_refresh, col_end = st.columns(2)

    with col_refresh:
        if st.button(
            "Sync Live Data",
            use_container_width=True,
        ):
            st.rerun()

    with col_end:
        if st.button(
            "End Experience",
            use_container_width=True,
        ):
            try:
                pipedream, _ = get_services()

                pipedream.send(
                    "end",
                    SESSION_ID,
                )

            except Exception as error:
                st.warning(
                    "本機已停止，但 Pipedream "
                    f"通知失敗：{error}"
                )

            st.session_state.active = False
            st.session_state.page = "init"
            st.session_state.baseline_id = None
            st.session_state.last_record_id = None
            st.rerun()