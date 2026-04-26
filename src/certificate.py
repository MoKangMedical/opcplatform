"""证书生成模块 — 生成完成证书、验证证书"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data"


@dataclass
class Certificate:
    """证书"""

    id: str
    template_id: str
    user_id: str
    user_name: str
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    path_id: Optional[str] = None
    path_name: Optional[str] = None
    score: float = 0.0
    issued_at: str = ""
    expires_at: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    status: str = "active"  # active / revoked / expired


class CertificateManager:
    """证书管理器"""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self._templates: list[dict] = []
        self._certificates: dict[str, Certificate] = {}
        self._load_templates()

    def _load_templates(self):
        """加载证书模板"""
        templates_file = self.data_dir / "certificates.json"
        if templates_file.exists():
            with open(templates_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._templates = data.get("templates", [])

    def get_templates(self) -> list[dict]:
        """获取所有证书模板"""
        return self._templates

    def get_template(self, template_id: str) -> Optional[dict]:
        """获取指定模板"""
        for tpl in self._templates:
            if tpl["id"] == template_id:
                return tpl
        return None

    def generate_certificate(
        self,
        user_id: str,
        user_name: str,
        template_id: str = "tpl001",
        course_id: Optional[str] = None,
        course_name: Optional[str] = None,
        path_id: Optional[str] = None,
        path_name: Optional[str] = None,
        score: float = 0.0,
    ) -> Optional[Certificate]:
        """生成证书"""
        template = self.get_template(template_id)
        if not template:
            return None

        cert_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        certificate = Certificate(
            id=cert_id,
            template_id=template_id,
            user_id=user_id,
            user_name=user_name,
            course_id=course_id,
            course_name=course_name,
            path_id=path_id,
            path_name=path_name,
            score=score,
            issued_at=datetime.now().isoformat(),
            metadata={
                "template_name": template["name"],
                "generated_by": "OPC Platform",
            },
        )
        self._certificates[cert_id] = certificate
        return certificate

    def get_certificate(self, cert_id: str) -> Optional[Certificate]:
        """获取证书"""
        return self._certificates.get(cert_id)

    def verify_certificate(self, cert_id: str) -> dict:
        """验证证书有效性"""
        cert = self._certificates.get(cert_id)
        if not cert:
            return {"valid": False, "message": "证书不存在"}

        if cert.status == "revoked":
            return {"valid": False, "message": "证书已被撤销"}

        if cert.status == "expired":
            return {"valid": False, "message": "证书已过期"}

        return {
            "valid": True,
            "message": "证书有效",
            "certificate": {
                "id": cert.id,
                "user_name": cert.user_name,
                "course_name": cert.course_name,
                "path_name": cert.path_name,
                "score": cert.score,
                "issued_at": cert.issued_at,
                "status": cert.status,
            },
        }

    def revoke_certificate(self, cert_id: str) -> bool:
        """撤销证书"""
        cert = self._certificates.get(cert_id)
        if cert:
            cert.status = "revoked"
            return True
        return False

    def get_user_certificates(self, user_id: str) -> list[Certificate]:
        """获取用户的所有证书"""
        return [c for c in self._certificates.values() if c.user_id == user_id]

    def generate_course_certificate(self, user_id: str, user_name: str, course_id: str, course_name: str, score: float) -> Optional[Certificate]:
        """生成课程完成证书"""
        return self.generate_certificate(
            user_id=user_id,
            user_name=user_name,
            template_id="tpl001",
            course_id=course_id,
            course_name=course_name,
            score=score,
        )

    def generate_path_certificate(self, user_id: str, user_name: str, path_id: str, path_name: str, score: float) -> Optional[Certificate]:
        """生成学习路径完成证书"""
        return self.generate_certificate(
            user_id=user_id,
            user_name=user_name,
            template_id="tpl002",
            path_id=path_id,
            path_name=path_name,
            score=score,
        )

    def export_certificate_data(self, cert_id: str) -> Optional[dict]:
        """导出证书数据"""
        cert = self._certificates.get(cert_id)
        if not cert:
            return None
        return {
            "id": cert.id,
            "template_id": cert.template_id,
            "user_id": cert.user_id,
            "user_name": cert.user_name,
            "course_id": cert.course_id,
            "course_name": cert.course_name,
            "path_id": cert.path_id,
            "path_name": cert.path_name,
            "score": cert.score,
            "issued_at": cert.issued_at,
            "status": cert.status,
            "metadata": cert.metadata,
        }
