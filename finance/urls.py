from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    # user management
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("profile/", views.profile_view, name="profile"),

    # dashboard
    path("", views.dashboard_view, name="dashboard"),

    # incomes
    path("incomes/", views.income_list_view, name="income_list"),
    path("incomes/add/", views.income_form_view, name="income_add"),
    path("incomes/<int:pk>/edit/", views.income_form_view, name="income_edit"),

    # expenses
    path("expenses/", views.expense_list_view, name="expense_list"),
    path("expenses/add/", views.expense_form_view, name="expense_add"),
    path("expenses/<int:pk>/edit/", views.expense_form_view, name="expense_edit"),

    # transactions (รวมรับ–จ่าย)
    path("transactions/", views.transaction_list_view, name="transaction_list"),
]