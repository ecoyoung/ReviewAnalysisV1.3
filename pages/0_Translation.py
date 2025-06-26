import streamlit as st
import pandas as pd
import io
import time
import plotly.express as px
import plotly.graph_objects as go
from utils import get_download_data, create_translator, filter_dataframe, get_cache_stats, clear_expired_cache
from datetime import datetime
import base64

# 页面配置
st.set_page_config(
    page_title="评论翻译工具",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

def display_header():
    """显示页面头部信息"""
    st.markdown("""
    <style>
    .translation-header {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 50%, #2E7D32 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(76, 175, 80, 0.3);
    }
    
    .translation-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .translation-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    .translation-card {
        background: white;
        border: 1px solid #DDD;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .translation-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .progress-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .stats-box {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .error-box {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    header_content = """
    <div class="translation-header">
        <div class="translation-title">🌐 评论翻译工具</div>
        <div class="translation-subtitle">智能评论翻译，提升VOC分析效率</div>
        <div style="background: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 1rem; margin-top: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <span style="font-size: 1.1rem;"><strong>🔧 功能特性</strong></span><br>
                    <span style="font-size: 0.9rem; opacity: 0.8;">智能缓存 | 高级筛选 | 批量翻译 | 进度监控</span>
                </div>
                <div style="text-align: right;">
                    <span style="font-size: 0.9rem;">Powered by Google/腾讯翻译</span><br>
                    <span style="font-size: 0.8rem; opacity: 0.8;">支持英文→中文</span>
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(header_content, unsafe_allow_html=True)

def translate_text(text, translator, max_retries=3):
    """翻译单个文本，带重试机制和质量优化"""
    if not text or pd.isna(text) or str(text).strip() == '':
        return ''
    
    text = str(text).strip()
    
    # 预处理文本，提高翻译质量
    text = preprocess_text_for_translation(text)
    
    for attempt in range(max_retries):
        try:
            # 如果文本太长，分段翻译
            if len(text) > 4000:
                # 按句子分割
                sentences = text.split('. ')
                translated_parts = []
                current_part = ""
                
                for sentence in sentences:
                    if len(current_part + sentence) < 4000:
                        current_part += sentence + ". "
                    else:
                        if current_part:
                            translated_parts.append(translator.translate(current_part.strip()))
                        current_part = sentence + ". "
                
                if current_part:
                    translated_parts.append(translator.translate(current_part.strip()))
                
                result = ' '.join(translated_parts)
            else:
                result = translator.translate(text)
            
            # 后处理翻译结果，提高质量
            result = postprocess_translation(result)
            
            return result
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # 等待1秒后重试
                continue
            else:
                st.error(f"翻译失败: {str(e)}")
                return f"[翻译错误: {text[:50]}...]"

def preprocess_text_for_translation(text):
    """预处理文本，提高翻译质量"""
    # 移除多余的空白字符
    text = ' '.join(text.split())
    
    # 处理常见的电商术语和缩写
    text = text.replace('ASIN', 'ASIN')  # 保持ASIN不变
    text = text.replace('USB-C', 'USB-C')  # 保持技术术语不变
    text = text.replace('HDMI', 'HDMI')
    text = text.replace('WiFi', 'WiFi')
    text = text.replace('Bluetooth', 'Bluetooth')
    
    # 处理评分相关文本
    text = text.replace('5 stars', '5星')
    text = text.replace('4 stars', '4星')
    text = text.replace('3 stars', '3星')
    text = text.replace('2 stars', '2星')
    text = text.replace('1 star', '1星')
    
    return text

def postprocess_translation(translated_text):
    """后处理翻译结果，提高质量"""
    if not translated_text:
        return translated_text
    
    # 修复常见的翻译错误
    corrections = {
        'ASIN': 'ASIN',  # 保持ASIN不变
        'USB-C': 'USB-C',
        'HDMI': 'HDMI',
        'WiFi': 'WiFi',
        'Bluetooth': 'Bluetooth',
        '5星': '5星',
        '4星': '4星',
        '3星': '3星',
        '2星': '2星',
        '1星': '1星'
    }
    
    for original, corrected in corrections.items():
        translated_text = translated_text.replace(original, corrected)
    
    # 修复标点符号
    translated_text = translated_text.replace('。。', '。')
    translated_text = translated_text.replace('，，', '，')
    translated_text = translated_text.replace('！！', '！')
    translated_text = translated_text.replace('？？', '？')
    
    return translated_text

def translate_dataframe(df, columns_to_translate, progress_bar, status_text, engine='google', secret_id=None, secret_key=None, filters=None):
    """批量翻译DataFrame中的指定列"""
    try:
        translator = create_translator(engine, secret_id, secret_key)
    except Exception as e:
        st.error(f"创建翻译器失败: {str(e)}")
        return df, 0, 0, 0
    
    # 应用筛选条件
    if filters:
        df = filter_dataframe(df, filters)
    
    # 创建翻译后的DataFrame副本
    df_translated = df.copy()
    
    # 为每个要翻译的列创建对应的中文列
    translation_mapping = {}
    for col in columns_to_translate:
        if col in df.columns:
            chinese_col = f"{col}_中文"
            df_translated[chinese_col] = ''
            translation_mapping[col] = chinese_col
    
    total_rows = len(df)
    translated_count = 0
    error_count = 0
    cached_count = 0
    
    # 获取缓存统计
    cache_stats = get_cache_stats()
    
    # 翻译进度
    for idx, row in df.iterrows():
        try:
            for original_col, chinese_col in translation_mapping.items():
                if pd.notna(row[original_col]) and str(row[original_col]).strip():
                    # 检查是否已有翻译
                    if chinese_col in df_translated.columns and pd.notna(df_translated.at[idx, chinese_col]) and str(df_translated.at[idx, chinese_col]).strip():
                        cached_count += 1
                        continue
                    
                    translated_text = translate_text(row[original_col], translator)
                    df_translated.at[idx, chinese_col] = translated_text
            
            translated_count += 1
            
            # 更新进度
            progress = (idx + 1) / total_rows
            progress_bar.progress(progress)
            status_text.text(f"正在翻译... {idx + 1}/{total_rows} ({progress:.1%}) - 缓存命中: {cached_count}")
            
            # 添加小延迟避免API限制
            time.sleep(0.1)
            
        except Exception as e:
            error_count += 1
            st.error(f"第 {idx + 1} 行翻译失败: {str(e)}")
            continue
    
    return df_translated, translated_count, error_count, cached_count

def main():
    # 显示头部
    display_header()
    
    # 侧边栏配置
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: white; margin-bottom: 0.5rem;">🌐 翻译设置</h3>
            <div style="font-size: 0.9rem; line-height: 1.6;">
                <p><strong>源语言:</strong> 英语 (en)</p>
                <p><strong>目标语言:</strong> 中文 (zh-CN)</p>
                <p><strong>翻译引擎:</strong> Google/腾讯</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 缓存管理面板
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: white; margin-bottom: 0.5rem;">💾 智能缓存</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 显示缓存统计
        cache_stats = get_cache_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📁 缓存文件", f"{cache_stats['valid_files']}/{cache_stats['total_files']}")
        with col2:
            st.metric("💾 缓存大小", f"{cache_stats['total_size_mb']:.1f}MB")
        
        # 缓存管理按钮
        if st.button("🗑️ 清理过期缓存", use_container_width=True):
            clear_expired_cache()
            st.success("✅ 过期缓存已清理")
            st.rerun()
        
        st.markdown("""
        <div style="background: rgba(76, 175, 80, 0.1); padding: 1rem; border-radius: 10px; border-left: 4px solid #4CAF50;">
            <h4 style="color: #4CAF50; margin-bottom: 0.5rem;">💡 使用提示</h4>
            <ul style="font-size: 0.9rem; color: #666;">
                <li>支持批量翻译多个列</li>
                <li>智能缓存避免重复翻译</li>
                <li>高级筛选精确控制范围</li>
                <li>实时进度监控</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(255, 193, 7, 0.1); padding: 1rem; border-radius: 10px; border-left: 4px solid #FFC107;">
            <h4 style="color: #FFC107; margin-bottom: 0.5rem;">⚠️ 翻译质量说明</h4>
            <ul style="font-size: 0.9rem; color: #666;">
                <li>Google翻译可能存在不准确情况</li>
                <li>建议翻译后人工检查重要内容</li>
                <li>专业术语会自动保持原样</li>
                <li>可考虑使用专业翻译API提升质量</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # 检查是否有处理后的数据
    if 'processed_df' not in st.session_state or st.session_state.processed_df is None:
        st.markdown("""
        <div class="error-box">
            <h4 style="margin: 0; color: white;">⚠️ 没有可翻译的数据</h4>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">请先在首页上传并处理数据，然后再进行翻译</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="translation-card">
            <h3 style="color: #2E7D32; margin-bottom: 1rem;">📋 翻译流程</h3>
            <div style="display: flex; flex-direction: column; gap: 1rem;">
                <div style="display: flex; align-items: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #4CAF50;">
                    <div style="background: #4CAF50; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">1</div>
                    <div>
                        <strong style="color: #2E7D32;">数据预处理</strong><br>
                        <span style="color: #666; font-size: 0.9rem;">在首页上传并处理Excel数据</span>
                    </div>
                </div>
                <div style="display: flex; align-items: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #45a049;">
                    <div style="background: #45a049; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">2</div>
                    <div>
                        <strong style="color: #2E7D32;">选择翻译列</strong><br>
                        <span style="color: #666; font-size: 0.9rem;">选择需要翻译的文本列</span>
                    </div>
                </div>
                <div style="display: flex; align-items: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #4CAF50;">
                    <div style="background: #4CAF50; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">3</div>
                    <div>
                        <strong style="color: #2E7D32;">开始翻译</strong><br>
                        <span style="color: #666; font-size: 0.9rem;">批量翻译并监控进度</span>
                    </div>
                </div>
                <div style="display: flex; align-items: center; padding: 1rem; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #2E7D32;">
                    <div style="background: #2E7D32; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 1rem; font-weight: bold;">4</div>
                    <div>
                        <strong style="color: #2E7D32;">下载结果</strong><br>
                        <span style="color: #666; font-size: 0.9rem;">下载翻译后的数据文件</span>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return
    
    # 获取处理后的数据
    df = st.session_state.processed_df
    
    # 显示数据概览
    st.markdown("""
    <div class="translation-card">
        <h3 style="color: #2E7D32; margin-bottom: 1rem;">📊 数据概览</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 总行数", f"{len(df):,}")
    with col2:
        st.metric("📊 总列数", len(df.columns))
    with col3:
        text_columns = [col for col in df.columns if df[col].dtype == 'object']
        st.metric("📝 文本列数", len(text_columns))
    with col4:
        if 'Title' in df.columns and 'Content' in df.columns:
            title_count = df['Title'].notna().sum()
            content_count = df['Content'].notna().sum()
            st.metric("💬 评论数量", f"{max(title_count, content_count):,}")
    
    # 选择要翻译的列
    st.markdown("""
    <div class="translation-card">
        <h3 style="color: #2E7D32; margin-bottom: 1rem;">🎯 翻译设置</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 获取文本列
    text_columns = [col for col in df.columns if df[col].dtype == 'object' and col not in ['ID', 'Asin', 'Brand', 'Model', 'Rating', 'Date', 'Review Type']]
    
    if not text_columns:
        st.warning("没有找到可翻译的文本列")
        return
    
    # 选择要翻译的列
    selected_columns = st.multiselect(
        "选择要翻译的列:",
        text_columns,
        default=['Content'] if 'Title' in text_columns and 'Content' in text_columns else text_columns[:2],
        help="选择需要翻译为中文的文本列"
    )
    
    if not selected_columns:
        st.warning("请至少选择一列进行翻译")
        return
    
    # 高级筛选设置
    st.markdown("""
    <div class="translation-card">
        <h3 style="color: #2E7D32; margin-bottom: 1rem;">🎯 高级筛选设置</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建筛选条件
    filters = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 品牌筛选
        if 'Brand' in df.columns:
            brands = ['全部'] + sorted(df['Brand'].dropna().unique().tolist())
            selected_brand = st.selectbox(
                "选择品牌:",
                brands,
                help="筛选特定品牌的评论进行翻译"
            )
            if selected_brand != '全部':
                filters['Brand'] = selected_brand
        
        # ASIN筛选
        if 'Asin' in df.columns:
            asins = ['全部'] + sorted(df['Asin'].dropna().unique().tolist())
            selected_asin = st.selectbox(
                "选择ASIN:",
                asins,
                help="筛选特定产品的评论进行翻译"
            )
            if selected_asin != '全部':
                filters['Asin'] = selected_asin
    
    with col2:
        # 评分筛选
        if 'Rating' in df.columns:
            ratings = ['全部'] + sorted(df['Rating'].dropna().unique().tolist())
            selected_rating = st.selectbox(
                "选择评分:",
                ratings,
                help="筛选特定评分的评论进行翻译"
            )
            if selected_rating != '全部':
                filters['Rating'] = selected_rating
        
        # 评论类型筛选
        if 'Review Type' in df.columns:
            review_types = ['全部'] + sorted(df['Review Type'].dropna().unique().tolist())
            selected_review_type = st.selectbox(
                "选择评论类型:",
                review_types,
                help="筛选特定类型的评论进行翻译"
            )
            if selected_review_type != '全部':
                filters['Review Type'] = selected_review_type
    
    # 行范围筛选
    st.markdown("""
    <div class="translation-card">
        <h4 style="color: #2E7D32; margin-bottom: 1rem;">📊 行范围设置</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        use_row_range = st.checkbox(
            "启用行范围筛选",
            value=False,
            help="限制翻译的行数范围"
        )
    
    with col2:
        if use_row_range:
            start_row = st.number_input(
                "起始行",
                min_value=0,
                max_value=len(df)-1,
                value=0,
                help="开始翻译的行号（从0开始）"
            )
    
    with col3:
        if use_row_range:
            end_row = st.number_input(
                "结束行",
                min_value=start_row+1,
                max_value=len(df),
                value=min(start_row+100, len(df)),
                help="结束翻译的行号（不包含）"
            )
            filters['row_range'] = (start_row, end_row)
    
    # 显示筛选后的数据统计
    if filters:
        filtered_df = filter_dataframe(df, filters)
        st.markdown("""
        <div class="translation-card">
            <h4 style="color: #2E7D32; margin-bottom: 1rem;">📈 筛选结果统计</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔍 筛选后行数", f"{len(filtered_df):,}")
        with col2:
            st.metric("📊 筛选前行数", f"{len(df):,}")
        with col3:
            filter_ratio = (len(filtered_df) / len(df) * 100) if len(df) > 0 else 0
            st.metric("📈 筛选比例", f"{filter_ratio:.1f}%")
        with col4:
            if 'Rating' in filtered_df.columns:
                avg_rating = filtered_df['Rating'].mean()
                st.metric("⭐ 平均评分", f"{avg_rating:.1f}")
    
    # 显示选中列的统计信息
    st.markdown("""
    <div class="translation-card">
        <h3 style="color: #2E7D32; margin-bottom: 1rem;">📈 翻译预览</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用筛选后的数据或原始数据
    preview_df = filtered_df if filters else df
    
    preview_data = []
    for col in selected_columns:
        if col in preview_df.columns:
            total_count = len(preview_df)
            non_empty_count = preview_df[col].notna().sum()
            empty_count = total_count - non_empty_count
            
            preview_data.append({
                '列名': col,
                '总行数': total_count,
                '非空行数': non_empty_count,
                '空行数': empty_count,
                '非空率': f"{(non_empty_count/total_count*100):.1f}%"
            })
    
    if preview_data:
        preview_df_stats = pd.DataFrame(preview_data)
        st.dataframe(preview_df_stats, use_container_width=True)
        
        # 显示示例数据
        with st.expander("🔍 查看示例数据", expanded=False):
            for col in selected_columns:
                if col in preview_df.columns:
                    st.write(f"**{col} 列示例:**")
                    sample_data = preview_df[col].dropna().head(3)
                    for i, text in enumerate(sample_data, 1):
                        st.write(f"{i}. {text[:100]}{'...' if len(str(text)) > 100 else ''}")
                    st.write("---")
    
    # 翻译控制
    st.markdown("""
    <div class="translation-card">
        <h3 style="color: #2E7D32; margin-bottom: 1rem;">🚀 开始翻译</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 翻译引擎选择
    st.markdown("""
    <div class="translation-card">
        <h4 style="color: #2E7D32; margin-bottom: 1rem;">🔧 翻译引擎设置</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        translation_engine = st.selectbox(
            "选择翻译引擎",
            ["Google翻译", "腾讯翻译API"],
            help="Google翻译免费但可能不够准确，腾讯翻译API更准确但需要密钥"
        )
    
    with col2:
        if translation_engine == "腾讯翻译API":
            st.info("⚠️ 腾讯翻译API需要配置密钥，请在下方输入")
        else:
            st.success("✅ Google翻译无需配置，可直接使用")
    
    # 腾讯翻译API配置
    if translation_engine == "腾讯翻译API":
        st.markdown("""
        <div class="translation-card">
            <h4 style="color: #2E7D32; margin-bottom: 1rem;">🔑 腾讯翻译API配置</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            secret_id = st.text_input(
                "SecretId",
                type="password",
                help="腾讯云API密钥ID"
            )
        
        with col2:
            secret_key = st.text_input(
                "SecretKey", 
                type="password",
                help="腾讯云API密钥Key"
            )
        
        if not secret_id or not secret_key:
            st.warning("⚠️ 请配置腾讯翻译API的SecretId和SecretKey")
            st.markdown("""
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                <h5 style="color: #856404; margin-bottom: 0.5rem;">📋 如何获取腾讯翻译API密钥？</h5>
                <ol style="color: #856404; font-size: 0.9rem; margin: 0; padding-left: 1.5rem;">
                    <li>登录 <a href="https://console.cloud.tencent.com/" target="_blank">腾讯云控制台</a></li>
                    <li>进入"访问管理" →"访问密钥" →"API密钥管理"</li>
                    <li>创建新的API密钥</li>
                    <li>复制SecretId和SecretKey</li>
                    <li>确保已开通机器翻译服务</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
    else:
        secret_id = None
        secret_key = None
    
    # 翻译参数设置
    st.markdown("""
    <div class="translation-card">
        <h4 style="color: #2E7D32; margin-bottom: 1rem;">⚙️ 翻译参数设置</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        batch_size = st.slider(
            "批次大小",
            min_value=10,
            max_value=100,
            value=50,
            help="每批处理的记录数，较小的值更稳定但较慢"
        )
        
        # 添加翻译质量设置
        translation_quality = st.selectbox(
            "翻译质量设置",
            ["标准模式", "高质量模式", "快速模式"],
            help="高质量模式会进行更多预处理和后处理，但速度较慢"
        )
    
    with col2:
        delay_time = st.slider(
            "延迟时间 (秒)",
            min_value=0.0,
            max_value=2.0,
            value=0.1,
            step=0.1,
            help="每次翻译之间的延迟时间，避免API限制"
        )
        
        # 添加专业术语处理选项
        preserve_terms = st.checkbox(
            "保持专业术语不变",
            value=True,
            help="保持ASIN、USB-C等技术术语的原始形式"
        )
    
    # 翻译按钮
    if st.button("🌐 开始翻译", type="primary", use_container_width=True):
        if not selected_columns:
            st.error("请选择要翻译的列")
            return
        
        # 创建进度条和状态文本
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 开始翻译
            with st.spinner('正在初始化翻译引擎...'):
                time.sleep(1)
            
            # 翻译数据
            engine_name = 'google' if translation_engine == "Google翻译" else 'tencent'
            df_translated, translated_count, error_count, cached_count = translate_dataframe(
                df, selected_columns, progress_bar, status_text, engine=engine_name, secret_id=secret_id, secret_key=secret_key, filters=filters
            )
            
            # 更新session state
            st.session_state.translated_df = df_translated
            
            # 显示翻译结果
            progress_bar.empty()
            status_text.empty()
            
            st.markdown("""
            <div class="success-box">
                <h4 style="margin: 0; color: white;">✅ 翻译完成！</h4>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">所有选中的列已成功翻译为中文</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 显示翻译统计
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("✅ 成功翻译", f"{translated_count:,}")
            with col2:
                st.metric("❌ 翻译失败", f"{error_count:,}")
            with col3:
                st.metric("💾 缓存命中", f"{cached_count:,}")
            with col4:
                total_processed = translated_count + error_count + cached_count
                success_rate = (translated_count / total_processed * 100) if total_processed > 0 else 0
                st.metric("📊 成功率", f"{success_rate:.1f}%")
            
            # 显示翻译后的数据预览
            with st.expander("📋 查看翻译结果预览", expanded=True):
                # 选择要显示的列
                display_columns = []
                for col in selected_columns:
                    display_columns.extend([col, f"{col}_中文"])
                
                # 添加其他重要列
                important_cols = ['ID', 'Asin', 'Brand', 'Rating', 'Review Type']
                for col in important_cols:
                    if col in df_translated.columns and col not in display_columns:
                        display_columns.append(col)
                
                # 重新排序列
                final_columns = []
                for col in df_translated.columns:
                    if col in display_columns:
                        final_columns.append(col)
                
                preview_df = df_translated[final_columns].head(10)
                st.dataframe(preview_df, use_container_width=True)
            
        except Exception as e:
            st.error(f"翻译过程中出错: {str(e)}")
            progress_bar.empty()
            status_text.empty()
    
    # 如果已有翻译结果，显示下载选项
    if 'translated_df' in st.session_state and st.session_state.translated_df is not None:
        st.markdown("""
        <div class="translation-card">
            <h3 style="color: #2E7D32; margin-bottom: 1rem;">📥 下载翻译结果</h3>
        </div>
        """, unsafe_allow_html=True)
        
        df_translated = st.session_state.translated_df
        
        col1, col2 = st.columns(2)
        
        with col1:
            file_format = st.radio(
                "选择下载格式",
                ["Excel", "TXT"],
                help="选择适合的文件格式"
            )
        
        with col2:
            include_original = st.checkbox(
                "包含原始英文列",
                value=True,
                help="是否在下载文件中包含原始英文列"
            )
        
        # 准备下载数据
        if include_original:
            download_df = df_translated
        else:
            # 只保留中文列和其他非翻译列
            chinese_columns = [col for col in df_translated.columns if col.endswith('_中文')]
            other_columns = [col for col in df_translated.columns if not col.endswith('_中文') and col not in selected_columns]
            download_df = df_translated[other_columns + chinese_columns]
        
        # 下载按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if file_format == "Excel":
                file_data = get_download_data(download_df, 'excel')
                st.download_button(
                    label="📥 下载翻译结果 (Excel)",
                    data=file_data,
                    file_name=f"translated_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
            else:
                file_data = get_download_data(download_df, 'txt')
                st.download_button(
                    label="📥 下载翻译结果 (TXT)",
                    data=file_data,
                    file_name=f"translated_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    type="primary",
                    use_container_width=True
                )
        
        # 清除翻译结果按钮
        if st.button("🗑️ 清除翻译结果", use_container_width=True):
            if 'translated_df' in st.session_state:
                del st.session_state.translated_df
            st.rerun()

if __name__ == "__main__":
    main() 