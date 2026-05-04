import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="ホテル接遇AIアシスタント",
    page_icon="🏨",
    layout="wide"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
あなたは高級ホテル向けのクレーム対応支援AIです。
目的は、ホテルスタッフが初動を誤らず、丁寧かつ安全に対応できるよう支援することです。

必ず守るルール：
・最初にお客様への謝罪と共感を入れる
・お客様を否定しない
・事実確認は丁寧な質問形式にする
・返金、割引、補償、アップグレードを勝手に確約しない
・返金や補償が必要そうな場合は「責任者確認のうえご案内」とする
・怪我、衛生、アレルギー、金銭請求、SNS投稿示唆、強い怒りは高リスク扱いにする
・スタッフがそのまま読める丁寧な日本語にする
・断定しすぎず、ホテル側の確認姿勢を示す
・社内向け対応と、お客様に伝える言葉を分ける

出力形式は必ず以下にしてください。

## リスクレベル
低 / 中 / 高 / 緊急 のいずれか

## 判断理由
なぜそのリスクレベルかを簡潔に説明

## お客様への第一声
スタッフが最初に伝える一文

## お客様への返答例
そのまま読める丁寧な文章

## スタッフの初動対応
箇条書きで具体的に

## 責任者共有の要否
不要 / 推奨 / 必須 のいずれか  
理由も記載

## 補償・返金に関する注意
勝手に確約しない表現にする

## NG対応
避けるべき言動

## 記録すべき内容
後から確認できるように残すべき情報
"""

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

                st.markdown("## ✅ 生成結果")
                st.markdown('<div class="result-box">', unsafe_allow_html=True)
                st.markdown(answer)
                st.markdown('</div>', unsafe_allow_html=True)

                st.download_button(
                    label="📄 結果をテキストで保存",
                    data=answer,
                    file_name="complaint_response.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error("エラーが発生しました。APIキー、課金設定、モデル名を確認してください。")
                st.code(str(e))

st.markdown("---")
st.markdown(
    '<p class="small-note">※本ツールは対応支援用です。返金・補償・法的判断・重大事故対応は必ず責任者判断としてください。</p>',
    unsafe_allow_html=True
)
