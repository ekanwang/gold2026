import streamlit as st
import yfinance as yf
import time
import pandas as pd

# 1. 网页基础配置
st.set_page_config(page_title="大宗商品全球情绪池 v2026.02.21", layout="wide")

st.title("💰 大宗商品全球情绪池 (2026 终极决策版)")
st.caption("集成：避险脱钩判定、美元动量红绿灯、COMEX保证金预警及特朗普政策因子")

# 2. 核心数据抓取函数
@st.cache_data(ttl=60)
def get_market_data():
    results = {"gold": 0.0, "silver": 0.0, "oil": 0.0, "dxy": 0.0, "gold_change": 0.0, "dxy_change": 0.0, "silver_change": 0.0, "oil_change": 0.0}
    tickers = {"gold": "GC=F", "silver": "SI=F", "oil": "BZ=F", "dxy": "DX-Y.NYB"}
    
    for key, symbol in tickers.items():
        try:
            ticker_obj = yf.Ticker(symbol)
            hist = ticker_obj.history(period="2d")
            if len(hist) >= 2:
                results[key] = hist['Close'].iloc[-1]
                change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]
                results[f"{key}_change"] = change
        except Exception:
            pass
    return results

# 同步实时数据
with st.spinner('正在同步 2026.02.21 全球宏观共振信号...'):
    data = get_market_data()
    gold_p, silver_p, oil_p, dxy_p = data["gold"], data["silver"], data["oil"], data["dxy"]
    # 修正白银显示单位
    display_silver = silver_p / 100 if silver_p > 500 else silver_p
    dxy_delta = data['dxy_change'] * 100 

# 3. 顶部实时行情卡片
col1, col2, col3, col4 = st.columns(4)
col1.metric("纽约金 (Gold)", f"${gold_p:,.2f}", f"{data['gold_change']*100:.2f}%")
col2.metric("白银主连 (Silver)", f"${display_silver:,.2f}", f"{data['silver_change']*100:.2f}%")
col3.metric("布伦特原油", f"${oil_p:,.2f}", f"{data['oil_change']*100:.2f}%")
col4.metric("美元指数 (DXY)", f"{dxy_p:.2f}", f"{dxy_delta:+.2f}%")

st.markdown("---")

# 4. 🚦 美元风控决策灯 (修复兼容性版)
st.markdown("### 🚦 美元风控决策灯 (DXY Momentum Alert)")

# 判定逻辑
if dxy_delta > 0.8:
    status_label = "🔴 极端危险：流动性黑洞"
    advice_text = "【绝对不买！】美元正在疯狂吸金，贵金属随时可能发生‘爆仓踩踏’。即使行情看涨，也要管住手，等美元冷静。"
    dxy_penalty = -30
    st.error(status_label)
elif 0.3 <= dxy_delta <= 0.8:
    status_label = "🟡 警惕：货币压制增强"
    advice_text = "【谨慎做多】美元走势强劲。除非此时‘避险系数’是激活状态（金美同涨），否则不要重仓。"
    dxy_penalty = -10
    st.warning(status_label)
elif -0.5 <= dxy_delta < 0.3:
    status_label = "🔵 正常：技术面主导"
    advice_text = "【正常交易】美元波动很小。现在决定金价的是特朗普言论和地缘政治，按原计划操作。"
    dxy_penalty = 0
    st.info(status_label)
else:
    status_label = "🟢 极佳：美元泄洪信号"
    advice_text = "【值得出手】美元大幅撤退！这是金银爆发的温床。如果综合分也高，是极佳的入场时机。"
    dxy_penalty = 15
    st.success(status_label)

with st.expander("🔍 点击查看详细决策建议", expanded=True):
    st.write(f"**当前美元波动：** {dxy_delta:+.2f}%")
    st.markdown(f"**核心建议：** {advice_text}")

st.markdown("---")

# 5. 深度逻辑调节区
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("🛠️ 宏观变量干预")
    trump_val = st.select_slider("1. 特朗普政策/关税强度", 
                               options=["利空/正常", "中性", "10%关税预期", "15%关税震荡"], 
                               value="15%关税震荡")
    trump_score = {"利空/正常": 20, "中性": 50, "10%关税预期": 80, "15%关税震荡": 100}[trump_val]

    fed_status = st.radio("2. 美联储与人事变动", 
                         ["加息预期 (Hawkish)", "不降息/暂停 (Wait)", "降息/Warsh 确认提名 (Dovish)"], 
                         index=2)
    fed_score = {"加息预期 (Hawkish)": 20, "不降息/暂停 (Wait)": 55, "降息/Warsh 确认提名 (Dovish)": 90}[fed_status]

    geo_risk = st.slider("3. 地缘政治风险 (伊朗/中东)", 0, 100, 75)
    margin_stress = st.slider("4. COMEX 保证金压力指数", 0, 100, 30)

with right_col:
    st.subheader("🧠 逻辑监控看板")
    
    # 避险脱钩逻辑
    is_safe_haven_active = data['gold_change'] > 0 and data['dxy_change'] > 0
    if is_safe_haven_active:
        st.warning("🔥 **避险系数：已激活 (Safe-Haven On)**")
        st.caption("逻辑：金美同涨。信用风险已覆盖利率风险。")
    else:
        st.info("ℹ️ **避险系数：休眠**")
        st.caption("逻辑：金美负相关。当前受传统汇率定价逻辑驱动。")

    # 金银比分析
    gs_ratio = gold_p / display_silver if display_silver > 0 else 0
    st.write(f"📊 **当前金银比: {gs_ratio:.2f}**")
    if gs_ratio < 60:
        st.error("⚠️ 白银投机过热，警惕洗盘！")
    elif gs_ratio > 85:
        st.success("💡 白银严重低估，存在补涨逻辑。")

# 6. 综合评分算法
safe_bonus = 25 if is_safe_haven_active else 0
macro_base = 100 - ((dxy_p - 100) * 8)
final_score = (macro_base * 0.2) + (trump_score * 0.25) + (fed_score * 0.2) + (geo_risk * 0.2) + safe_bonus - (margin_stress * 0.15) + dxy_penalty
final_score = max(0, min(100, final_score))

st.markdown("---")

# 7. 最终决策
res_l, res_r = st.columns([1, 2])
with res_l:
    st.header("综合得分")
    st.markdown(f"<h1 style='color: #ff4b4b;'>{final_score:.1f}</h1>", unsafe_allow_html=True)

with res_r:
    st.subheader("🎯 实时出手判定 (2026版)")
    
    current_hour = time.localtime().tm_hour
    is_prime_time = 20 <= current_hour <= 24 or 0 <= current_hour <= 1
    
    if dxy_delta > 0.8:
        st.error("🛑 **【系统强制风控】美元涨幅异常！** 无论得分多高，当前都不建议出手。")
    elif final_score > 80:
        st.success("💎 **【最值得出手时刻】** 全维度逻辑共振。")
    elif final_score > 60:
        st.info("📈 **【偏多震荡】** 支撑较强。")
    else:
        st.error("📉 **【建议观望】** 逻辑不一致或压制过强。")
    
    if is_prime_time:
        st.markdown("⚡ **当前为欧美重叠高流动性时段。**")

st.caption(f"数据更新：{time.strftime('%Y-%m-%d %H:%M:%S')} | 策略引擎：v2026.02.21")