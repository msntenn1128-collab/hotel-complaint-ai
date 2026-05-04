import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="ホテル接遇AIアシスタント", page_icon="🏨")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SYSTEM_PROMPT = """
あなたは高級ホテル向けのクレーム対応支援AIです。

以下のルールを必ず守ってください。
・まず謝罪する
・お客様を否定しない
・事実確認を入れる
・返金や補償を勝手に確約しない
・必要に応じて責任者共有を促す
・スタッフがそのまま読める丁寧な表現にする

出力形式は以下にしてください。

■お客様への返答例
■スタッフの初動対応
■責任者共有の要否
■NG対応
■記録すべき内容
"""

st.title("🏨 ホテル接遇AIアシスタント")
st.caption("クレーム内容を入力すると、対応文・初動対応・NG対応を生成します。")

complaint = st.text_area("クレーム内容", height=120)
place = st.selectbox("発生場所", ["客室", "フロント", "レストラン", "予約", "チェックアウト後", "その他"])
emotion = st.selectbox("お客様の温度感", ["少し不満", "強く怒っている", "返金要求あり", "SNS投稿を示唆", "責任者を要求"])
urgency = st.selectbox("緊急度", ["低", "中", "高"])
note = st.text_area("補足情報", height=80)

if st.button("対応案を生成する"):
    if not complaint:
        st.warning("クレーム内容を入力してください。")
    else:
        user_prompt = f"""
クレーム内容：
{complaint}

発生場所：
{place}

お客様の温度感：
{emotion}

緊急度：
{urgency}

補足情報：
{note}
"""

        with st.spinner("対応案を生成しています..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )

        answer = response.choices[0].message.content
        st.markdown(answer)