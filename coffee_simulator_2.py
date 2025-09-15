import streamlit as st
import pandas as pd
import math

st.title("コーヒー抽出シミュレーター（実測ベース）")

# --- データ保存用（セッション状態） ---
if "results" not in st.session_state:
    st.session_state.results = pd.DataFrame(columns=[
        "名前","豆量","挽き目","注湯量","浸漬時間","TDS","収率","感想"
    ])

# --- 抽出結果入力画面 ---
st.header("抽出結果入力")
with st.form("input_form"):
    name = st.text_input("結果の名前（例: 抽出結果1）")
    beans = st.number_input("豆量 (g)", value=20, min_value=5, max_value=50)
    grind = st.slider("挽き目 (数値)", 4.0, 7.0, 5.5, 0.1)
    brew_water = st.number_input("注湯量 (g)", value=285)
    brew_time = st.number_input("浸漬時間 (秒)", value=170)
    tds = st.number_input("TDS (%)", value=1.35, step=0.01)
    ey = st.number_input("収率 (%)", value=19.0, step=0.1)
    taste = st.text_input("感想")
    submitted = st.form_submit_button("抽出結果を保存")
    
    if submitted and name != "":
        st.session_state.results = pd.concat([
            st.session_state.results,
            pd.DataFrame([{
                "名前": name,
                "豆量": beans,
                "挽き目": grind,
                "注湯量": brew_water,
                "浸漬時間": brew_time,
                "TDS": tds,
                "収率": ey,
                "感想": taste
            }])
        ], ignore_index=True)
        st.success(f"{name} を保存しました！")

# --- 保存結果一覧 & コピー ---
st.header("保存された抽出結果")
if not st.session_state.results.empty:
    st.dataframe(st.session_state.results[["名前","豆量","挽き目","注湯量","浸漬時間","TDS","収率"]])
    
    copy_name = st.selectbox("コピーしてシミュレーションに使う結果を選ぶ", st.session_state.results["名前"])
    if copy_name:
        base = st.session_state.results[st.session_state.results["名前"]==copy_name].iloc[0]

        st.header("抽出シミュレーション")
        beans_sim = st.number_input("豆量 (g)", value=float(base["豆量"]))
        grind_sim = st.slider("挽き目 (数値)", 4.0, 7.0, float(base["挽き目"]), 0.1)
        brew_water_sim = st.number_input("注湯量 (g)", value=float(base["注湯量"]))
        brew_time_sim = st.number_input("浸漬時間 (秒)", value=float(base["浸漬時間"]))

        # --- 推定TDSと収率の簡易モデル ---
        # 基準TDSをコピー元、挽き目・湯量・時間で補正
        tds_base = float(base["TDS"])
        ey_base = float(base["収率"])
        
        # 挽き目補正: 粗くするとTDS減, 細かくするとTDS増
        tds_corr = tds_base * (1 + 0.02*(5.5 - grind_sim))
        
        # 湯量補正: 注湯増えるとTDS減
        tds_corr *= brew_water_sim / float(base["注湯量"])
        
        # 浸漬時間補正: 時間長いとTDS増
        tds_corr *= 1 + 0.0005*(brew_time_sim - float(base["浸漬時間"]))
        
        ey_corr = ey_base * tds_corr / tds_base  # 収率も連動
        
        st.subheader("推定結果")
        st.write(f"TDS: {tds_corr:.3f}%")
        st.write(f"収率: {ey_corr:.1f}%")