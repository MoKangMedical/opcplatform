"""评估系统模块 — 创建测验、评分、生成报告"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Question:
    """测验题目"""

    id: str
    question: str
    options: list[str]
    correct_answer: int  # 正确答案的索引 (0-based)
    explanation: str = ""
    points: int = 10


@dataclass
class Quiz:
    """测验"""

    id: str
    course_id: str
    title: str
    description: str
    questions: list[Question] = field(default_factory=list)
    passing_score: float = 60.0
    time_limit_minutes: int = 30

    @property
    def total_points(self) -> int:
        return sum(q.points for q in self.questions)


@dataclass
class QuizAttempt:
    """测验尝试"""

    id: str
    quiz_id: str
    user_id: str
    answers: dict[str, int] = field(default_factory=dict)  # question_id -> answer_index
    score: float = 0.0
    passed: bool = False
    started_at: str = ""
    completed_at: str = ""
    time_spent_seconds: int = 0


# 预置测验数据
SAMPLE_QUIZZES = {
    "q001": {
        "id": "q001",
        "course_id": "c001",
        "title": "一人公司基础测验",
        "description": "测试你对一人公司基础知识的掌握程度",
        "passing_score": 60.0,
        "questions": [
            {
                "id": "q001_1",
                "question": "一人公司最核心的优势是什么？",
                "options": ["团队规模大", "决策灵活、成本可控", "融资能力强", "品牌知名度高"],
                "correct_answer": 1,
                "explanation": "一人公司由一人独立运营，决策链条短，运营成本可控。",
                "points": 10,
            },
            {
                "id": "q001_2",
                "question": "以下哪个不属于常见的一人公司商业模式？",
                "options": ["自由职业", "SaaS产品", "传统制造业", "内容创作"],
                "correct_answer": 2,
                "explanation": "传统制造业通常需要较大规模的团队和资本投入。",
                "points": 10,
            },
            {
                "id": "q001_3",
                "question": "一人公司注册时最重要的步骤是？",
                "options": ["选择公司名称", "税务登记", "商业计划书", "融资路演"],
                "correct_answer": 1,
                "explanation": "税务登记是公司合法经营的基础，也是合规运营的关键。",
                "points": 10,
            },
            {
                "id": "q001_4",
                "question": "一人公司财务管理的核心原则是？",
                "options": ["尽量少记账", "公私分明", "只关注收入", "忽略税务"],
                "correct_answer": 1,
                "explanation": "公私分明是一人公司财务管理的核心，避免税务风险。",
                "points": 10,
            },
            {
                "id": "q001_5",
                "question": "以下哪个适合一人公司的收入模式？",
                "options": ["一次性项目收入", "订阅制收入", "以上都适合", "仅销售产品"],
                "correct_answer": 2,
                "explanation": "一人公司可以根据自身情况选择多种收入模式。",
                "points": 10,
            },
        ],
    },
    "q002": {
        "id": "q002",
        "course_id": "c002",
        "title": "产品思维测验",
        "description": "测试你对MVP和产品设计的理解",
        "passing_score": 60.0,
        "questions": [
            {
                "id": "q002_1",
                "question": "MVP的核心理念是什么？",
                "options": ["做最完美的产品", "用最小成本验证假设", "功能越多越好", "只做技术原型"],
                "correct_answer": 1,
                "explanation": "MVP是用最小可行产品验证市场需求的假设。",
                "points": 10,
            },
            {
                "id": "q002_2",
                "question": "需求验证的最佳方式是？",
                "options": ["闭门造车", "用户访谈和问卷", "看竞品做啥", "听朋友建议"],
                "correct_answer": 1,
                "explanation": "直接与目标用户沟通是验证需求最有效的方式。",
                "points": 10,
            },
            {
                "id": "q002_3",
                "question": "产品迭代的关键依据是？",
                "options": ["个人喜好", "用户反馈和数据", "投资人意见", "竞品功能"],
                "correct_answer": 1,
                "explanation": "用户反馈和数据是产品迭代最可靠的依据。",
                "points": 10,
            },
        ],
    },
}


class AssessmentEngine:
    """评估引擎"""

    def __init__(self):
        self._quizzes: dict[str, Quiz] = {}
        self._attempts: list[QuizAttempt] = []
        self._load_sample_quizzes()

    def _load_sample_quizzes(self):
        """加载示例测验"""
        for qid, qdata in SAMPLE_QUIZZES.items():
            questions = [Question(**q) for q in qdata["questions"]]
            self._quizzes[qid] = Quiz(
                id=qdata["id"],
                course_id=qdata["course_id"],
                title=qdata["title"],
                description=qdata["description"],
                passing_score=qdata["passing_score"],
                questions=questions,
            )

    def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """获取测验"""
        return self._quizzes.get(quiz_id)

    def get_quizzes_by_course(self, course_id: str) -> list[Quiz]:
        """获取课程的所有测验"""
        return [q for q in self._quizzes.values() if q.course_id == course_id]

    def create_quiz(self, course_id: str, title: str, description: str, questions: list[dict]) -> Quiz:
        """创建新测验"""
        quiz_id = f"q{uuid.uuid4().hex[:6]}"
        quiz_questions = [Question(**q) for q in questions]
        quiz = Quiz(
            id=quiz_id,
            course_id=course_id,
            title=title,
            description=description,
            questions=quiz_questions,
        )
        self._quizzes[quiz_id] = quiz
        return quiz

    def start_attempt(self, quiz_id: str, user_id: str) -> Optional[QuizAttempt]:
        """开始一次测验尝试"""
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            return None

        attempt = QuizAttempt(
            id=f"a{uuid.uuid4().hex[:6]}",
            quiz_id=quiz_id,
            user_id=user_id,
            started_at=datetime.now().isoformat(),
        )
        self._attempts.append(attempt)
        return attempt

    def submit_answer(self, attempt_id: str, question_id: str, answer_index: int) -> bool:
        """提交答案"""
        for attempt in self._attempts:
            if attempt.id == attempt_id:
                attempt.answers[question_id] = answer_index
                return True
        return False

    def grade_attempt(self, attempt_id: str) -> Optional[dict]:
        """评分"""
        attempt = None
        for a in self._attempts:
            if a.id == attempt_id:
                attempt = a
                break
        if not attempt:
            return None

        quiz = self.get_quiz(attempt.quiz_id)
        if not quiz:
            return None

        total_points = 0
        earned_points = 0
        results = []

        for question in quiz.questions:
            total_points += question.points
            user_answer = attempt.answers.get(question.id)
            is_correct = user_answer == question.correct_answer
            if is_correct:
                earned_points += question.points

            results.append(
                {
                    "question_id": question.id,
                    "question": question.question,
                    "user_answer": user_answer,
                    "correct_answer": question.correct_answer,
                    "is_correct": is_correct,
                    "explanation": question.explanation,
                    "points": question.points if is_correct else 0,
                }
            )

        score = round(earned_points / total_points * 100, 1) if total_points else 0
        attempt.score = score
        attempt.passed = score >= quiz.passing_score
        attempt.completed_at = datetime.now().isoformat()

        return {
            "attempt_id": attempt.id,
            "quiz_title": quiz.title,
            "score": score,
            "passed": attempt.passed,
            "passing_score": quiz.passing_score,
            "earned_points": earned_points,
            "total_points": total_points,
            "results": results,
        }

    def get_user_attempts(self, user_id: str, quiz_id: Optional[str] = None) -> list[QuizAttempt]:
        """获取用户的测验记录"""
        attempts = [a for a in self._attempts if a.user_id == user_id]
        if quiz_id:
            attempts = [a for a in attempts if a.quiz_id == quiz_id]
        return attempts

    def generate_report(self, user_id: str) -> dict:
        """生成用户评估报告"""
        user_attempts = self.get_user_attempts(user_id)
        if not user_attempts:
            return {"user_id": user_id, "message": "暂无测验记录", "quizzes_taken": 0}

        total_score = sum(a.score for a in user_attempts)
        avg_score = round(total_score / len(user_attempts), 1)
        passed_count = sum(1 for a in user_attempts if a.passed)

        return {
            "user_id": user_id,
            "quizzes_taken": len(user_attempts),
            "average_score": avg_score,
            "passed": passed_count,
            "failed": len(user_attempts) - passed_count,
            "pass_rate": round(passed_count / len(user_attempts) * 100, 1),
            "attempts": [
                {
                    "quiz_id": a.quiz_id,
                    "score": a.score,
                    "passed": a.passed,
                    "completed_at": a.completed_at,
                }
                for a in user_attempts
            ],
        }
