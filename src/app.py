"""OPC Platform — Streamlit 原型应用（5页）"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.course_manager import CourseManager
from src.learning_path import LearningPathEngine, LEARNING_PATHS
from src.assessment import AssessmentEngine
from src.certificate import CertificateManager

# 初始化模块
@st.cache_resource
def init_modules():
    cm = CourseManager()
    lp = LearningPathEngine(cm)
    ae = AssessmentEngine()
    cert = CertificateManager()
    return cm, lp, ae, cert

cm, lp_engine, assessment_engine, cert_manager = init_modules()

# 页面配置
st.set_page_config(
    page_title="OPC Platform — 一人公司全链路学习平台",
    page_icon="🚀",
    layout="wide",
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1E3A5F 0%, #2C5F8A 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .course-card {
        border: 1px solid #e0e0e0;
        border-radius: 0.8rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: box-shadow 0.3s;
    }
    .course-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .badge-beginner { background: #E8F5E9; color: #2E7D32; }
    .badge-intermediate { background: #FFF3E0; color: #EF6C00; }
    .badge-advanced { background: #FFEBEE; color: #C62828; }
</style>
""", unsafe_allow_html=True)

# 侧边栏导航
st.sidebar.title("🚀 OPC Platform")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "导航",
    ["🏠 首页", "📚 课程中心", "🗺️ 学习路径", "📝 在线评估", "👤 个人中心"],
)
st.sidebar.markdown("---")
st.sidebar.markdown("**一人公司全链路学习平台**")
st.sidebar.markdown("帮助你从0到1建立一人公司")


