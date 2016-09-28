from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for


class AuthorizedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("frontend.login"))


class UserModelView(AuthorizedModelView):
    can_create = False
    can_edit = False
    can_delete = True
    column_exclude_list = ["password"]


class ReportModelView(AuthorizedModelView):
    can_create = False
    can_edit = False
    can_delete = True


class AuthenticatedIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('frontend.login'))
        return super(AuthenticatedIndexView, self).index()
