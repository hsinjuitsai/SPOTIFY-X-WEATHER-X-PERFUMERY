# Scent To YOU

## 你的專屬自動化調香機器人

Scent To YOU 是一套結合音樂情緒、環境狀態與香氛配方的智慧感官系統。

系統會取得使用者目前播放的 Spotify 歌曲與所在地天氣，分析音樂的 Valence、Energy、Danceability、Acousticness 與 Tempo，再結合溫度、濕度及香氛膠囊特性，自動產生香氣組合與擴香強度。

> 將非結構化的感官資料，轉換為結構化的香氛控制指令。

---

## 專案發想

現有智慧香氛產品通常提供：

- 手動選擇香味
- App 遠端控制
- 定時與排程
- 固定情境模式
- 使用者自行調整比例

這些功能的前提是：使用者已經知道自己想要什麼。

但在真實生活中，情緒、音樂與環境會持續變化，使用者不一定能立即察覺自己的需求，也不一定會主動調整香氛。

Scent To YOU 希望讓香氛從「等待使用者操作」，轉變為「主動感知情境並提供回應」。

---

## 核心概念

### 跨感官知覺整合

系統將三種感官資訊整合：

```text
音樂情緒
+
環境狀態
+
香氛特性
=
個人化香氛決策
生活儀式感
香氣不再只是固定的背景氣味，而是會隨歌曲與環境改變的感官體驗。
當音樂改變時，系統會重新判斷目前的情緒動態，並產生新的香氛名稱、理由與膠囊比例。
系統流程
使用者啟動 Streamlit
        ↓
選擇四個香氛膠囊與排除成分
        ↓
Streamlit 呼叫 Pipedream Webhook
        ↓
取得 Spotify 目前播放歌曲
        ↓
取得 OpenWeather 即時天氣
        ↓
讀取香氛膠囊資料
        ↓
Python 計算香氛排名、比例與風速
        ↓
Gemini 產生四字香氛名稱與簡短理由
        ↓
結果寫入 Airtable
        ↓
Streamlit 顯示即時香氛結果


專案結構
scent-to-you/
├── app/
│   └── streamlit_app.py
│
├── scent_core/
│   ├── __init__.py
│   ├── models.py
│   └── decision_engine.py
│
├── integrations/
│   ├── __init__.py
│   ├── airtable.py
│   └── pipedream.py
│
├── pipedream/
│   ├── fetch_context.py
│   ├── logic_processor.py
│   ├── session_manager.js
│   ├── update_session.js
│   ├── parse_ai_output.js
│   └── prompt.txt
│
├── tests/
│   └── test_decision_engine.py
│
├── docs/
│   ├── architecture.md
│   └── pipedream_setup.md
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
安裝方式
1. Clone 專案
git clone https://github.com/你的帳號/scent-to-you.git
cd scent-to-you
2. 建立虛擬環境
python -m venv .venv
Windows 啟用方式：
.\.venv\Scripts\Activate.ps1
3. 安裝套件
python -m pip install -r requirements.txt
4. 建立 Streamlit Secrets
複製：
.streamlit/secrets.toml.example
重新命名為：
.streamlit/secrets.toml
填入自己的設定：
AIRTABLE_TOKEN = "你的 Airtable Token"
AIRTABLE_BASE_ID = "你的 Base ID"
AIRTABLE_TABLE_NAME = "你的 Table ID"

PIPEDREAM_WEBHOOK_URL = "你的 Pipedream HTTP Trigger URL"
SCENT_SESSION_ID = "demo-user"
POLL_SECONDS = 60


Pipedream 設定
每位使用者需要在自己的 Pipedream Workspace：
建立 HTTP Trigger Workflow。
連接自己的 Spotify 帳號。
連接自己的 Airtable 帳號。
設定自己的 Gemini 帳號。
建立 OpenWeather API Key。
建立 Pipedream Project Secret：
OPENWEATHER_API_KEY
將 pipedream/ 內的程式放入對應步驟。
將 Pipedream HTTP Trigger URL 填入 Streamlit Secrets。
完成測試後按下 Deploy。
GitHub 不包含任何使用者的 OAuth Token 或 API Key。
啟動系統
streamlit run app/streamlit_app.py
瀏覽器通常會自動開啟：
http://localhost:8501
執行測試
pytest -q
目前測試包含：
比例總和檢查
安全排除檢查
學習期時間判斷
重置模式風速檢查
Airtable 結果欄位
current_song
AI_Scent
AI_Reasoning

slot_a_name
slot_a_val

slot_b_name
slot_b_val

slot_c_name
slot_c_val

slot_d_name
slot_d_val

fan_speed
createdTime
目前完成度
已完成
Spotify 歌曲資料取得
OpenWeather 天氣資料取得
香氛膠囊評分
香氛比例產生
AI 香氛名稱與理由
Airtable 結果保存
Streamlit 即時顯示
Pipedream Webhook 串接
核心規則測試
尚未完成
使用者評分回饋
長期個人偏好學習
正式硬體控制
正式雲端長時間部署
多使用者帳號管理

已知限制
Pipedream 免費方案具有執行額度與 Connected Accounts 限制。
自動輪詢頻率會影響免費額度。
Streamlit 在本機關閉後，本機介面不會繼續更新。
Spotify API 功能會受到帳號、授權與 API 政策限制。
目前是軟體原型，尚未連接正式香氛硬體。
回饋學習功能仍在規劃中。
----
專案定位
Scent To YOU 不是單純的香氛控制介面，而是一個跨感官決策實驗。
本專案嘗試探索：
當使用者尚未明確意識到自己的感官需求時，系統是否能透過音樂與環境資訊，主動提供合適的香氛回應？