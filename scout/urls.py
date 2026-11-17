from django.urls import path
from . import views

urlpatterns = [
    path('',                          views.dashboard,          name='home'),
    path('login/',                    views.login_view,         name='login'),
    path('register/',                 views.register_view,      name='register'),
    path('logout/',                   views.logout_view,        name='logout'),
    path('dashboard/',                views.dashboard,          name='dashboard'),
    path('players/',                  views.players_by_position,name='players'),
    path('compare/',                  views.compare_players,    name='compare'),
    path('player/<int:pk>/',          views.player_profile,     name='player_profile'),
    path('player/<int:pk>/stats/',    views.player_stats_api,   name='player_stats_api'),  # AJAX
    path('recommend/',                views.recommend,          name='recommend'),
    path('shortlist/',                views.shortlist,          name='shortlist'),
    path('shortlist/add/',            views.add_to_shortlist,   name='add_shortlist'),
    path('shortlist/remove/',         views.remove_shortlist,   name='remove_shortlist'),
    path('shortlist/export/',         views.export_shortlist,   name='export_shortlist'),
    path('shortlist/<int:shortlist_id>/review/', views.analyst_review, name='analyst_review'),
    path('approvals/',                views.head_scout_approvals, name='head_scout_approvals'),
    path('workflow/',                 views.workflow_dashboard,  name='workflow_dashboard'),
    path('admin-panel/',              views.admin_panel,        name='admin_panel'),
    path('admin-panel/users/',        views.admin_users,        name='admin_users'),
    path('profile/<int:user_id>/',    views.user_profile,        name='user_profile'),
    path('profile/<int:user_id>/edit/', views.edit_profile,      name='edit_profile'),
    path('admin-panel/audit/',        views.admin_audit,        name='admin_audit'),
    path('admin-panel/logs/',         views.admin_logs,         name='admin_logs'),
    path('admin-panel/toggle-user/<int:user_id>/', views.toggle_user_active, name='toggle_user_active'),
    path('admin-panel/delete-user/<int:user_id>/', views.delete_user_admin, name='delete_user_admin'),
    path('admin-panel/clear-logs/',   views.clear_logs,         name='clear_logs'),
]
