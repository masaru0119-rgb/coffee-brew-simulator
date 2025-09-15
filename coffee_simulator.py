import streamlit as st

st.title("コーヒー抽出シミュレーター（ハリオスイッチ向け）")

# --- 入力 ---
beans = st.number_input("豆量 (g)", value=20, min_value=5, max_value=50, step=1)
grind = st.slider("挽き目（数値）", 4.0, 7.0, 5.5, 0.1)
brew_water = st.number_input("注湯量 (g)", value=317, min_value=100, max_value=500, step=1)
final_liquid = st.number_input("最終液量 (g)", value=270, min_value=100, max_value=400, step=1)
brew_time = st.number_input("浸漬時間 (秒)", value=170, min_value=60, max_value=600, step=10)

# --- EY（収率）の簡易モデル ---
# 挽き目が細かいと抽出効率が上がる想定
ey_base = 0.19  # 基準収率19%
ey_correction = (5.5 - grind) * 0.01  # 挽き目補正
ey = ey_base + ey_correction

# 可溶成分量
S = beans * ey  # g

# TDS計算
tds = S / final_liquid  # %

# 結果表示
st.subheader("推定抽出結果")
st.write(f"推定TDS: {tds:.3f}%")
st.write(f"推定収率(EY): {ey*100:.1f}%")
st.write(f"可溶成分量: {S:.2f} g")

# --- 目標TDSとの比較 ---
target_tds = st.number_input("目標TDS (%)", value=1.35, step=0.01)
diff = tds - target_tds
st.write(f"TDS差: {diff:+.3f}%")
if diff < 0:
    st.info("TDSが低めです → 挽き目を細かくするか浸漬時間を少し延ばす")
elif diff > 0:
    st.info("TDSが高めです → 挽き目を粗くするか湯量を少し増やす")
else:
    st.success("TDSは目標値にほぼ一致です！")