import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 基础配置：强制单列排列，确保手机端数字够大
st.set_page_config(page_title="2026 行情看板", layout="centered")

# 2. 注入 CSS：针对手机屏幕的“精装修”
st.markdown("""
    <style>
    /* 隐藏所有网页杂元素，让它看起来像个真 App */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 1.5rem 1rem !important; background-color: #0E1117;}
    
    /* 强行让所有指标垂直大卡片排列 */
    [data-testid="stMetric"] {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border: 1px solid #3e4451;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    /* 数字颜色与大小 */
    [data-testid="stMetricValue"] {
        font-size: 40px !important;
        color: #00FFCC !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 18px !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💰 个人行情看板")

# 3. 增强版抓取逻辑：彻底解决“数据归零”
@st.cache_data(ttl=60)
def get_clean_data():
    # 修正代码：黄金(GC=F), 美元(DX-Y.NYB), 白银(SI=F), 原油(CL=F)
    tickers = {
        '纽约金 (Gold)': 'GC=F', 
        '美元指数 (DXY)': 'DX-Y.NYB', 
        '白银主连 (Silver)': 'SI=F', 
        '美原油 (Oil)': 'CL=F'
    }
    results = {}
    for name, ticker in tickers.items():
        try:
            # 关键：从 2d 改为 7d，确保即便接口延迟也能抓到最近一个有效价
            data = yf.Ticker(ticker).history(period="7d")
            if not data.empty:
                # 过滤空值，取最后一行有效数据
                valid_data = data.dropna(subset=['Close'])
                current = valid_data['Close'].iloc[-1]
                prev = valid_data['Close'].iloc[-2] if len(valid_data) > 1 else current
                change = (current - prev) / prev
                results[name] = {"price": current, "change": change}
            else:
                results[name] = {"price": 0.0001, "change": 0.0}
        except:
            results[name] = {"price": 0.0001, "change": 0.0}
    return results

data = get_clean_data()

# 4. 纯净展示：手机端垂直大卡片
if data:
    for name, info in data.items():
        # 格式化价格显示
        p_str = f"{info['price']:.2f}" if 'DXY' in name else f"${info['price']:,.2f}"
        st.metric(label=name, value=p_str, delta=f"{info['change']*100:+.2f}%")

st.divider()
st.caption(f"最后同步: {pd.Timestamp.now().strftime('%H:%M:%S')} • 数据源: Yahoo Finance")
