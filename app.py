import streamlit as st
from openai import OpenAI
import re
from supabase import create_client

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="ホテル接遇AIアシスタント",
    page_icon="🏨",
    layout="wide"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "answer" not in st.session_state:
    st.session_state.answer = None

def load_system_prompt():
    with open("rules/default.txt", "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PROMPT = load_system_prompt()

st.markdown("""
<style>
.main {
    background-color: #fafafa;
}
.block-container {
    padding-top: 2rem;
    max-width: 1100px;
}
.title-box {
    padding: 1.4rem 1.6rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #2f3a4a, #596579);
    color: white;
    margin-bottom: 1.5rem;
}
.title-box h1 {
    margin: 0;
    font-size: 2rem;
}
.title-box p {
    margin-top: 0.5rem;
    color: #e8e8e8;
}
.result-box {
    padding: 1.2rem 1.4rem;
    border-radius: 16px;
    background-color: white;
    border: 1px solid #e5e5e5;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.small-note {
    color: #666;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-box">
    <h1>🏨 ホテル接遇AIアシスタント</h1>
    <p>クレーム内容から、初動対応・お客様への返答例・責任者共有の要否・NG対応を生成します。</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ 設定")
    model = st.selectbox(
        "使用モデル",
        ["gpt-4o-mini", "gpt-4o"],
        index=0
    )
    st.caption("通常は gpt-4o-mini で十分です。より高品質にしたい場合は gpt-4o。")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 クレーム情報")

    complaint_type = st.selectbox(
        "クレーム種別",
        [
            "清掃不備",
            "騒音",
            "接客態度",
            "予約ミス",
            "食事・アレルギー",
            "設備不良",
            "料金・請求",
            "忘れ物",
            "怪我・事故",
            "SNS投稿示唆",
            "その他"
        ]
    )

    place = st.selectbox(
        "発生場所",
        ["客室", "フロント", "レストラン", "予約", "チェックアウト後", "館内施設", "その他"]
    )

    emotion = st.selectbox(
        "お客様の温度感",
        ["少し不満", "強く怒っている", "返金要求あり", "SNS投稿を示唆", "責任者を要求", "非常に興奮している"]
    )

    urgency = st.selectbox(
        "緊急度",
        ["低", "中", "高", "緊急"]
    )

with col2:
    st.subheader("💬 詳細入力")

    complaint = st.text_area(
        "クレーム内容",
        height=160,
        placeholder="例：チェックイン直後、客室の浴室に髪の毛が残っており、お客様が強くお怒りになっている。"
    )

    note = st.text_area(
        "補足情報",
        height=120,
        placeholder="例：お客様は別部屋への変更を希望。小さなお子様連れ。"
    )

generate = st.button("✨ 対応案を生成する", use_container_width=True)

if generate:
    if not complaint.strip():
        st.warning("クレーム内容を入力してください。")
    else:
        user_prompt = f"""
以下のクレームについて、ホテルスタッフ向けに対応案を作成してください。

クレーム種別：
{complaint_type}

クレーム内容：
{complaint}

発生場所：
{place}

お客様の温度感：
{emotion}

緊急度：
{urgency}

補足情報：
{note if note else "特になし"}
"""

        with st.spinner("対応案を生成しています..."):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.2,
                )

                

                answer = response.choices[0].message.content

                st.session_state.answer = answer

                # ----------------------------
                # リスク情報を抽出
                # ----------------------------
                risk_level = "不明"
                manager = "不明"

                def extract_field(text, field):
                    match = re.search(rf"{field}.*?\n(.*)", text)
                    return match.group(1).strip() if match else "不明"

                risk_level = extract_field(answer, "リスクレベル")
                manager = extract_field(answer, "責任者共有の要否")

                def extract_section(text, title):
                    pattern = rf"## {title}\n(.*?)(?=\n## |\Z)"
                    match = re.search(pattern, text, re.DOTALL)
                    return match.group(1).strip() if match else "該当内容を取得できませんでした。"

                # ----------------------------
                # 色を決定
                # ----------------------------
                def get_color(level):
                    if "緊急" in level:
                        return "#ff4b4b"
                    elif "高" in level:
                        return "#ff8c00"
                    elif "中" in level:
                        return "#f1c40f"
                    else:
                        return "#2ecc71"

                risk_color = get_color(risk_level)

                # ----------------------------
                # カード表示
                # ----------------------------
                st.markdown("### 🚨 重要判断")

                card1, card2 = st.columns(2)

                with card1:
                    st.markdown(
                        f"""
                        <div style="
                            padding:14px 18px;
                            border-radius:14px;
                            background-color:{risk_color};
                            color:white;
                            text-align:center;
                            min-height:95px;
                        ">
                            <div style="font-size:15px; font-weight:600;">リスクレベル</div>
                            <div style="font-size:30px; font-weight:700; margin-top:8px;">{risk_level}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with card2:
                    st.markdown(
                        f"""
                        <div style="
                            padding:14px 18px;
                            border-radius:14px;
                            background-color:#34495e;
                            color:white;
                            text-align:center;
                            min-height:95px;
                        ">
                            <div style="font-size:15px; font-weight:600;">責任者共有</div>
                            <div style="font-size:30px; font-weight:700; margin-top:8px;">{manager}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # ----------------------------
                # 全文表示
                # ----------------------------
                st.markdown("### 📋 詳細対応")

                tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
                    "第一声",
                    "返答例",
                    "初動対応",
                    "補償・返金",
                    "NG対応",
                    "記録内容"
                ])

                with tab1:
                    st.markdown(extract_section(answer, "お客様への第一声"))

                with tab2:
                    st.markdown(extract_section(answer, "お客様への返答例"))

                with tab3:
                    st.markdown(extract_section(answer, "スタッフの初動対応"))

                with tab4:
                    st.markdown(extract_section(answer, "補償・返金に関する注意"))

                with tab5:
                    st.markdown(extract_section(answer, "NG対応"))

                with tab6:
                    st.markdown(extract_section(answer, "記録すべき内容"))

                st.markdown("### 📄 全文コピー用")

                with st.expander("全文を表示する"):
                    st.code(answer, language="markdown")

                st.download_button(
                    label="📥 生成結果をテキスト保存",
                    data=st.session_state.answer,
                    file_name="complaint_response.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            except Exception as e:
                st.error("エラーが発生しました。APIキー、課金設定、モデル名を確認してください。")
                st.code(str(e))

st.markdown("---")
st.markdown(
    '<p class="small-note">※本ツールは対応支援用です。返金・補償・法的判断・重大事故対応は必ず責任者判断としてください。</p>',
    unsafe_allow_html=True
)
