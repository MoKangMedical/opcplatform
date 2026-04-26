"""课程管理模块 — 加载、查询、管理课程数据"""

import json
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data"


class CourseManager:
    """课程管理器"""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self._courses: list[dict] = []
        self._load_courses()

    def _load_courses(self) -> None:
        """加载课程数据"""
        courses_file = self.data_dir / "courses.json"
        if courses_file.exists():
            with open(courses_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._courses = data.get("courses", [])

    def get_all_courses(self) -> list[dict]:
        """获取所有课程列表"""
        return [
            {
                "id": c["id"],
                "name": c["name"],
                "description": c.get("description", ""),
                "duration": c["duration"],
                "difficulty": c["difficulty"],
                "category": c["category"],
                "tags": c["tags"],
                "module_count": len(c["modules"]),
            }
            for c in self._courses
        ]

    def get_course_by_id(self, course_id: str) -> Optional[dict]:
        """根据ID获取课程详情"""
        for course in self._courses:
            if course["id"] == course_id:
                return course
        return None

    def get_courses_by_category(self, category: str) -> list[dict]:
        """根据分类筛选课程"""
        return [c for c in self._courses if c["category"] == category]

    def get_courses_by_difficulty(self, difficulty: str) -> list[dict]:
        """根据难度筛选课程"""
        return [c for c in self._courses if c["difficulty"] == difficulty]

    def get_module(self, course_id: str, module_id: str) -> Optional[dict]:
        """获取指定课程的指定模块"""
        course = self.get_course_by_id(course_id)
        if course:
            for module in course["modules"]:
                if module["id"] == module_id:
                    return module
        return None

    def get_categories(self) -> list[str]:
        """获取所有课程分类"""
        return list(set(c["category"] for c in self._courses))

    def get_difficulty_levels(self) -> list[str]:
        """获取所有难度等级"""
        return list(set(c["difficulty"] for c in self._courses))

    def search_courses(self, keyword: str) -> list[dict]:
        """搜索课程"""
        keyword = keyword.lower()
        results = []
        for c in self._courses:
            if (
                keyword in c["name"].lower()
                or keyword in c.get("description", "").lower()
                or keyword in " ".join(c.get("tags", [])).lower()
            ):
                results.append(c)
        return results

    def get_course_modules(self, course_id: str) -> list[dict]:
        """获取课程的所有模块"""
        course = self.get_course_by_id(course_id)
        if course:
            return course["modules"]
        return []

    def get_total_duration(self, course_id: str) -> str:
        """获取课程总时长"""
        course = self.get_course_by_id(course_id)
        if course:
            return course["duration"]
        return "未知"


# 便捷函数
def load_courses() -> CourseManager:
    """加载并返回课程管理器实例"""
    return CourseManager()
