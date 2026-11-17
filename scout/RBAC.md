# Role-Based Access Control (RBAC) System

This document outlines the role-based access control system for the Football Scout platform.

## Overview

The RBAC system enforces role-based permissions at both the view level (backend) and the UI level (frontend). Each user is assigned one of four roles, and access to features is controlled based on that role.

## Roles

### 1. **Scout** (scout)
Entry-level scouting staff responsible for identifying and evaluating players.

**Permissions:**
- View Dashboard (personal stats)
- View Players
- View own Profile / Edit own Profile
- View Shortlist (own shortlist only)
- Add to Shortlist
- Remove from Shortlist
- Export Shortlist (CSV)
- Compare Players
- View Player Stats
- Submit Recommendations

**Pages:**
- `/dashboard/` - Personal dashboard
- `/players/` - Player search and browse
- `/compare/` - Player comparison
- `/shortlist/` - Personal shortlist
- `/recommend/` - AI recommendations for new players
- `/profile/<id>/` - Own profile
- `/profile/<id>/edit/` - Edit own profile
- `/player/<id>/` - Player details and notes

**Cannot Access:**
- Analyst Review
- Head Scout Approvals
- Workflow Dashboard
- Admin Panel

---

### 2. **Analyst** (analyst)
Reviews shortlist entries from assigned scouts and provides detailed analysis.

