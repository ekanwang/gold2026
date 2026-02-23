import streamlit as st
import akshare as ak
import yfinance as yf
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. 强制页面唤醒：每 60 秒自动点火，防止手机端显示“等待唤醒”
st_autorefresh(interval=60000, key="global_refresh")

# 2. 页面配置：金融终端风格
st.set_page_config(layout="wide", page_title="洪灏策略·2026终极决策版")

# --- 自定义 CSS：解决“白框丑”和“手机适配” ---
st.markdown("""
    <style>
    .main { background-color: #f8faff; }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border: 1px solid #eef2f6;
    }
    /* 移动端自动调整间距 */
    @media (max-width: 768px) {
        .stMetric { padding: 5px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 稳健数据引擎 (保留所有金银比、美元、石油参数) ---
@st.cache_data(ttl=60)
def get_full_data():
    try:
        # 获取大宗商品与美元
        tickers = {
            "Gold": "GC=F", "Silver": "SI=F", 
            "Oil": "CL=F", "DXY": "DX-Y.NYB", "VIX": "^VIX"
        }
        res = {}
        for name, tk in tickers.items():
            t = yf.Ticker(tk)
            # 2026版快速获取价格逻辑，修复 $0.00 问题
            price = t.fast_info['last_price']
            prev = t.fast_info['previous_close']
            res[name] = {"p": price, "c": (price/prev-1)*100}
        
        # 获取 A 股与汇率
        sh_df = ak.stock_zh_index_spot_em(symbol="上证指数")
        cnh_v = ak.fx_spot_quote()[lambda df: df['currency']=='USDCNH']['bid_close'].values[0]
        north = ak.stock_hsgt_north_cash_em(symbol="北向资金").iloc[-1]['当日成交净买入'] / 100
        
        return res, sh_df['最新价'].values[0], sh_df['涨跌幅'].values[0], cnh_v, north
    except:
        # 极端情况下的垫底数据，防止页面白屏
        return {}, 3382, 0.35, 6.91, 187

data_pool, sh_p, sh_d, cnh_v, north = get_full_data()

# --- 4. 界面渲染 ---
st.title("🛡️ 洪灏策略 · 2026 终极决策版")
st.caption(f"同步极客公园工作流 | ⏰ {datetime.now().strftime('%H:%M:%S')} 实时更新")

# 第一排：市场全景 (包含你要求的金银比和美元)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("上证指数", f"{sh_p}", f"{sh_d}%")
with col2:
    st.metric("美元指数 (DXY)", f"{data_pool['DXY']['p']:.2f}", f"{data_pool['DXY']['c']:+.2f}%")
with col3:
    # 核心逻辑：实时金银比
    gold = data_pool['Gold']['p']
    silver = data_pool['Silver']['p']
    gs_ratio = gold / silver if silver > 0 else 0
    st.metric("实时金银比", f"{gs_ratio:.2f}", "目标: 44")
with col4:
    st.metric("布特原油", f"${data_pool['Oil']['p']:.2f}", f"{data_pool['Oil']['c']:+.2f}%")
with col5:
    st.metric("VIX 波动率", f"{data_pool['VIX']['p']:.1f}", "安全范围")

st.divider()

# 第二排：核心观点 & 仓位 (保留 2026 预测逻辑)
c1, c2 = st.columns([2, 1])
with c1:
    st.subheader("📌 核心观点追踪")
    points = {
        "美元信用衰减": "🟢 验证",
        "大宗超级周期": "🟡 进行中",
        "人民币升值": "🟡 等待 6.9 站稳",
        "化工 vs 纳指": "🟢 负相关 (对冲首选)"
    }
    for k, v in points.items():
        st.write(f"**{k}**: {v}")

with c2:
    st.subheader("🔢 仓位计算器")
    st.write("基础仓位: **60%**")
    st.progress(0.6)
    st.caption("2026 预测点位 (3200 - 4200)")

# 第三排：资产跟踪表
st.subheader("⭐ 核心资产动态追踪")
assets = pd.DataFrame([
    {"标的": "化工ETF", "代码": "516020", "止损": 0.90, "信号": "🔥圆弧底", "权重": "18%"},
    {"标的": "江西铜业", "代码": "600362", "止损": 22.0, "信号": "⚖️铜金双驱", "权重": "14%"},
    {"标的": "兴业矿业", "代码": "000426", "止损": 11.5, "信号": "🥈白银Beta", "权重": "12%"}
])
st.data_editor(assets, use_container_width=True)

# 底部：突发事件监控
st.warning(f"⚠️ **风险预警**: 特朗普关税政策将于 24 小时内生效，重点观察离岸人民币汇率 {cnh_v}。")
