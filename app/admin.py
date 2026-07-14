from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.config import settings
from app.database import engine
from app.models import Charm, ExHave, ExWant, Have, Student, Want


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if (
            username == settings.admin_username
            and password == settings.admin_password
        ):
            request.session.update({"admin": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        if request.session.get("admin"):
            return True
        return False


class StudentAdmin(ModelView, model=Student):
    name = "Student"
    name_plural = "Students"
    icon = "fa-solid fa-user-graduate"
    column_list = [
        Student.student_id,
        Student.name,
        Student.gender,
        Student.age,
        Student.mbti,
    ]
    column_searchable_list = [Student.student_id, Student.name, Student.mbti]
    column_sortable_list = [
        Student.student_id,
        Student.name,
        Student.gender,
        Student.age,
        Student.mbti,
    ]
    column_labels = {
        Student.student_id: "학번",
        Student.name: "이름",
        Student.gender: "성별(여=True)",
        Student.age: "나이",
        Student.mbti: "MBTI",
    }


class CharmAdmin(ModelView, model=Charm):
    name = "Charm"
    name_plural = "Charms"
    icon = "fa-solid fa-tags"
    column_list = [Charm.charm_id, Charm.name]
    column_searchable_list = [Charm.name]
    column_sortable_list = [Charm.name]
    column_labels = {
        Charm.charm_id: "ID",
        Charm.name: "매력 이름",
    }


class HaveAdmin(ModelView, model=Have):
    name = "Have"
    name_plural = "Have"
    icon = "fa-solid fa-hand-holding-heart"
    column_list = [Have.student_id, Have.charm_id]
    column_searchable_list = [Have.student_id]
    column_labels = {
        Have.student_id: "학번",
        Have.charm_id: "Charm ID",
    }


class WantAdmin(ModelView, model=Want):
    name = "Want"
    name_plural = "Want"
    icon = "fa-solid fa-heart"
    column_list = [Want.student_id, Want.charm_id]
    column_searchable_list = [Want.student_id]
    column_labels = {
        Want.student_id: "학번",
        Want.charm_id: "Charm ID",
    }


class ExHaveAdmin(ModelView, model=ExHave):
    name = "ExHave"
    name_plural = "ExHave"
    icon = "fa-solid fa-comment"
    column_list = [ExHave.student_id, ExHave.charm]
    column_searchable_list = [ExHave.student_id, ExHave.charm]
    column_labels = {
        ExHave.student_id: "학번",
        ExHave.charm: "추가 어필",
    }


class ExWantAdmin(ModelView, model=ExWant):
    name = "ExWant"
    name_plural = "ExWant"
    icon = "fa-solid fa-comment-dots"
    column_list = [ExWant.student_id, ExWant.charm]
    column_searchable_list = [ExWant.student_id, ExWant.charm]
    column_labels = {
        ExWant.student_id: "학번",
        ExWant.charm: "추가 이상형",
    }


def setup_admin(app) -> Admin:
    admin = Admin(
        app,
        engine,
        title="QRious Admin",
        base_url="/admin",
        authentication_backend=AdminAuth(secret_key=settings.admin_secret_key),
    )
    admin.add_view(StudentAdmin)
    admin.add_view(CharmAdmin)
    admin.add_view(HaveAdmin)
    admin.add_view(WantAdmin)
    admin.add_view(ExHaveAdmin)
    admin.add_view(ExWantAdmin)
    return admin
