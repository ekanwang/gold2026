import streamlit as st
import yfinance as yf
import time
import pandas as pd
import streamlit.components.v1 as components

# 1. 网页基础配置 (优化为手机视角)
st.set_page_config(page_title="全球大宗情绪池 2026", layout="centered")

# 2. 手机端 UI 样式补丁 (极致适配)
st.markdown("""
    <style>
    /* 隐藏杂项，沉浸式黑色背景 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 1rem 1rem !important; background-color: #0E1117;}
    
    /* 大号卡片，垂直单列堆叠 */
    [data-testid="stMetric"] {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        border: 1px solid #3e4451;
    }
    [data-testid="stMetricValue"] { font-size: 30px !important; color: #00FFCC !important; }
    [data-testid="stMetricLabel"] { font-size: 15px !important; color: #888 !important; }
    
    /* 调整滑动条在手机上的间距 */
    .stSlider { padding-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 3. 抗休眠脚本：每 60 秒触发微小前端通讯，防止 App 进入 Sleeping 状态
components.html("""
    <script>
    setInterval(function(){
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: Date.now()}, '*');
    }, 60000);
    </script>
""", height=0)

# 4. 稳健版实时抓取函数 (解决归零问题)
@st.cache_data(ttl=60)
def get_market_data():
    results = {"gold": 0.0, "silver": 0.0, "oil": 0.0, "dxy": 0.0, 
               "gold_change": 0.0, "dxy_change": 0.0, "silver_change": 0.0, "oil_change": 0.0}
    # 修正原油为 CL=F (美原油) 以获得更高更新频次
    tickers = {"gold": "GC=F", "silver": "SI=F", "oil": "CL=F", "dxy": "DX-Y.NYB"}
    
    for key, symbol in tickers.items():
        try:
            # 回溯 7 天以确保在任何开盘瞬间都能抓到有效收盘价
            obj = yf.Ticker(symbol)
            hist = obj.history(period="7d")
            if not hist.empty:
                # 过滤 NaN 归零行
                valid = hist.dropna(subset=['Close'])
                if len(valid) >= 2:
                    results[key] = valid['Close'].iloc[-1]
                    results[f"{key}_change"] = (valid['Close'].iloc[-1] - valid['Close'].iloc[-2]) / valid['Close'].iloc[-2]
                elif len(valid) == 1:
                    results[key] = valid['Close'].iloc[-1]
        except:
            pass
    return results

# 同步数据
data = get_market_data()
gold_p, silver_p, oil_p, dxy_p = data["gold"], data["silver"], data["oil"], data["dxy"]
display_silver = silver_p
dxy_delta = data['dxy_change'] * 100 

st.title("💰 大宗情绪模型")
st.caption("2026.02.23 决策版 | 实时决策引擎")

# 5. 核心行情展示 (手机大卡片)
st.metric("纽约金 (Gold)", f"${gold_p:,.1f}", f"{data['gold_change']*100:+.2f}%")
st.metric("美元指数 (DXY)", f"{dxy_p:.2f}", f"{dxy_delta:+.2f}%")
st.metric("白银主连 (Silver)", f"${display_silver:,.2f}", f"{data['silver_change']*100:+.2f}%")
st.metric("美原油 (Oil)", f"${oil_p:,.2f}")

st.markdown("---")

# 6. 🚦 美元风控决策灯 (保留你的原始判定)
dxy_penalty = 0
if dxy_delta > 0.8:
    st.error("🔴 极端危险：流动性黑洞")
    advice_text = "【绝对不买！】美元正在疯狂吸金。"
    dxy_penalty = -30
elif 0.3 <= dxy_delta <= 0.8:
    st.warning("🟡 警惕：货币压制增强")
    advice_text = "【谨慎做多】美元走势强劲。"
    dxy_penalty = -10
elif -0.5 <= dxy_delta < 0.3:
    st.info("🔵 正常：技术面主导")
    advice_text = "【正常交易】美元波动很小。"
    dxy_penalty = 0
else:
    st.success("🟢 极佳：美元泄洪信号")
    advice_text = "【值得出手】美元大幅撤退！"
    dxy_penalty = 15

st.caption(f"决策建议：{advice_text}")

# 7. 深度逻辑调节区
st.markdown("### 🛠️ 宏观变量干预")
trump_val = st.select_slider("1. 特朗普政策强度", options=["利空", "中性", "10%关税", "15%关税"], value="15%关税")
trump_score = {"利空": 20, "中性": 50, "10%关税": 80, "15%关税": 100}[trump_val]

geo_risk = st.slider("2. 地缘政治风险 (伊朗/中东)", 0, 100, 75)
margin_stress = st.slider("3. 保证金压力指数", 0, 100, 30)

# 8. 情绪算法内核 (保留你的避险加分逻辑)
is_safe_haven_active = data['gold_change'] > 0 and data['dxy_change'] > 0
safe_bonus = 25 if is_safe_haven_active else 0
macro_base = 100 - ((dxy_p - 100) * 8)
final_score = (macro_base * 0.2) + (trump_score * 0.25) + (geo_risk * 0.3) + safe_bonus - (margin_stress * 0.15) + dxy_penalty
final_score = max(0, min(100, final_score))

st.markdown("---")

# 9. 最终判定输出
res_l, res_r = st.columns([1, 1])
with res_l:
    st.header("综合得分")
    st.title(f"{final_score:.1f}")

with res_r:
    st.subheader("🎯 实时出手判定")
    if dxy_delta > 0.8:
        st.error("🛑 强制风控")
    elif final_score > 80:
        st.success("💎 最值得出手")
    elif final_score > 60:
        st.info("📈 偏多震荡")
    else:
        st.error("📉 建议观望")

# 10. 金银比监控
gs_ratio = gold_p / display_silver if display_silver > 0 else 0
st.caption(f"当前金银比: {gs_ratio:.2f} | 避险系数: {'🔥激活' if is_safe_haven_active else 'ℹ️休眠'}")
st.caption(f"最后刷新: {time.strftime('%H:%M:%S')}")
