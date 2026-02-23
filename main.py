import streamlit as st
import yfinance as yf
import pandas as pd
import streamlit.components.v1 as components

# 1. 页面配置：强制手机全屏感
st.set_page_config(page_title="2026 金融实战终端", layout="centered", initial_sidebar_state="collapsed")

# 2. 注入 CSS：极致暗黑手机适配
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 1rem 1rem !important; background-color: #0E1117;}
    
    /* 大号指标卡片，单列堆叠适合手机 */
    [data-testid="stMetric"] {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border: 1px solid #3e4451;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] { font-size: 38px !important; color: #00FFCC !important; }
    [data-testid="stMetricLabel"] { font-size: 18px !important; color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# 3. 活跃补丁：通过 JS 每分钟微刷新，缓解手机端切后台断连
components.html("""
    <script>
    setInterval(function(){
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: Date.now()}, '*');
    }, 60000);
    </script>
""", height=0)

# 4. 增强版数据抓取：解决“数据归零”
@st.cache_data(ttl=60)
def get_safe_data():
    # 替换了更活跃的合约代码：美原油(CL=F)
    tickers = {
        '纽约金': 'GC=F', 
        '美元指数': 'DX-Y.NYB', 
        '白银主连': 'SI=F', 
        '美原油': 'CL=F'
    }
    results = {}
    for name, ticker in tickers.items():
        try:
            # 抓取 7 天数据，确保跨周末或节假日也能拿到最后有效价
            df = yf.Ticker(ticker).history(period="7d")
            if not df.empty:
                # 过滤空值并取最后一行有效数据
                valid_rows = df.dropna(subset=['Close'])
                current = valid_rows['Close'].iloc[-1]
                # 计算涨跌幅
                if len(valid_rows) >= 2:
                    prev = valid_rows['Close'].iloc[-2]
                    change = (current - prev) / prev
                else:
                    change = 0.0
                results[name] = {"price": current, "change": change}
            else:
                results[name] = {"price": 0.0001, "change": 0.0}
        except:
            results[name] = {"price": 0.0001, "change": 0.0}
    return results

# 5. 渲染主界面
st.title("💰 2026 极客实战灯")
st.caption(f"更新时间: {pd.Timestamp.now().strftime('%H:%M:%S')} (每分钟自动同步)")

data = get_safe_data()

if data:
    # 手机端垂直排列大卡片
    st.metric("纽约金 (Gold)", f"${data['纽约金']['price']:,.1f}", f"{data['纽约金']['change']*100:+.2f}%")
    st.metric("美元指数 (DXY)", f"{data['美元指数']['price']:.2f}", f"{data['美元指数']['change']*100:+.2f}%")
    st.metric("白银 (Silver)", f"${data['白银主连']['price']:,.2f}", f"{data['白银主连']['change']*100:+.2f}%")
    st.metric("美原油 (Oil)", f"${data['美原油']['price']:,.2f}")

    # 6. 对接“极客公园”工作流的判定逻辑
    st.divider()
    dxy_val = data['美元指数']['price']
    dxy_change = data['美元指数']['change']
    
    # 这里可以根据极客公园的具体参数实时修改阈值
    st.subheader("💡 极客公园联动建议")
    
    if dxy_change > 0.005 or dxy_val > 102:
        st.error("🚨 预警：美元动能过强。根据工作流，应收紧止损，暂避多头。")
    elif dxy_change < -0.005 or dxy_val < 96:
        st.success("✅ 信号：美元走势疲软。避险情绪利好黄金，可按计划加码。")
    else:
        st.info("🔵 判定：震荡格局。参考极客公园今日具体的“阻力位”操作。")

st.caption("注：若数据长时间未跳动，请点击 Manage app 菜单中的 Reboot")