# ==================== 首页 ====================
if page == "🏠 首页":
    st.markdown('<div class="main-header">🚀 OPC Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">一人公司全链路学习平台 — 从想法到盈利的完整学习路径</div>', unsafe_allow_html=True)

    # 统计数据
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 课程总数", "6门")
    with col2:
        st.metric("📖 学习模块", "24个")
    with col3:
        st.metric("👨‍🏫 专家团队", "8位")
    with col4:
        st.metric("🗺️ 学习路径", "4条")

    st.markdown("---")

    # 平台特色
    st.markdown("### ✨ 平台特色")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🎯 系统化学习**\n\n从基础到进阶，覆盖一人公司全生命周期")
    with col2:
        st.markdown("**👨‍🏫 专家指导**\n\n8位实战专家，分享真实创业经验")
    with col3:
        st.markdown("**📜 证书认证**\n\n完成课程获得认证，证明你的能力")

    st.markdown("---")

    # 课程列表
    st.markdown("### 📚 热门课程")
    courses = cm.get_all_courses()
    for i in range(0, len(courses), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(courses):
                course = courses[i + j]
                with col:
                    difficulty_class = {
                        "入门": "badge-beginner",
                        "中级": "badge-intermediate",
                        "高级": "badge-advanced",
                    }.get(course["difficulty"], "")
                    st.markdown(f"""
                    <div class="course-card">
                        <h4>{course['name']}</h4>
                        <p>{course['description'][:80]}...</p>
                        <span class="badge {difficulty_class}">{course['difficulty']}</span>
                        <span style="margin-left: 1rem; color: #666;">⏱️ {course['duration']}</span>
                        <span style="margin-left: 1rem; color: #666;">📖 {course['module_count']}个模块</span>
                    </div>
                    """, unsafe_allow_html=True)


# ==================== 课程中心 ====================
elif page == "📚 课程中心":
    st.markdown("## 📚 课程中心")

    # 筛选
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox("按分类筛选", ["全部"] + cm.get_categories())
    with col2:
        difficulty_filter = st.selectbox("按难度筛选", ["全部"] + cm.get_difficulty_levels())

    # 搜索
    search_keyword = st.text_input("🔍 搜索课程", placeholder="输入关键词搜索...")

    # 获取课程
    if search_keyword:
        courses = cm.search_courses(search_keyword)
    elif category_filter != "全部":
        courses = cm.get_courses_by_category(category_filter)
    elif difficulty_filter != "全部":
        courses = cm.get_courses_by_difficulty(difficulty_filter)
    else:
        courses = cm.get_all_courses()

    # 课程详情选择
    if courses:
        course_names = [c["name"] if isinstance(c, dict) and "name" in c else c.get("name", "") for c in courses]
        selected_course_name = st.selectbox("选择课程查看详情", course_names)

        # 找到选中的课程
        selected_course = None
        for c in courses:
            name = c["name"] if isinstance(c, dict) and "name" in c else c.get("name", "")
            if name == selected_course_name:
                selected_course = c
                break

        if selected_course:
            # 获取完整课程数据
            full_course = cm.get_course_by_id(selected_course["id"])
            if full_course:
                st.markdown(f"### {full_course['name']}")
                st.markdown(f"**描述：** {full_course.get('description', '')}")
                st.markdown(f"**时长：** {full_course['duration']} | **难度：** {full_course['difficulty']} | **分类：** {full_course['category']}")

                # 标签
                tags_html = " ".join([f'<span class="badge" style="background:#E3F2FD;color:#1565C0;margin-right:0.5rem;">{tag}</span>' for tag in full_course.get("tags", [])])
                st.markdown(f"**标签：** {tags_html}", unsafe_allow_html=True)

                st.markdown("---")
                st.markdown("### 📖 课程模块")

                for module in full_course["modules"]:
                    with st.expander(f"📄 {module['title']} — {module['duration']}"):
                        st.markdown(module["content"])

                # 显示课程评分
                st.markdown("---")
                st.markdown("### 📊 课程评估")
                st.info("完成课程学习后，可以在「在线评估」页面进行测验。")
    else:
        st.warning("未找到匹配的课程")


# ==================== 学习路径 ====================
elif page == "🗺️ 学习路径":
    st.markdown("## 🗺️ 学习路径")

    st.markdown("选择适合你的学习路径，系统化提升一人公司技能。")

    # 显示所有学习路径
    for path_id, path in LEARNING_PATHS.items():
        with st.expander(f"📍 {path['name']} — {path['duration']}"):
            st.markdown(f"**描述：** {path['description']}")
            st.markdown(f"**适合人群：** {path['target']}")

            st.markdown("**课程列表：**")
            for i, course_id in enumerate(path["courses"], 1):
                course = cm.get_course_by_id(course_id)
                if course:
                    st.markdown(f"{i}. {course['name']} ({course['difficulty']}) — {course['duration']}")

    st.markdown("---")

    # 个性化推荐
    st.markdown("### 🎯 个性化推荐")
    st.markdown("告诉我们你的背景，我们为你推荐最适合的学习路径。")

    col1, col2 = st.columns(2)
    with col1:
        background = st.selectbox(
            "你的背景",
            ["创业者", "自由职业者", "技术人员", "营销人员", "职场新人", "其他"],
        )
    with col2:
        experience = st.selectbox(
            "你的经验水平",
            ["零基础", "有一些了解", "有一定经验", "经验丰富"],
        )

    if st.button("获取推荐"):
        experience_map = {
            "零基础": "beginner",
            "有一些了解": "beginner",
            "有一定经验": "intermediate",
            "经验丰富": "advanced",
        }

        # 创建临时用户获取推荐
        temp_user = lp_engine.create_user_profile(
            user_id="temp_user",
            name="临时用户",
            background=background,
            experience_level=experience_map.get(experience, "beginner"),
        )

        recommended = lp_engine.recommend_path("temp_user")
        if recommended:
            st.success(f"🎉 推荐学习路径：**{recommended['name']}**")
            st.markdown(f"**描述：** {recommended['description']}")
            st.markdown(f"**预计时长：** {recommended['duration']}")

            st.markdown("**推荐课程顺序：**")
            for i, cid in enumerate(recommended["courses"], 1):
                c = cm.get_course_by_id(cid)
                if c:
                    st.markdown(f"{i}. {c['name']}")
        else:
            st.info("请尝试选择不同的背景信息。")


# ==================== 在线评估 ====================
elif page == "📝 在线评估":
    st.markdown("## 📝 在线评估")

    # 获取所有测验
    all_quizzes = list(assessment_engine._quizzes.values())

    if not all_quizzes:
        st.info("暂无可用测验")
    else:
        quiz_options = {q.title: q.id for q in all_quizzes}
        selected_quiz_title = st.selectbox("选择测验", list(quiz_options.keys()))

        if selected_quiz_title:
            quiz_id = quiz_options[selected_quiz_title]
            quiz = assessment_engine.get_quiz(quiz_id)

            if quiz:
                st.markdown(f"### {quiz.title}")
                st.markdown(f"**描述：** {quiz.description}")
                st.markdown(f"**题目数：** {len(quiz.questions)} | **及格线：** {quiz.passing_score}% | **时间限制：** {quiz.time_limit_minutes}分钟")

                st.markdown("---")

                # 用户答题
                user_id = st.text_input("输入你的用户ID", value="user_001")

                if st.button("开始测验"):
                    st.session_state.quiz_started = True
                    st.session_state.quiz_id = quiz_id
                    st.session_state.user_id = user_id
                    st.session_state.answers = {}

                if st.session_state.get("quiz_started") and st.session_state.get("quiz_id") == quiz_id:
                    st.markdown("### 答题区")
                    for i, q in enumerate(quiz.questions, 1):
                        st.markdown(f"**第{i}题：** {q.question}")
                        answer = st.radio(
                            f"选择答案",
                            q.options,
                            key=f"q_{q.id}",
                            label_visibility="collapsed",
                        )
                        st.session_state.answers[q.id] = q.options.index(answer)
                        st.markdown("---")

                    if st.button("提交答案"):
                        # 创建测验尝试
                        attempt = assessment_engine.start_attempt(quiz_id, user_id)
                        if attempt:
                            # 提交所有答案
                            for qid, ans_idx in st.session_state.answers.items():
                                assessment_engine.submit_answer(attempt.id, qid, ans_idx)

                            # 评分
                            result = assessment_engine.grade_attempt(attempt.id)
                            if result:
                                st.markdown("### 📊 测验结果")

                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("得分", f"{result['score']}%")
                                with col2:
                                    st.metric("状态", "✅ 通过" if result["passed"] else "❌ 未通过")
                                with col3:
                                    st.metric("得分", f"{result['earned_points']}/{result['total_points']}")

                                st.markdown("---")
                                st.markdown("### 📝 详细解析")
                                for r in result["results"]:
                                    status = "✅" if r["is_correct"] else "❌"
                                    st.markdown(f"{status} **{r['question']}**")
                                    if not r["is_correct"]:
                                        st.markdown(f"   - 你的答案：{quiz.questions[0].options[r['user_answer']] if r['user_answer'] is not None else '未作答'}")
                                        st.markdown(f"   - 正确答案：{quiz.questions[0].options[r['correct_answer']]}")
                                    st.markdown(f"   - 解析：{r['explanation']}")
                                    st.markdown("---")

                                # 重置状态
                                st.session_state.quiz_started = False


# ==================== 个人中心 ====================
elif page == "👤 个人中心":
    st.markdown("## 👤 个人中心")

    user_id = st.text_input("用户ID", value="user_001")
    user_name = st.text_input("姓名", value="学员")

    tab1, tab2, tab3 = st.tabs(["📊 学习进度", "📜 我的证书", "📈 技能评估"])

    with tab1:
        st.markdown("### 📊 学习进度")

        # 创建/获取用户
        profile = lp_engine.get_user_profile(user_id)
        if not profile:
            profile = lp_engine.create_user_profile(user_id=user_id, name=user_name)

        # 模拟一些已完成的课程
        if st.button("模拟完成第一门课程"):
            lp_engine.mark_course_completed(user_id, "c001")
            st.success("已标记课程 c001 为完成")

        # 显示各路径进度
        st.markdown("**各学习路径进度：**")
        for path_id, path in LEARNING_PATHS.items():
            progress = lp_engine.calculate_progress(user_id, path_id)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{path['name']}**")
                st.progress(progress["progress"] / 100)
            with col2:
                st.markdown(f"{progress['completed']}/{progress['total']}")

    with tab2:
        st.markdown("### 📜 我的证书")

        # 生成示例证书
        if st.button("生成示例证书"):
            cert = cert_manager.generate_course_certificate(
                user_id=user_id,
                user_name=user_name,
                course_id="c001",
                course_name="一人公司基础：从0到1搭建",
                score=85.0,
            )
            if cert:
                st.success(f"证书已生成！证书编号：{cert.id}")

        # 显示用户证书
        user_certs = cert_manager.get_user_certificates(user_id)
        if user_certs:
            for cert in user_certs:
                with st.expander(f"📜 {cert.id} — {cert.course_name or cert.path_name}"):
                    st.markdown(f"**证书编号：** {cert.id}")
                    st.markdown(f"**课程：** {cert.course_name or 'N/A'}")
                    st.markdown(f"**得分：** {cert.score}%")
                    st.markdown(f"**颁发时间：** {cert.issued_at}")
                    st.markdown(f"**状态：** {cert.status}")

                    # 验证按钮
                    if st.button(f"验证证书 {cert.id}"):
                        result = cert_manager.verify_certificate(cert.id)
                        if result["valid"]:
                            st.success(result["message"])
                        else:
                            st.error(result["message"])
        else:
            st.info("暂无证书，完成课程后可获得证书。")

    with tab3:
        st.markdown("### 📈 技能评估")

        # 获取技能评估
        skills = lp_engine.assess_skills(user_id)

        if skills:
            # 雷达图
            categories = list(skills.keys())
            values = list(skills.values())

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name="技能水平",
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                title="技能雷达图",
            )
            st.plotly_chart(fig, use_container_width=True)

            # 技能详情
            st.markdown("**技能详情：**")
            for skill, score in skills.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{skill}**")
                    st.progress(score / 100)
                with col2:
                    st.markdown(f"{score}%")
        else:
            st.info("完成课程学习后，系统将自动评估你的技能水平。")

        # 评估报告
        st.markdown("---")
        st.markdown("### 📋 评估报告")
        report = assessment_engine.generate_report(user_id)
        if report.get("quizzes_taken", 0) > 0:
            st.markdown(f"**测验次数：** {report['quizzes_taken']}")
            st.markdown(f"**平均分：** {report['average_score']}%")
            st.markdown(f"**通过率：** {report['pass_rate']}%")
        else:
            st.info("暂无测验记录，去「在线评估」页面参加测验吧！")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
    "OPC Platform v0.1.0 — 一人公司全链路学习平台 | "
    "Built with ❤️ by MoKangMedical"
    "</div>",
    unsafe_allow_html=True,
)
