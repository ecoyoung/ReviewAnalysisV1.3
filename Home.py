import streamlit as st
import pandas as pd
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import plotly.figure_factory as ff
from utils import process_data, get_download_data, calculate_review_stats, create_pie_chart, analyze_by_group, create_rating_trend_chart, create_rating_heatmap, save_fig_to_html
import base64

# 应用配置 - 可以在这里修改logo和作者信息
APP_CONFIG = {
    "app_title": "Amazon Review Analytics Pro",
    "app_subtitle": "专业的亚马逊评论数据分析平台",
    "author": "海翼IDC团队",
    "version": "v1.2.0",
    "contact": "idc@oceanwing.com",
    # logo_path 可以设置为本地图片路径，或者使用base64编码的图片
    "logo_path": None,  # 设置为图片文件路径，如 "logo.png"
    "company": "Anker Oceanwing Inc."
}

def get_base64_image(image_path):
    """将图片转换为base64编码"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def display_header():
    """显示页面头部信息"""
    # 自定义CSS样式
    st.markdown("""
    <style>
    /* 主要样式 */
    .main-header {
        background: linear-gradient(135deg, #FF9500 0%, #FF6B35 50%, #232F3E 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(255, 149, 0, 0.3);
    }
    
    .app-title {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .app-subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .author-info {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
    }
    
    /* Amazon风格的卡片 */
    .amazon-card {
        background: white;
        border: 1px solid #DDD;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .amazon-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .feature-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 4px solid #FF9500;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .stats-container {
        background: linear-gradient(135deg, #232F3E 0%, #37475A 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .step-indicator {
        background: linear-gradient(135deg, #FF9500 0%, #FF6B35 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .progress-bar {
        background: #e0e0e0;
        border-radius: 10px;
        height: 10px;
        margin: 1rem 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #FF9500, #FF6B35);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #FF9500 0%, #FF6B35 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 149, 0, 0.3);
    }
    
    /* 文件上传区域 */
    .uploadedFile {
        border: 2px dashed #FF9500;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: rgba(255, 149, 0, 0.05);
    }
    
    /* 成功/错误消息样式 */
    .success-message {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #dc3545 0%, #fd7e14 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* 侧边栏样式 */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #232F3E 0%, #37475A 100%);
    }
    
    /* 数据表格样式 */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 页面头部
    header_content = f"""
    <div class="main-header">
        <div class="app-title">🛒 {APP_CONFIG['app_title']}</div>
        <div class="app-subtitle">{APP_CONFIG['app_subtitle']}</div>
        <div class="author-info">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 1.1rem;"><strong>👨‍💻 {APP_CONFIG['author']}</strong></span><br>
                    <span style="font-size: 0.9rem; opacity: 0.8;">{APP_CONFIG['company']}</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.9rem;">{APP_CONFIG['version']}</span><br>
                    <span style="font-size: 0.8rem; opacity: 0.8;">📧 {APP_CONFIG['contact']}</span>
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(header_content, unsafe_allow_html=True)

def display_features():
    """显示功能特性"""
    st.markdown("""
    <div class="amazon-card">
        <h3 style="color: #232F3E; margin-bottom: 1rem;">🚀 平台核心功能</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
            <div class="feature-card">
                <h4 style="color: #FF9500; margin-bottom: 0.5rem;">📊 数据预处理</h4>
                <p style="margin: 0; color: #666;">自动清洗和标准化Amazon评论数据，支持多种格式导入导出</p>
            </div>
            <div class="feature-card">
                <h4 style="color: #FF9500; margin-bottom: 0.5rem;">🌐 评论翻译</h4>
                <p style="margin: 0; color: #666;">智能英文评论翻译为中文，提升VOC分析效率，支持批量处理</p>
            </div>
            <div class="feature-card">
                <h4 style="color: #FF9500; margin-bottom: 0.5rem;">📈 统计分析</h4>
                <p style="margin: 0; color: #666;">全方位的评论数据统计分析，包含情感分析和趋势预测</p>
            </div>
            <div class="feature-card">
                <h4 style="color: #FF9500; margin-bottom: 0.5rem;">🎯 关键词匹配</h4>
                <p style="margin: 0; color: #666;">智能关键词匹配和人群分类，精准洞察用户反馈</p>
            </div>
            <div class="feature-card">
                <h4 style="color: #FF9500; margin-bottom: 0.5rem;">📝 自动化报告(开发中...)</h4>
                <p style="margin: 0; color: #666;">AI赋能一键自动化生成专业的分析报告，支持多种格式导出</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_workflow():
    """显示工作流程"""
    st.markdown("""
    <div class="amazon-card">
        <h3 style="color: #232F3E; margin-bottom: 1.5rem;">📋 分析流程</h3>
        <div style="display: flex; flex-direction: column; gap: 1rem;">
            <div style="display: flex; align-items: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #FF9500;">
                <div style="background: #FF9500; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">1</div>
                <div>
                    <strong style="color: #232F3E;">数据预处理</strong><br>
                    <span style="color: #666; font-size: 0.9rem;">上传Excel文件，自动清洗和标准化数据</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #4CAF50;">
                <div style="background: #4CAF50; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">2</div>
                <div>
                    <strong style="color: #232F3E;">评论翻译</strong><br>
                    <span style="color: #666; font-size: 0.9rem;">智能翻译英文评论为中文，提升分析效率</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #FF6B35;">
                <div style="background: #FF6B35; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">3</div>
                <div>
                    <strong style="color: #232F3E;">统计分析</strong><br>
                    <span style="color: #666; font-size: 0.9rem;">深度分析评论数据，生成可视化图表</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #28a745;">
                <div style="background: #28a745; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">4</div>
                <div>
                    <strong style="color: #232F3E;">关键词匹配</strong><br>
                    <span style="color: #666; font-size: 0.9rem;">基于关键词进行人群分类和特征分析</span>
                </div>
            </div>
            <div style="display: flex; align-items: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #17a2b8;">
                <div style="background: #17a2b8; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">5</div>
                <div>
                    <strong style="color: #232F3E;">报告生成</strong><br>
                    <span style="color: #666; font-size: 0.9rem;">自动生成专业分析报告和数据导出</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_pie_chart(review_counts, title='评论类型分布'):
    # 确保索引顺序与颜色映射一致
    review_counts = review_counts.reindex(
        ['positive', 'neutral', 'negative'], 
        fill_value=0
    )
    
    # 创建数据框确保顺序
    df = pd.DataFrame({
        'type': review_counts.index,
        'count': review_counts.values
    })
    
    fig = px.pie(
        df,
        values='count',
        names='type',
        title=title,
        color='type',  # 关键：通过color参数指定分组
        color_discrete_map={
            'positive': '#2ECC71',  # 绿色
            'neutral': '#F1C40F',   # 黄色
            'negative': '#E74C3C'   # 红色
        },
        category_orders={'type': ['positive', 'neutral', 'negative']}
    )
    
    # 禁用主题干扰
    fig.update_layout(template='none')
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        marker=dict(line=dict(color='#FFFFFF', width=1))  # 添加白色边框
    )
    return fig

def analyze_by_group(df, group_by):
    """按指定字段进行分组分析"""
    # 始终计算ASIN维度的统计信息
    asin_stats = df.groupby('Asin').agg({
        'Rating': ['count', 'mean', 'std'],
        'Review Type': lambda x: x.value_counts().to_dict()
    }).round(2)
    
    # 重命名列
    asin_stats.columns = ['评论数量', '平均评分', '标准差', '评论类型分布']
    
    # 计算ASIN的评分分布
    rating_dist = df.groupby(['Asin', 'Rating']).size().unstack(fill_value=0)
    rating_dist_pct = rating_dist.div(rating_dist.sum(axis=1), axis=0) * 100
    
    # 如果是Asin+Model分析，创建组合数据用于时间趋势图
    if isinstance(group_by, list):
        df['Group'] = df['Asin'] + ' - ' + df['Model']
        group_by_trend = 'Group'
    else:
        group_by_trend = 'Asin'
    
    return asin_stats, rating_dist_pct, group_by_trend

def create_rating_trend_chart(df, group_by):
    """创建评分趋势图"""
    # 按时间和分组计算平均评分
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    trend_data = df.groupby(['Month', group_by])['Rating'].mean().reset_index()
    
    # 创建趋势图
    title = 'Asin-Model组合随时间的平均评分变化' if group_by == 'Group' else 'Asin随时间的平均评分变化'
    
    fig = px.line(trend_data, 
                  x='Month', 
                  y='Rating', 
                  color=group_by,
                  title=title,
                  labels={'Rating': '平均评分', 'Month': '月份'})
    
    fig.update_xaxes(tickangle=45)
    return fig

def create_rating_heatmap(rating_dist_pct, title):
    """创建评分分布热力图"""
    fig = go.Figure(data=go.Heatmap(
        z=rating_dist_pct.values,
        x=rating_dist_pct.columns,
        y=rating_dist_pct.index,
        colorscale='RdYlGn',
        text=rating_dist_pct.round(1).values,
        texttemplate='%{text}%',
        textfont={"size": 10},
        hoverongaps=False))
    
    fig.update_layout(
        title=title,
        xaxis_title='评分',
        yaxis_title='产品',
        height=max(300, len(rating_dist_pct) * 30))
    
    return fig

def save_fig_to_html(fig, filename):
    """保存图表为HTML文件"""
    return fig.to_html()

def process_uploaded_file(uploaded_file):
    """处理上传的文件"""
    try:
        # 根据文件类型选择读取方法
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("不支持的文件格式，请上传CSV或Excel文件")
            return None
        
        # 检查必要的列
        required_columns = ['Asin', 'Title', 'Content', 'Rating', 'Date']
        if not all(col in df.columns for col in required_columns):
            st.error(f"文件缺少必要的列：{', '.join(required_columns)}")
            return None
        
        return df
    except Exception as e:
        st.error(f"处理文件时出错：{str(e)}")
        return None

def process_brand_file(uploaded_file):
    """处理品牌文件"""
    try:
        if uploaded_file.name.endswith('.csv'):
            brand_df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            brand_df = pd.read_excel(uploaded_file)
        else:
            st.error("不支持的文件格式，请上传CSV或Excel文件")
            return None
        
        # 检查必要的列
        if not all(col in brand_df.columns for col in ['ASIN', 'Brand']):
            st.error("品牌文件必须包含 'ASIN' 和 'Brand' 列")
            return None
        
        # 清理数据
        brand_df['ASIN'] = brand_df['ASIN'].astype(str).str.strip()
        brand_df['Brand'] = brand_df['Brand'].astype(str).str.strip()
        
        # 重命名列以匹配主数据
        brand_df = brand_df.rename(columns={'ASIN': 'Asin'})
        
        return brand_df
    except Exception as e:
        st.error(f"处理品牌文件时出错：{str(e)}")
        return None

def main():
    st.set_page_config(
        page_title=APP_CONFIG['app_title'],
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 显示头部信息
    display_header()
    
    # 显示功能特性
    display_features()
    
    # 侧边栏信息
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #232F3E 0%, #37475A 100%); color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: #FF9500; margin-bottom: 0.5rem;">📚 使用指南</h3>
            <div style="font-size: 0.9rem; line-height: 1.6;">
                <p><strong>Step 1:</strong> 上传Excel文件</p>
                <p><strong>Step 2:</strong> 数据预处理</p>
                <p><strong>Step 3:</strong> 评论翻译(可选)</p>
                <p><strong>Step 4:</strong> 统计分析</p>
                <p><strong>Step 5:</strong> 下载报告</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(255, 149, 0, 0.1); padding: 1rem; border-radius: 10px; border-left: 4px solid #FF9500;">
            <h4 style="color: #FF9500; margin-bottom: 0.5rem;">💡 小贴士</h4>
            <ul style="font-size: 0.9rem; color: #666;">
                <li>支持.xlsx和.xls格式</li>
                <li>建议文件大小不超过50MB</li>
                <li>确保数据包含必要字段</li>
                <li>英文评论可翻译为中文</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 显示工作流程
    display_workflow()
    
    # 进度指示器
    st.markdown('<div class="step-indicator">📊 第一步：数据预处理</div>', unsafe_allow_html=True)
    
    # 初始化session state
    if 'processed_df' not in st.session_state:
        st.session_state.processed_df = None
    if 'file_processed' not in st.session_state:
        st.session_state.file_processed = False
    
    # 文件上传区域
    st.markdown("""
    <div class="amazon-card">
        <h3 style="color: #232F3E; margin-bottom: 1rem;">📂 数据上传</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_file = st.file_uploader(
            "选择评论数据Excel文件", 
            type=['xlsx', 'xls'],
            help="请上传包含Amazon评论数据的Excel文件"
        )
    
    with col2:
        brand_file = st.file_uploader(
            "选择品牌数据Excel文件（可选）", 
            type=['xlsx', 'xls'],
            help="请上传包含ASIN和Brand对应关系的Excel文件"
        )
    
    if uploaded_file is not None:
        try:
            if 'original_df' not in st.session_state:
                st.session_state.original_df = None
            if 'brand_df' not in st.session_state:
                st.session_state.brand_df = None
            if not st.session_state.file_processed:
                df = pd.read_excel(uploaded_file)
                st.session_state.original_df = df
                
                # 如果上传了品牌数据，读取并存储
                if brand_file is not None:
                    brand_df = pd.read_excel(brand_file)
                    st.session_state.brand_df = brand_df
                    st.success("✅ 品牌数据上传成功！")
                
                # 显示原始数据信息
                st.markdown("""
                <div class="amazon-card">
                    <h3 style="color: #232F3E; margin-bottom: 1rem;">📋 原始数据概览</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 总行数", f"{len(df):,}")
                with col2:
                    st.metric("📈 总列数", len(df.columns))
                with col3:
                    st.metric("💾 文件大小", f"{uploaded_file.size / 1024 / 1024:.2f} MB")
                
                # 数据预览
                with st.expander("🔍 查看原始数据预览", expanded=False):
                    st.write("**列名信息:**", list(df.columns))
                    st.dataframe(df.head(10), use_container_width=True)
                
                # 数据处理按钮
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 开始数据处理", type="primary", use_container_width=True):
                    with st.spinner('正在处理数据，请稍候...'):
                        try:
                            # 读取品牌数据（如果上传了的话）
                            brand_df = None
                            if brand_file is not None:
                                brand_df = pd.read_excel(brand_file)
                                st.write("品牌数据预览：", brand_df.head())
                                st.write("品牌数据列名：", brand_df.columns.tolist())
                                
                                if 'ASIN' not in brand_df.columns or 'Brand' not in brand_df.columns:
                                    st.warning("品牌数据缺少必要的列（ASIN或Brand），将跳过品牌关联")
                                    brand_df = None
                                else:
                                    st.success("✅ 成功读取品牌数据")
                            
                            # 处理数据
                            processed_df = process_data(df, brand_df)
                            
                            if processed_df is not None:
                                st.write("处理后的数据列名：", processed_df.columns.tolist())
                                st.session_state.processed_df = processed_df
                                st.session_state.file_processed = True
                                st.rerun()
                        except Exception as e:
                            st.error(f"处理数据时出错: {str(e)}")
            
            if st.session_state.file_processed and st.session_state.processed_df is not None:
                processed_df = st.session_state.processed_df
                
                # 处理成功消息
                st.markdown("""
                <div class="success-message">
                    <h4 style="margin: 0; color: white;">✅ 数据处理完成！</h4>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">数据已成功清洗和标准化，可以进行下一步分析</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 处理后数据信息
                st.markdown("""
                <div class="amazon-card">
                    <h3 style="color: #232F3E; margin-bottom: 1rem;">📊 处理后数据信息</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("✅ 处理后行数", f"{len(processed_df):,}")
                with col2:
                    st.metric("📋 列数", len(processed_df.columns))
                with col3:
                    original_df = st.session_state.original_df
                    if original_df is not None:
                        # 修改清洗率计算逻辑
                        original_rows = len(original_df)
                        processed_rows = len(processed_df)
                        if original_rows > 0:
                            data_reduction = ((original_rows - processed_rows) / original_rows * 100)
                            # 确保清洗率在合理范围内
                            data_reduction = max(min(data_reduction, 100), 0)
                        else:
                            data_reduction = 0
                    else:
                        data_reduction = 0
                    st.metric("🔄 数据清洗率", f"{data_reduction:.1f}%")
                with col4:
                    if 'Review Type' in processed_df.columns:
                        positive_rate = (processed_df['Review Type'] == 'positive').mean() * 100
                        st.metric("😊 正面评论占比", f"{positive_rate:.1f}%")
                
                # 添加品牌关联功能
                st.markdown("""
                <div class="amazon-card">
                    <h3 style="color: #232F3E; margin-bottom: 1rem;">🏷️ 品牌信息关联</h3>
                </div>
                """, unsafe_allow_html=True)
                
                brand_file = st.file_uploader(
                    "上传品牌数据文件（包含ASIN和Brand列）",
                    type=['xlsx', 'xls'],
                    help="请上传包含ASIN和Brand对应关系的Excel文件"
                )
                
                if brand_file is not None:
                    try:
                        brand_df = pd.read_excel(brand_file)
                        if 'ASIN' in brand_df.columns and 'Brand' in brand_df.columns:
                            # 清理品牌数据
                            brand_df['ASIN'] = brand_df['ASIN'].astype(str).str.strip()
                            brand_df['Brand'] = brand_df['Brand'].astype(str).str.strip()
                            
                            # 处理重复的ASIN，保留最新的品牌信息
                            brand_df = brand_df.drop_duplicates(subset=['ASIN'], keep='last')
                            
                            # 重命名ASIN列为Asin以匹配主数据
                            brand_df = brand_df.rename(columns={'ASIN': 'Asin'})
                            
                            # 确保processed_df中有Brand列，如果没有则添加
                            if 'Brand' not in processed_df.columns:
                                processed_df['Brand'] = None
                            
                            # 关联品牌信息前先备份原始ID
                            original_ids = processed_df['ID'].copy()
                            
                            # 关联品牌信息
                            processed_df = processed_df.merge(
                                brand_df[['Asin', 'Brand']], 
                                on='Asin', 
                                how='left',
                                suffixes=('', '_new')
                            )
                            
                            # 如果存在重复的Brand列，保留新的Brand列
                            if 'Brand_new' in processed_df.columns:
                                processed_df['Brand'] = processed_df['Brand_new']
                                processed_df = processed_df.drop(columns=['Brand_new'])
                            
                            # 恢复原始ID
                            processed_df['ID'] = original_ids
                            
                            # 重新排序列
                            columns = processed_df.columns.tolist()
                            if 'Brand' in columns:
                                columns.remove('Brand')
                            asin_index = columns.index('Asin')
                            columns.insert(asin_index + 1, 'Brand')
                            processed_df = processed_df[columns]
                            
                            # 更新session state
                            st.session_state.processed_df = processed_df
                            
                            st.success(f"✅ 成功关联品牌数据！共关联 {processed_df['Brand'].notna().sum()} 条记录")
                            
                            # 显示更新后的数据预览
                            with st.expander("📈 查看更新后的数据预览", expanded=True):
                                st.write("**更新后的列名:**", list(processed_df.columns))
                                st.dataframe(processed_df.head(10), use_container_width=True)
                        else:
                            st.error("品牌数据文件必须包含 'ASIN' 和 'Brand' 列")
                    except Exception as e:
                        st.error(f"处理品牌数据时出错: {str(e)}")
                
                # 处理后数据预览
                with st.expander("📈 查看处理后数据预览", expanded=True):
                    st.write("**处理后列名:**", list(processed_df.columns))
                    st.dataframe(processed_df.head(10), use_container_width=True)
                
                # 下载区域
                st.markdown("""
                <div class="amazon-card">
                    <h3 style="color: #232F3E; margin-bottom: 1rem;">📥 数据下载</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    review_type = st.selectbox(
                        "📝 选择要下载的评论类型",
                        ["全部评论", "positive", "neutral", "negative"],
                        help="选择特定类型的评论进行下载"
                    )
                
                with col2:
                    file_format = st.radio(
                        "📄 选择下载格式", 
                        ["Excel", "TXT"],
                        help="选择适合的文件格式"
                    )
                
                # 根据选择筛选数据
                if review_type != "全部评论":
                    download_df = processed_df[processed_df['Review Type'] == review_type.lower()]
                else:
                    download_df = processed_df
                
                # 显示下载数据统计
                st.info(f"📊 将下载 {len(download_df):,} 条记录")
                
                # 下载按钮
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if file_format == "Excel":
                        file_data = get_download_data(download_df, 'excel')
                        st.download_button(
                            label="📥 下载Excel文件",
                            data=file_data,
                            file_name=f"amazon_reviews_{review_type.lower()}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary",
                            use_container_width=True
                        )
                    else:
                        file_data = get_download_data(download_df, 'txt')
                        st.download_button(
                            label="📥 下载TXT文件",
                            data=file_data,
                            file_name=f"amazon_reviews_{review_type.lower()}.txt",
                            mime="text/plain",
                            type="primary",
                            use_container_width=True
                        )
                
                # 操作按钮
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                
                with col1:
                     if st.button("🔄 清除数据重新开始", use_container_width=True):
                        st.session_state.processed_df = None
                        st.session_state.file_processed = False
                        st.session_state.original_df = None
                        st.session_state.brand_df = None
                        st.rerun()
                
                with col2:
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                                color: white; padding: 0.75rem; border-radius: 8px; text-align: center; margin-top: 0.5rem;">
                        <strong>🎉 准备就绪！</strong><br>
                        <small>可选择"Translation"翻译英文评论，或前往"Statistics"进行统计分析</small>
                    </div>
                    """, unsafe_allow_html=True)
                        
        except Exception as e:
            st.markdown(f"""
            <div class="error-message">
                <h4 style="margin: 0; color: white;">❌ 处理文件时出错</h4>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">错误信息: {str(e)}</p>
                <small style="opacity: 0.8;">请检查文件格式是否正确，或联系技术支持</small>
            </div>
            """, unsafe_allow_html=True)
    
    # 页面底部信息
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; text-align: center; margin-top: 2rem;">
        <div style="color: #666; margin-bottom: 1rem;">
            <strong style="color: #FF9500;">Amazon Review Analytics Pro</strong> - 
            专业的亚马逊评论数据分析平台
        </div>
        <div style="font-size: 0.9rem; color: #999;">
            Powered by Streamlit | Made with ❤️ by {author}
        </div>
    </div>
    """.format(author=APP_CONFIG['author']), unsafe_allow_html=True)

if __name__ == "__main__":
    main()