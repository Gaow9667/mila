import streamlit as st
from openai import OpenAI
import os

# 页面配置
st.set_page_config(
    page_title="智教·极速教学反思生成器",
    page_icon="🎓",
    layout="centered"
)

# 侧边栏配置
with st.sidebar:
    st.header("⚙️ 设置")
    
    # 优先尝试从 Secrets 或环境变量获取 Key
    try:
        default_key = st.secrets["DEEPSEEK_API_KEY"]
    except:
        default_key = os.getenv("DEEPSEEK_API_KEY", "")

    # 如果有内置 Key，这就隐藏输入框（或者显示为已配置）
    if default_key:
        st.success("✅ 已激活授权许可")
        api_key = default_key
    else:
        api_key = st.text_input("请输入 API Key", type="password", help="推荐使用 DeepSeek 或兼容 OpenAI 格式的 Key")
    
    base_url = st.text_input("Base URL", value="https://api.deepseek.com", help="例如: https://api.deepseek.com")
    model_name = st.text_input("模型名称", value="deepseek-chat", help="例如: deepseek-chat, deepseek-reasoner")
    
    st.markdown("---")
    st.markdown("### 关于")
    st.markdown("专为公立学校教师打造的**教学反思辅助工具**。")
    st.markdown("拒绝形式主义，让 AI 帮你写公文。")

# 主标题
st.title("🎓 智教 · 极速教学反思生成器")
st.markdown("#### 10秒生成符合教务检查标准的专业反思")

# --- 输入区域 ---
st.divider()

col1, col2 = st.columns(2)

with col1:
    grade_subject = st.text_input("年级/科目", placeholder="例如：八年级语文")
    lesson_type = st.selectbox("课时类型", ["新授课", "复习课", "试卷讲评课", "公开课", "实验课"])

with col2:
    lesson_topic = st.text_input("课题名称", placeholder="例如：《背影》")
    style = st.selectbox("生成风格", ["应付检查版 (中规中矩)", "公开课评比版 (理论深厚)", "深刻自我剖析版 (诚恳谦卑)"])

st.markdown("### 1. 教学亮点 (多选)")
highlights = st.multiselect(
    "本节课哪些地方做得好？",
    [
        "课堂气氛活跃，学生参与度高",
        "多媒体课件运用得当，直观形象",
        "重难点突破巧妙，学生易于理解",
        "师生互动频繁，体现学生主体地位",
        "小组合作学习组织有序",
        "板书设计条理清晰，重点突出",
        "德育渗透自然，达到育人效果",
        "教学环节过渡自然，逻辑严密"
    ]
)

st.markdown("### 2. 存在不足 (多选)")
shortcomings = st.multiselect(
    "本节课有哪些遗憾？",
    [
        "时间把控稍显局促，练习时间不足",
        "个别后进生关注不够",
        "小组讨论流于形式，深度不够",
        "提问覆盖面不够广",
        "板书设计略显凌乱",
        "教学评价语言较为单一",
        "对学生生成的突发问题处理不够机智",
        "信息技术与学科融合度有待提高"
    ]
)

st.markdown("### 3. 改进措施 (多选/自定义)")
improvements = st.multiselect(
    "下节课打算怎么改？",
    [
        "优化时间分配，精讲多练",
        "加强课堂巡视，关注不同层次学生",
        "精心设计探究问题，引导深度思考",
        "丰富评价语，多鼓励学生",
        "加强板书设计的规范性",
        "预设更多教学情境，提高应变能力"
    ]
)
custom_improvement = st.text_input("补充其他改进措施（可选）")

# --- 处理逻辑 ---
def generate_reflection():
    if not api_key:
        st.error("请先在左侧设置 API Key")
        return

    if not grade_subject or not lesson_topic:
        st.warning("请填写完整的课程信息（年级科目、课题）")
        return

    # 构造 Prompt
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    # 组合改进措施
    final_improvements = improvements.copy()
    if custom_improvement:
        final_improvements.append(custom_improvement)
    
    system_prompt = f"""
# Role
你是一名拥有20年教龄的公立中学资深教师，擅长撰写深刻、专业、符合教育局规范的“教学反思”。

# Task
根据用户提供的课程信息和教学片段反馈，撰写一篇逻辑通顺、用词考究的教学反思短文。

# Style
- 风格偏向：{style}
- 语气诚恳，态度严谨。
- 多使用教育学专业术语（如：核心素养、支架式教学、最近发展区、教学评一致性、深度学习等）。
- 避免过于口语化，必须是标准的“书面汇报”风格。

# Rules
1. **第一段 (教学目标与导入)**：简述基于《{lesson_topic}》的教学目标达成情况，简要提及教学设计思路。
2. **第二段 (亮点剖析)**：基于用户提供的【亮点】，深入展开。不要仅仅罗列关键词，要结合“体现了学生主体地位”、“激发了探究兴趣”等理论进行升华。
3. **第三段 (不足反思)**：基于用户提供的【不足】，诚恳剖析原因（如：预设不足、对学情把握不准等），语言要客观中肯。
4. **第四段 (改进措施)**：基于【改进措施】，提出具体的行动计划，展望下一节课。
5. 字数控制在 400-600 字之间。
6. 不要输出 Markdown 标题（如 ### 第一段），直接输出正文段落。

# Input Data
- 课程：{grade_subject} - {lesson_topic} ({lesson_type})
- 亮点：{', '.join(highlights)}
- 不足：{', '.join(shortcomings)}
- 改进：{', '.join(final_improvements)}
"""

    user_prompt = "请生成教学反思。"

    try:
        with st.spinner("AI 正在奋笔疾书，请稍候..."):
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                stream=True
            )
            
            # 流式输出
            result_container = st.empty()
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    result_container.markdown(full_response)
            
            st.session_state['generated_reflection'] = full_response
            
    except Exception as e:
        st.error(f"生成失败: {str(e)}")

# --- 按钮与输出 ---
st.divider()
if st.button("✨ 一键生成教学反思", type="primary", use_container_width=True):
    generate_reflection()

# 结果展示区 (如果有历史生成)
if 'generated_reflection' in st.session_state:
    st.markdown("### 📝 生成结果")
    st.text_area("您可以直接复制下方内容：", value=st.session_state['generated_reflection'], height=400)
    
    # 模拟复制功能的提示（Streamlit 限制，很难直接操作剪贴板，text_area 自带复制方便）
    st.caption("提示：点击右上角的复制图标即可复制全部内容。")