**Permissions:**
- View Dashboard
- View Players
- View own Profile / Edit own Profile
- View Shortlist (assigned scout's shortlist)
- Compare Players
- View Player Stats
- Analyst Review (review assigned scout's players)

**Pages:**
- `/dashboard/` - Personal dashboard
- `/players/` - Player search and browse
- `/compare/` - Player comparison
- `/shortlist/` - Shortlist of assigned scout
- `/shortlist/<id>/review/` - Detailed analyst review page
- `/profile/<id>/` - Own profile
- `/profile/<id>/edit/` - Edit own profile
- `/player/<id>/` - Player details

**Cannot Access:**
- Recommendations
- Head Scout Approvals
- Workflow Dashboard
- Admin Panel
- Remove Shortlist (view only)

---

### 3. **Head Scout** (head_scout)
Senior scouting staff who approves shortlisted players and manages the workflow.

**Permissions:**
- View Dashboard (all stats)
- View Players
- View own Profile / Edit own Profile
- View Shortlist (all)
- Compare Players
- View Player Stats
- Remove Shortlist entries
- Head Scout Approvals
- Workflow Dashboard

**Pages:**
- `/dashboard/` - Global dashboard with all stats
- `/players/` - Player search and browse
- `/compare/` - Player comparison
- `/shortlist/` - All shortlists
- `/approvals/` - Head Scout approval dashboard
- `/workflow/` - Workflow overview
- `/profile/<id>/` - View any profile
- `/profile/<id>/edit/` - Edit any profile
- `/player/<id>/` - Player details

**Cannot Access:**
- Recommendations
- Analyst Review
- Admin Panel

---

### 4. **Manager** (manager)
System administrator with full access to all features.

**Permissions:** `all` (unrestricted access)

**Pages:**
- All pages accessible
- Admin Panel with:
  - User Management (`/admin-panel/users/`)
  - Activity Audit (`/admin-panel/audit/`)
  - Detailed Logs (`/admin-panel/logs/`)
- Toggle user active/inactive status
- Delete users
- Clear activity logs

---

## Permission Map

| Permission | Scout | Analyst | Head Scout | Manager |
|-----------|-------|---------|------------|---------|
| view_dashboard | ✓ | ✓ | ✓ | ✓ |
| view_players | ✓ | ✓ | ✓ | ✓ |
| view_profile | ✓ | ✓ | ✓ | ✓ |
| edit_profile | ✓ | ✓ | ✓ | ✓ |
| shortlist_view | ✓ | ✓ | ✓ | ✓ |
| shortlist_add | ✓ | ✗ | ✗ | ✓ |
| shortlist_remove | ✓ | ✗ | ✓ | ✓ |
| export_shortlist | ✓ | ✗ | ✗ | ✓ |
| compare_players | ✓ | ✓ | ✓ | ✓ |
| player_stats | ✓ | ✓ | ✓ | ✓ |
| recommend | ✓ | ✗ | ✗ | ✓ |
| analyst_review | ✗ | ✓ | ✗ | ✓ |
| head_scout_approvals | ✗ | ✗ | ✓ | ✓ |
| workflow_dashboard | ✗ | ✗ | ✓ | ✓ |

---

## URL Routes and Access Control

### Public Routes (No Authentication Required)
- `/login/` - Login page
- `/logout/` - Logout (requires authentication)

### Protected Routes with Role Checks

| Route | Method | Required Role(s) | Decorator |
|-------|--------|------------------|-----------|
| `/dashboard/` | GET | All authenticated | `@login_required` |
| `/players/` | GET | All authenticated | `@login_required` |
| `/compare/` | GET | All authenticated | `@role_required('compare_players')` |
| `/player/<id>/` | GET, POST | All authenticated | `@login_required` |
| `/player/<id>/stats/` | GET | All authenticated | `@role_required_json('player_stats')` |
| `/recommend/` | GET | Scout, Manager | `@role_required('recommend')` |
| `/shortlist/` | GET | Scout, Analyst, Head Scout, Manager | `@role_required('shortlist_view')` |
| `/shortlist/add/` | POST | Scout, Manager | `@role_required('shortlist_add')` |
| `/shortlist/remove/` | POST | Scout, Head Scout, Manager | `@role_required('shortlist_remove')` |
| `/shortlist/export/` | GET | Scout, Manager | `@role_required('export_shortlist')` |
| `/shortlist/<id>/review/` | GET, POST | Analyst, Head Scout, Manager | `@role_required('analyst_review')` |
| `/approvals/` | GET, POST | Head Scout, Manager | `@role_required('head_scout_approvals')` |
| `/workflow/` | GET | Head Scout, Manager | `@role_required('workflow_dashboard')` |
| `/profile/<id>/` | GET | All authenticated | `@role_required('view_profile')` |
| `/profile/<id>/edit/` | GET, POST | All authenticated | `@role_required('edit_profile')` |
| `/admin-panel/` | GET | Manager only | `@admin_only` |
| `/admin-panel/users/` | GET, POST | Manager only | `@admin_only` |
| `/admin-panel/audit/` | GET | Manager only | `@admin_only` |
| `/admin-panel/logs/` | GET | Manager only | `@admin_only` |

---

## Navigation Menu Visibility

The main navigation bar dynamically displays links based on the user's role:

### Navigation Items
- **Dashboard** - All authenticated users
- **Profile** - All authenticated users
- **Players** - All authenticated users
- **Compare** - All authenticated users
- **Shortlist** - Scout, Analyst, Head Scout, Manager
- **Recommendations** - Scout only
- **Review** - Analyst only (links to shortlist)
- **Approvals** - Head Scout, Manager
- **Workflow** - Manager only
- **Admin** - Manager only

---

## Implementation Details

### View Decorators

Three main decorators are used:

1. **`@login_required`** - Ensures user is authenticated
2. **`@role_required(permission)`** - Checks if user has required permission
3. **`@admin_only`** - Restricts to superusers only
4. **`@role_required_json(permission)`** - JSON responses for AJAX endpoints

### Permission Checking

Permissions are checked using:
- `has_permission(user, permission)` - Checks if user has permission
- `has_role(user, roles)` - Checks if user has one of the specified roles
- `get_user_role(user)` - Gets the user's role

### Superuser Handling

- Superusers automatically have `manager` role
- Superusers bypass all permission checks
- Superusers have access to all features

---

## Best Practices

1. **Always use decorators** - Apply `@role_required()` to every protected view
2. **Specify exact permissions** - Use specific permission names, not role names
3. **Check in templates** - Use `{% if user.profile.role == 'scout' %}` in templates
4. **Frontend/Backend sync** - Keep template visibility in sync with view permissions
5. **Log access attempts** - The system logs all activity for audit purposes

---

## Troubleshooting

### User Can't Access Page
1. Check that the decorator is applied to the view
2. Verify the user's role in the Profile model
3. Check the ROLE_ACCESS dictionary for the permission
4. Review activity logs for denied access attempts

### Navigation Links Not Showing
1. Verify the base.html template has the correct role check
2. Clear browser cache
3. Check the `user.profile.role` value in Django admin

### Permission Not Defined
1. Add the permission to the ROLE_ACCESS dictionary
2. Add the decorator to the view
3. Update the navigation links in base.html

---

## Adding a New Role or Permission

1. **Create new permission** - Add to `ROLE_ACCESS` dict in views.py
2. **Add decorator** - Apply to the view: `@role_required('new_permission')`
3. **Update template** - Add condition to base.html navigation
4. **Create role** - Add to Profile model ROLE_CHOICES if needed
5. **Test thoroughly** - Verify access for each role

---

## Related Files

- `scout/views.py` - View functions with decorators and permission checks
- `scout/models.py` - Profile model with role field
- `scout/templates/scout/base.html` - Navigation menu with role-based visibility
- `scout/urls.py` - URL routing
