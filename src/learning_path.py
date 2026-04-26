"""学习路径推荐模块 — 根据用户背景推荐学习路径、进度追踪、技能评估"""

from dataclasses import dataclass, field
from typing import Optional

from src.course_manager import CourseManager


@dataclass
class UserProfile:
    """用户画像"""

    user_id: str
    name: str
    background: str = ""  # 背景：创业者、自由职业、转行等
    experience_level: str = "beginner"  # beginner / intermediate / advanced
    interests: list[str] = field(default_factory=list)
    completed_courses: list[str] = field(default_factory=list)
    completed_modules: list[str] = field(default_factory=list)
    skill_scores: dict[str, float] = field(default_factory=dict)


# 预定义学习路径
LEARNING_PATHS = {
    "startup_beginner": {
        "name": "创业新手路径",
        "description": "适合零基础创业者的入门学习路径",
        "target": "想从0开始创业的新手",
        "courses": ["c001", "c002", "c003", "c005", "c004", "c006"],
        "duration": "16小时",
    },
    "freelancer": {
        "name": "自由职业者路径",
        "description": "适合想转型自由职业的人群",
        "target": "有专业技能想独立执业的人",
        "courses": ["c001", "c003", "c004", "c005"],
        "duration": "11小时",
    },
    "tech_founder": {
        "name": "技术创始人路径",
        "description": "适合有技术背景想做SaaS产品的人",
        "target": "程序员/技术人员",
        "courses": ["c002", "c004", "c003", "c006"],
        "duration": "11小时",
    },
    "growth_hacker": {
        "name": "增长黑客路径",
        "description": "专注营销和效率提升的快速路径",
        "target": "已有产品想快速获客的人",
        "courses": ["c003", "c004", "c006"],
        "duration": "8小时",
    },
}


class LearningPathEngine:
    """学习路径推荐引擎"""

    def __init__(self, course_manager: Optional[CourseManager] = None):
        self.course_manager = course_manager or CourseManager()
        self.user_profiles: dict[str, UserProfile] = {}

    def create_user_profile(self, user_id: str, name: str, **kwargs) -> UserProfile:
        """创建用户画像"""
        profile = UserProfile(user_id=user_id, name=name, **kwargs)
        self.user_profiles[user_id] = profile
        return profile

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """获取用户画像"""
        return self.user_profiles.get(user_id)

    def recommend_path(self, user_id: str) -> Optional[dict]:
        """根据用户背景推荐学习路径"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return None

        # 根据背景和经验推荐
        if profile.experience_level == "beginner":
            if "技术" in profile.background or "程序员" in profile.background:
                return LEARNING_PATHS["tech_founder"]
            elif "自由职业" in profile.background or "独立" in profile.background:
                return LEARNING_PATHS["freelancer"]
            else:
                return LEARNING_PATHS["startup_beginner"]
        elif profile.experience_level == "intermediate":
            if "营销" in profile.background or "增长" in profile.background:
                return LEARNING_PATHS["growth_hacker"]
            else:
                return LEARNING_PATHS["freelancer"]
        else:  # advanced
            return LEARNING_PATHS["growth_hacker"]

    def get_all_paths(self) -> dict[str, dict]:
        """获取所有学习路径"""
        return LEARNING_PATHS

    def get_path_courses(self, path_id: str) -> list[dict]:
        """获取学习路径中的课程详情"""
        path = LEARNING_PATHS.get(path_id)
        if not path:
            return []
        courses = []
        for cid in path["courses"]:
            course = self.course_manager.get_course_by_id(cid)
            if course:
                courses.append(course)
        return courses

    def calculate_progress(self, user_id: str, path_id: str) -> dict:
        """计算用户在指定学习路径中的进度"""
        profile = self.get_user_profile(user_id)
        path = LEARNING_PATHS.get(path_id)
        if not profile or not path:
            return {"progress": 0, "completed": 0, "total": 0}

        total_courses = len(path["courses"])
        completed = sum(1 for c in path["courses"] if c in profile.completed_courses)

        return {
            "progress": round(completed / total_courses * 100, 1) if total_courses else 0,
            "completed": completed,
            "total": total_courses,
            "remaining": total_courses - completed,
        }

    def mark_course_completed(self, user_id: str, course_id: str) -> bool:
        """标记课程为已完成"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return False
        if course_id not in profile.completed_courses:
            profile.completed_courses.append(course_id)
        return True

    def mark_module_completed(self, user_id: str, module_id: str) -> bool:
        """标记模块为已完成"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return False
        if module_id not in profile.completed_modules:
            profile.completed_modules.append(module_id)
        return True

    def assess_skills(self, user_id: str) -> dict[str, float]:
        """评估用户技能水平"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return {}

        skills = {}
        for course_id in profile.completed_courses:
            course = self.course_manager.get_course_by_id(course_id)
            if course:
                for tag in course.get("tags", []):
                    skills[tag] = skills.get(tag, 0) + 20  # 每门课+20分

        # 归一化到0-100
        max_score = max(skills.values()) if skills else 1
        return {k: min(round(v / max_score * 100, 1), 100) for k, v in skills.items()}

    def get_next_course(self, user_id: str, path_id: str) -> Optional[dict]:
        """获取用户在学习路径中下一个应该学习的课程"""
        profile = self.get_user_profile(user_id)
        path = LEARNING_PATHS.get(path_id)
        if not profile or not path:
            return None

        for course_id in path["courses"]:
            if course_id not in profile.completed_courses:
                return self.course_manager.get_course_by_id(course_id)
        return None
