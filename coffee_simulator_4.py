import streamlit as st
import pandas as pd

st.title("コーヒー抽出シミュレーター（完成液量版）")

# --- データ保存用 ---
if "results" not in st.session_state:
    st.session_state.results = pd.DataFrame(columns=[
        "名前","豆量","挽き目","完成液量","浸漬時間","TDS","収率","感想"
    ])

# --- 抽出結果入力画面 ---
st.header("抽出結果入力")
with st.form("input_form"):
    name = st.text_input("結果の名前（例: 抽出結果1）", key="name_input")
    beans = st.number_input("豆量 (g)", value=20, min_value=5, max_value=50, step=1, key="beans_input")
    grind = st.select_slider("挽き目（0.5刻み）",
                             options=[4.0,4.5,5.0,5.5,6.0,6.5,7.0],
                             value=5.5, key="grind_input")
    liquid = st.number_input("完成液量 (g)", value=270, min_value=100, step=1, key="liquid_input")
    brew_time = st.number_input("浸漬時間 (秒)", value=170, min_value=30, step=1, key="brew_time_input")
    tds = st.number_input("TDS (%)", value=1.35, step=0.01, key="tds_input")
    taste = st.text_input("感想", key="taste_input")
    
    # 収率自動計算
    ey = (tds * liquid / beans) * 100  # %
    st.write(f"計算収率(EY): {ey:.1f}%")
    
    submitted = st.form_submit_button("抽出結果を保存")
    
    if submitted and name != "":
        st.session_state.results = pd.concat([
            st.session_state.results,
            pd.DataFrame([{
                "名前": name,
                "豆量": beans,
                "挽き目": grind,
                "完成液量": liquid,
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
    st.dataframe(st.session_state.results[["名前","豆量","挽き目","完成液量","浸漬時間","TDS","収率","感想"]])
    
    copy_name = st.selectbox("コピーしてシミュレーションに使う結果を選ぶ",
                             st.session_state.results["名前"], key="copy_select")
    if copy_name:
        base = st.session_state.results[st.session_state.results["名前"]==copy_name].iloc[0]

        st.header("抽出シミュレーション")

        # --- シミュレーション入力（整数化） ---
        beans_sim = st.number_input("豆量 (g)", value=int(base["豆量"]), step=1, key="beans_sim")
        grind_sim = st.select_slider(
            "挽き目（0.5刻み）",
            options=[4.0,4.5,5.0,5.5,6.0,6.5,7.0],
            value=float(base["挽き目"]),
            key="grind_sim"
        )
        liquid_sim = st.number_input("完成液量 (g)", value=int(base["完成液量"]), step=1, key="liquid_sim")
        brew_time_sim = st.number_input("浸漬時間 (秒)", value=int(base["浸漬時間"]), step=1, key="brew_time_sim")

        # --- 推定TDSと収率の簡易モデル ---
        tds_base = float(base["TDS"])
        tds_corr = tds_base * (1 + 0.02*(5.5 - grind_sim))                  # 挽き目補正
        tds_corr *= float(base["完成液量"]) / liquid_sim                     # 液量補正
        tds_corr *= 1 + 0.0005*(brew_time_sim - float(base["浸漬時間"]))   # 浸漬時間補正
        
        ey_corr = tds_corr * liquid_sim / beans_sim * 100  # 収率計算
        
        st.subheader("推定結果")
        st.write(f"TDS: {tds_corr:.3f}%")
        st.write(f"収率: {ey_corr:.1f}%")

        # --- シミュレーション結果保存フォーム ---
        st.subheader("シミュレーション結果を保存")
        sim_name = st.text_input("保存する結果の名前（例: 抽出結果2）", key="sim_name_input")
        sim_note = st.text_area("感想やメモ（自由入力）", key="sim_note_input")
        if st.button("シミュレーション結果を保存"):
            if sim_name.strip() != "":
                st.session_state.results = pd.concat([
                    st.session_state.results,
                    pd.DataFrame([{
                        "名前": sim_name,
                        "豆量": beans_sim,
                        "挽き目": grind_sim,
                        "完成液量": liquid_sim,
                        "浸漬時間": brew_time_sim,
                        "TDS": tds_corr,
                        "収率": ey_corr,
                        "感想": sim_note if sim_note.strip() != "" else f"シミュレーション元: {copy_name}"
                    }])
                ], ignore_index=True)
                st.success(f"{sim_name} を保存しました！")
            else:
                st.error("保存する結果の名前を入力してください。")