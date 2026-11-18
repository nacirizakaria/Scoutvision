from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from .models import Shortlist, PlayerNote, Profile, ActivityLog, PlayerApproval

import csv
import json
import math
from types import SimpleNamespace

ROLE_VALUE_MAP = {
    'Scout': 'scout',
    'Analyst': 'analyst',
    'Head Scout': 'head_scout',
    'Director': 'head_scout',
    'Manager': 'manager',
}

VALID_ROLES = set(ROLE_VALUE_MAP.values())
ADVANCED_ROLES = ['scout', 'analyst', 'head_scout', 'manager']

ROLE_ACCESS = {
    'scout': {
        'view_dashboard',
        'view_players',
        'view_profile',
        'edit_profile',
        'shortlist_view',
        'shortlist_add',
        'shortlist_remove',
        'export_shortlist',
        'compare_players',
        'player_stats',
        'recommend',
    },
    'analyst': {
        'view_dashboard',
        'view_players',
        'view_profile',
        'edit_profile',
        'shortlist_view',
        'compare_players',
        'player_stats',
        'analyst_review',
    },
    'head_scout': {
        'view_dashboard',
        'view_players',
        'view_profile',
        'edit_profile',
        'shortlist_view',
        'shortlist_add',
        'shortlist_remove',
        'export_shortlist',
        'compare_players',
        'player_stats',
        'recommend',
        'head_scout_approvals',
        'workflow_dashboard',
    },
    'manager': 'all',
}


def has_role(user, roles):
    if user.is_superuser:
        return True

    role = get_user_role(user)
    if isinstance(roles, str):
        roles = [roles]

    return role in roles


def has_permission(user, permission):
    if user.is_superuser:
        return True

    role = get_user_role(user)
    permissions = ROLE_ACCESS.get(role, set())
    if permissions == 'all':
        return True

    return permission in permissions


def role_required(permission, redirect_view='dashboard', error_message='You do not have permission to access this page.'):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if not has_permission(request.user, permission):
                messages.error(request, error_message)
                return redirect(redirect_view)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def role_required_json(permission):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'ok': False, 'error': 'Authentication required.'}, status=401)

            if not has_permission(request.user, permission):
                return JsonResponse({'ok': False, 'error': 'You do not have permission to view this data.'}, status=403)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def log_activity(request, action, detail=''):
    """Log user activity to ActivityLog model."""
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
    ActivityLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action,
        detail=detail,
        ip_address=ip.split(',')[0].strip() if ip else None
    )


def sync_user_roles():
    """Sync user roles from Groups to Profile model."""
    for user in User.objects.all():
        if user.is_superuser:
            profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'manager'})
            if profile.role != 'manager':
                profile.role = 'manager'
                profile.save()
            continue

        profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'scout'})

        # Get first group
        first_group = user.groups.first()
        if first_group:
            # Convert group name to internal role value
            group_name = first_group.name.strip()
            profile_role = ROLE_VALUE_MAP.get(group_name, group_name.lower().replace(' ', '_'))
            if profile_role in VALID_ROLES and profile.role != profile_role:
                profile.role = profile_role
                profile.save()


def get_user_role(user):
    if user.is_superuser:
        return 'manager'

    try:
        role = user.profile.role
    except Profile.DoesNotExist:
        role = None

    if role in VALID_ROLES:
        first_group = user.groups.first()

        if first_group is not None:
            group_role = ROLE_VALUE_MAP.get(first_group.name.strip(), first_group.name.lower().replace(' ', '_'))
            if group_role in VALID_ROLES and group_role != 'scout' and role == 'scout':
                return group_role

        return role

    first_group = user.groups.first()
    if first_group:
        fallback_role = ROLE_VALUE_MAP.get(first_group.name.strip(), first_group.name.lower().replace(' ', '_'))
        if fallback_role in VALID_ROLES:
            return fallback_role

    return 'scout'


# =========================================================
# AUTH
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        user = authenticate(
            request,
            username=request.POST.get('username', '').strip(),
            password=request.POST.get('password', '')
        )

        if user:
            login(request, user)
            log_activity(request, 'login', f'User {user.username} logged in')
            return redirect('dashboard')

        class FakeForm:
            errors = True

        return render(
            request,
            'scout/login.html',
            {'form': FakeForm()}
        )

    return render(request, 'scout/login.html')


def register_view(request):
    """
    Admin-only user creation endpoint.
    Validates passwords and restricts users to predefined roles.
    """
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'You do not have permission to create users.')
        return redirect('dashboard')

    error = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'Scout').strip()

        # Normalize role names using the existing role definitions.
        role_lookup = {
            name.lower(): name
            for name in ROLE_VALUE_MAP
        }
        normalized_role = role_lookup.get(role.lower())

        if not username or not password:
            error = 'All fields are required.'

        elif normalized_role is None:
            error = 'Invalid role selected.'

        elif User.objects.filter(username=username).exists():
            error = 'Username already exists.'

        else:
            try:
                candidate_user = User(username=username)
                validate_password(password, user=candidate_user)
            except ValidationError as validation_error:
                error = ' '.join(validation_error.messages)

            if error is None:
                user = User.objects.create_user(
                    username=username,
                    password=password
                )

                group, _ = Group.objects.get_or_create(
                    name=normalized_role
                )
                user.groups.add(group)

                profile_role = ROLE_VALUE_MAP[normalized_role]
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.role = profile_role
                profile.save()

                log_activity(
                    request,
                    'user_create',
                    f'Admin created user {username} with role {normalized_role}'
                )
                messages.success(
                    request,
                    f'User {username} created successfully.'
                )
                return redirect('admin_users')

    return render(
        request,
        'scout/register.html',
        {
            'error': error,
            'success': None,
            'is_admin': True
        }
    )


@require_POST
def logout_view(request):
    username = (
        request.user.username
        if request.user.is_authenticated
        else 'Unknown'
    )

    log_activity(
        request,
        'logout',
        f'User {username} logged out'
    )
    logout(request)

    return redirect('login')


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def dashboard(request):

    from . import api_service

    # For managers, show global stats; for others, personal
    if get_user_role(request.user) == 'manager':
        shortlist_count = Shortlist.objects.all().count()
        recent_shortlist = Shortlist.objects.all().order_by('-added_at')[:5]
    else:
        shortlist_count = Shortlist.objects.filter(
            scout=request.user
        ).count()
        recent_shortlist = Shortlist.objects.filter(
            scout=request.user
        ).order_by('-added_at')[:5]

    all_players = api_service.PLAYERS

    total_players = len(all_players)

    leagues = set()

    for p in all_players:
        if p.get("league"):
            leagues.add(p["league"])

    leagues_count = len(leagues)

    positions = set()

    for p in all_players:
        if p.get("position"):
            positions.add(p["position"])

    positions_count = len(positions)

    forwards_count = len([
        p for p in all_players
        if p.get("position") == "F"
    ])

    midfielders_count = len([
        p for p in all_players
        if p.get("position") == "M"
    ])

    defenders_count = len([
        p for p in all_players
        if p.get("position") == "D"
    ])

    goalkeepers_count = len([
        p for p in all_players
        if p.get("position") == "G"
    ])

    positions_list = [
        (
            'Forward',
            '⚡',
            f'{forwards_count} attacking players'
        ),

        (
            'Midfielder',
            '🎯',
            f'{midfielders_count} midfield players'
        ),

        (
            'Defender',
            '🛡️',
            f'{defenders_count} defensive players'
        ),

        (
            'Goalkeeper',
            '🧤',
            f'{goalkeepers_count} goalkeepers'
        ),
    ]

    player_ids = [item.player_id for item in recent_shortlist]
    note_counts = PlayerNote.objects.filter(
        player_id__in=player_ids
    ).values('player_id').annotate(count=Count('id'))
    shortlist_note_counts = {
        item['player_id']: item['count'] for item in note_counts
    }

    latest_notes = PlayerNote.objects.filter(
        player_id__in=player_ids
    ).order_by('player_id', '-created_at')
    shortlist_ratings = {}
    for note in latest_notes:
        if note.player_id not in shortlist_ratings:
            shortlist_ratings[note.player_id] = note.rating

    for item in recent_shortlist:
        item.rating = shortlist_ratings.get(item.player_id)
        item.note_count = shortlist_note_counts.get(item.player_id, 0)

    return render(
        request,
        'scout/dashboard.html',
        {
            'shortlist_count': shortlist_count,
            'recent_shortlist': recent_shortlist,
            'shortlist_ratings': shortlist_ratings,
            'shortlist_note_counts': shortlist_note_counts,

            'total_players': total_players,
            'leagues_count': leagues_count,
            'positions_count': positions_count,

            'positions_list': positions_list,
        }
    )


# =========================================================
# PLAYERS
# =========================================================

@login_required
def players_by_position(request):

    from . import api_service

    position = request.GET.get('position', 'Forward')
    league_id = request.GET.get('league', '')
    search_q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'name')

    page = int(request.GET.get('page', 1))

    players = []
    total_count = 0
    error = None

    try:

        if search_q:

            result = api_service.search_players(
                search_q,
                page_size=20
            )

        else:

            result = api_service.get_players(
                position=position if position != 'All' else None,
                league_id=league_id or None,
                page=page,
                page_size=20
            )

        players = [
            api_service.enrich_player(p)
            for p in result.get('players', [])
        ]

        total_count = result.get('count', 0)

        def normalize_position_code(code):
            if not code:
                return 'Unknown'
            code = code.upper()
            if code in ['F', 'FORWARD']:
                return 'Forward'
            if code in ['M', 'MIDFIELDER']:
                return 'Midfielder'
            if code in ['D', 'DEFENDER']:
                return 'Defender'
            if code in ['G', 'GOALKEEPER']:
                return 'Goalkeeper'
            return code.title()

        def initials_from_name(name):
            if not name:
                return ''
            parts = [p for p in name.strip().split() if p]
            if len(parts) >= 2:
                return (parts[0][0] + parts[-1][0]).upper()
            return name.strip()[:2].upper()

        def availability_order(value):
            order = {
                'available': 0,
                'unknown': 1,
                'injured': 2,
            }
            return order.get((value or '').lower(), 1)

        for player in players:
            name = player.get('name', '')
            player['initials'] = initials_from_name(name)
            player['position_full'] = normalize_position_code(player.get('position'))
            player['position_class'] = {
                'Forward': 'forward',
                'Midfielder': 'midfielder',
                'Defender': 'defender',
                'Goalkeeper': 'goalkeeper',
            }.get(player['position_full'], 'forward')
            player['position_color'] = {
                'Forward': '#dc2626',
                'Midfielder': '#2563eb',
                'Defender': '#16a34a',
                'Goalkeeper': '#9333ea',
            }.get(player['position_full'], '#082040')
            player['availability_label'] = player.get('availability', 'unknown').capitalize()
            player['availability_status'] = (player.get('availability') or 'unknown').lower()
            player['availability_dot_color'] = {
                'available': '#22c55e',
                'injured': '#ef4444',
                'unknown': '#94a3b8',
            }.get(player['availability_status'], '#94a3b8')

        if sort == 'age':
            players.sort(key=lambda p: p.get('age') if p.get('age') is not None else 999)
        elif sort == 'market_value':
            players.sort(key=lambda p: p.get('market_value') if p.get('market_value') is not None else 0, reverse=True)
        elif sort == 'availability':
            players.sort(key=lambda p: availability_order(p.get('availability')))
        else:
            players.sort(key=lambda p: (p.get('name') or '').lower())

    except Exception as e:

        error = str(e)

    total_pages = math.ceil(total_count / 20) if total_count else 1

    shortlist_count = Shortlist.objects.filter(
        scout=request.user
    ).count()

    page_obj = SimpleNamespace(
        number=page,
        paginator=SimpleNamespace(
            page_range=range(1, total_pages + 1),
            num_pages=total_pages,
            count=total_count,
        ),
        has_previous=page > 1,
        has_next=page < total_pages,
        previous_page_number=page - 1 if page > 1 else 1,
        next_page_number=page + 1 if page < total_pages else total_pages,
    )

    return render(
        request,
        'scout/players.html',
        {
            'players': players,
            'position': position,
            'league_id': league_id,
            'search_q': search_q,
            'sort': sort,
            'error': error,
            'shortlist_count': shortlist_count,

            'total_count': total_count,
            'current_page': page,
            'total_pages': total_pages,
            'page_obj': page_obj,

            'has_next': page < total_pages,
            'has_prev': page > 1,
        }
    )


# =========================================================
# COMPARE
# =========================================================

@login_required
@role_required('compare_players')
def compare_players(request):

    from . import api_service

    ids = request.GET.getlist('ids')

    players_data = []
    error = None

    try:

        for pid in ids[:4]:

            player = api_service.get_player_profile(pid)

            if player:
                players_data.append(
                    api_service.enrich_player(player)
                )

    except Exception as e:

        error = str(e)

    shortlist_count = Shortlist.objects.filter(
        scout=request.user
    ).count()

    return render(
        request,
        'scout/compare.html',
        {
            'players': players_data,
            'chart_data': json.dumps(players_data),
            'player_ids': ids,
            'error': error,
            'shortlist_count': shortlist_count,
        }
    )


# =========================================================
# PROFILE
# =========================================================

@login_required
def player_profile(request, pk):

    from . import api_service

    if request.method == 'POST' and 'note_text' in request.POST:

        note_text = request.POST.get(
            'note_text',
            ''
        ).strip()

        rating = int(
            request.POST.get('rating', 0)
        )

        if note_text:

            PlayerNote.objects.create(
                scout=request.user,
                player_id=pk,
                note=note_text,
                rating=rating
            )

            messages.success(
                request,
                'Note saved.'
            )

            return redirect(
                'player_profile',
                pk=pk
            )

    profile = {}
    error = None

    try:

        profile = api_service.get_player_profile(pk)

        if profile:
            profile = api_service.enrich_player(profile)

    except Exception as e:

        error = str(e)

    notes = PlayerNote.objects.filter(
        scout=request.user,
        player_id=pk
    ).order_by('-created_at')

    in_shortlist = Shortlist.objects.filter(
        scout=request.user,
        player_id=pk
    ).exists()

    shortlist_count = Shortlist.objects.filter(
        scout=request.user
    ).count()

    return render(
        request,
        'scout/profile.html',
        {
            'profile': profile,
            'notes': notes,
            'in_shortlist': in_shortlist,

            'player_id': pk,
            'player_name': profile.get('name', ''),

            'error': error,
            'shortlist_count': shortlist_count,

            'chart_data': json.dumps(profile),
        }
    )


# =========================================================
# STATS API
# =========================================================

@login_required
@role_required_json('player_stats')
def player_stats_api(request, pk):

    from . import api_service

    try:

        profile = api_service.get_player_profile(pk)

        if not profile:

            return JsonResponse({
                'ok': False,
                'error': 'Player not found'
            })

        profile = api_service.enrich_player(profile)

        match_stats = api_service.get_player_match_stats(pk)

        player_stats = api_service.format_player_stats(
            api_service.get_player_stats(pk)
        )

        return JsonResponse({
            'ok': True,
            'match_stats': match_stats,
            'af_stats': player_stats,
            'image_url': profile.get('photo'),
        })

    except Exception as e:

        return JsonResponse({
            'ok': False,
            'error': str(e)
        })

# =========================================================
# RECOMMENDATIONS
# =========================================================

@login_required
@role_required('recommend')
def recommend(request):
    user_role = get_user_role(request.user)
    if user_role not in ['scout', 'manager']:
        messages.error(request, 'Only Scouts and Managers can access recommendations.')
        return redirect('dashboard')

    from . import api_service

    shortlist_count = Shortlist.objects.filter(
        scout=request.user
    ).count()

    position_filter = request.GET.get(
        'position',
        'Forward'
    )

    min_age = int(
        request.GET.get('min_age', 18)
    )

    max_age = int(
        request.GET.get('max_age', 35)
    )

    availability = request.GET.get(
        'availability',
        'all'
    )

    positions = [
        ('Forward', '⚡'),
        ('Midfielder', '🎯'),
        ('Defender', '🛡️'),
        ('Goalkeeper', '🧤'),
    ]

    recommendations = []

    try:

        result = api_service.get_players(
            position=position_filter,
            page_size=40
        )

        players = [
            api_service.enrich_player(p)
            for p in result.get('players', [])
        ]

        filtered = []

        for p in players:

            age = p.get('age')

            if age and (
                age < min_age or
                age > max_age
            ):
                continue

            if (
                availability == 'available' and
                p.get('availability') != 'available'
            ):
                continue

            filtered.append(p)

        def score(p):

            s = 0

            if p.get('availability') == 'available':
                s += 40

            age = p.get('age') or 25

            if 24 <= age <= 29:
                s += 30

            elif 21 <= age < 24:
                s += 22

            elif 30 <= age <= 33:
                s += 15

            else:
                s += 8

            mv = p.get('market_value') or 0

            if mv > 5_000_000:
                s += 20

            elif mv > 1_000_000:
                s += 15

            elif mv > 500_000:
                s += 10

            elif mv > 0:
                s += 5

            tc = len(p.get('transfers', []))

            if tc == 0:
                s += 10

            elif tc <= 2:
                s += 7

            elif tc <= 4:
                s += 4

            return s

        for p in filtered:
            p['fit_score'] = score(p)
            if p['fit_score'] >= 80:
                p['fit_grade'] = 'A+'
            elif p['fit_score'] >= 65:
                p['fit_grade'] = 'A'
            elif p['fit_score'] >= 45:
                p['fit_grade'] = 'B'
            else:
                p['fit_grade'] = 'C'

        recommendations = sorted(
            filtered,
            key=lambda p: p['fit_score'],
            reverse=True
        )[:12]

    except Exception as e:

        print(f'[RECOMMEND] Error: {e}')

    return render(
        request,
        'scout/recommend.html',
        {
            'shortlist_count': shortlist_count,
            'recommendations': recommendations,
            'position_filter': position_filter,
            'positions': positions,
            'min_age': min_age,
            'max_age': max_age,
            'availability': availability,
        }
    )


# =========================================================
# SHORTLIST
# =========================================================

@login_required
@role_required('shortlist_view')
def shortlist(request):

    user_role = get_user_role(request.user)
    is_manager_or_head_scout = user_role in ['head_scout', 'manager']
    is_analyst = user_role == 'analyst'

    if is_manager_or_head_scout:
        players = Shortlist.objects.all().order_by('-added_at')
    elif is_analyst:
        assigned_scout = getattr(request.user.profile, 'assigned_scout', None)
        if assigned_scout:
            players = Shortlist.objects.filter(
                scout=assigned_scout
            ).order_by('-added_at')
        else:
            players = Shortlist.objects.all().order_by('-added_at')
    else:
        players = Shortlist.objects.filter(
            scout=request.user
        ).order_by('-added_at')

    position_counts = {
        'Forward': players.filter(position='Forward').count(),
        'Midfielder': players.filter(position='Midfielder').count(),
        'Defender': players.filter(position='Defender').count(),
        'Goalkeeper': players.filter(position='Goalkeeper').count(),
    }

    approval_map = {}
    if is_analyst:
        approvals = PlayerApproval.objects.filter(shortlist_entry__in=players)
        approval_map = {
            approval.shortlist_entry_id: approval.id
            for approval in approvals
        }

    return render(
        request,
        'scout/shortlist.html',
        {
            'players': players,
            'shortlist_count': players.count(),
            'position_counts': position_counts,
            'is_manager_or_head_scout': is_manager_or_head_scout,
            'is_analyst': is_analyst,
            'approval_map': approval_map,
        }
    )


@login_required
@role_required('shortlist_add')
def add_to_shortlist(request):

    if request.method == 'POST':

        player_id = request.POST.get('player_id')

        player_name = request.POST.get(
            'player_name',
            'Unknown'
        )

        obj, created = Shortlist.objects.get_or_create(
            scout=request.user,
            player_id=player_id,

            defaults={
                'player_name': player_name,
                'position': request.POST.get('position', ''),
                'team': request.POST.get('team', ''),
            }
        )

        if created:

            messages.success(
                request,
                f'{player_name} added to shortlist.'
            )
            log_activity(request, 'shortlist_add', f'Added player {player_name} (ID {player_id})')

        else:

            messages.info(
                request,
                f'{player_name} is already in your shortlist.'
            )

        next_url = request.POST.get(
            'next',
            'players'
        )

        return redirect(
            next_url
            if next_url in [
                'players',
                'shortlist',
                'dashboard',
                'compare'
            ]
            else 'players'
        )

    return redirect('shortlist')


@login_required
@role_required('shortlist_remove')
def remove_shortlist(request):

    if request.method == 'POST':

        shortlist_id = request.POST.get('shortlist_id')
        shortlist_obj = None
        player_name = 'Unknown'

        if shortlist_id:
            try:
                shortlist_obj = Shortlist.objects.get(id=shortlist_id)
            except Shortlist.DoesNotExist:
                shortlist_obj = None

        if shortlist_obj:
            player_name = shortlist_obj.player_name
            user_role = get_user_role(request.user)

            if user_role in ['head_scout', 'manager'] or shortlist_obj.scout == request.user:
                shortlist_obj.delete()
                messages.success(request, 'Player removed from shortlist.')
                log_activity(request, 'shortlist_remove', f'Removed player {player_name} (ID {shortlist_id})')
            else:
                messages.error(request, 'You do not have permission to remove this shortlist entry.')
        else:
            messages.error(request, 'Shortlist item not found.')

    return redirect('shortlist')


# =========================================================
# EXPORT CSV
# =========================================================

@login_required
@role_required('export_shortlist')
def export_shortlist(request):

    players = Shortlist.objects.filter(
        scout=request.user
    ).order_by('-added_at')

    response = HttpResponse(
        content_type='text/csv'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="shortlist.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Name',
        'Position',
        'Team',
        'Notes',
        'Added'
    ])

    for p in players:

        writer.writerow([
            p.player_name,
            p.position,
            p.team,
            p.notes,
            p.added_at.strftime('%Y-%m-%d')
        ])

    log_activity(request, 'export_csv', f'{len(players)} players exported')

    return response


# =========================================================
# ADMIN PANEL
# =========================================================

def admin_only(view_func):
    """Decorator to restrict view to superusers only."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'You do not have permission to access the admin panel.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_only
def admin_panel(request):
    """Redirect to admin users page."""
    return redirect('admin_users')


@login_required
@role_required('view_profile')
def user_profile(request, user_id):
    """Return a profile page for a single user."""
    target_user = User.objects.filter(id=user_id).first()
    if not target_user:
        messages.error(request, 'User not found.')
        return redirect('dashboard')

    if not request.user.is_superuser and request.user.id != target_user.id:
        messages.error(request, 'You do not have permission to view this profile.')
        return redirect('dashboard')

    profile, _ = Profile.objects.get_or_create(user=target_user)
    user_role = get_user_role(target_user)
    role_name = 'Manager' if target_user.is_superuser else (profile.get_role_display() if profile.role else 'Scout')

    role_permissions = {
        'can_add_shortlist': user_role in ['scout', 'head_scout', 'manager'],
        'can_view_players': True,
        'can_recommend': user_role in ['analyst', 'head_scout', 'manager'],
        'can_approve': user_role in ['head_scout', 'manager'],
        'can_admin': user_role == 'manager',
    }

    if user_role in ['head_scout', 'manager']:
        shortlist_count = Shortlist.objects.all().count()
    else:
        shortlist_count = Shortlist.objects.filter(scout=target_user).count()

    activity_logs = ActivityLog.objects.filter(
        user=target_user
    ).order_by('-timestamp')[:10]

    total_actions = ActivityLog.objects.filter(
        user=target_user
    ).count()

    own_profile = request.user == target_user

    return render(
        request,
        'scout/user_profile.html',
        {
            'target_user': target_user,
            'profile': profile,
            'role_name': role_name,
            'user_role': user_role,
            'role_permissions': role_permissions,
            'shortlist_count': shortlist_count,
            'activity_logs': activity_logs,
            'total_actions': total_actions,
            'own_profile': own_profile,
            'can_view_password': request.user.is_superuser,
        }
    )


@login_required
@role_required('edit_profile')
def edit_profile(request, user_id):
    target_user = User.objects.filter(id=user_id).first()
    if not target_user:
        messages.error(request, 'User not found.')
        return redirect('dashboard')

    if request.user != target_user and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit this profile.')
        return redirect('dashboard')

    profile, _ = Profile.objects.get_or_create(user=target_user)
    role_name = 'Manager' if target_user.is_superuser else (
        profile.get_role_display() if profile.role else 'Scout'
    )
    user_role = get_user_role(target_user)

    if request.method == 'POST':
        bio = request.POST.get('bio', '').strip()
        phone = request.POST.get('phone', '').strip()

        if len(phone) > 20:
            messages.error(request, 'Phone number must not exceed 20 characters.')
            return redirect('edit_profile', user_id=target_user.id)

        assigned_scout = profile.assigned_scout

        if request.user.is_superuser:
            assigned_id = request.POST.get('assigned_scout', '').strip()

            if assigned_id:
                assigned_scout = User.objects.filter(
                    id=assigned_id,
                    is_active=True,
                    profile__role='scout'
                ).first()

                if assigned_scout is None:
                    messages.error(
                        request,
                        'Please select a valid active Scout.'
                    )
                    return redirect('edit_profile', user_id=target_user.id)
            else:
                assigned_scout = None

        profile.bio = bio
        profile.phone = phone

        if request.user.is_superuser:
            profile.assigned_scout = assigned_scout

        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('user_profile', user_id=target_user.id)

    assigned_scout_options = (
        User.objects.filter(
            is_active=True,
            profile__role='scout'
        ).order_by('username')
        if request.user.is_superuser else []
    )

    return render(
        request,
        'scout/edit_profile.html',
        {
            'target_user': target_user,
            'profile': profile,
            'role_name': role_name,
            'user_role': user_role,
            'assigned_scout_options': assigned_scout_options,
            'own_profile': request.user == target_user,
        }
    )

@login_required
@role_required('analyst_review')
def analyst_review(request, shortlist_id):
    from decimal import Decimal, InvalidOperation

    user_role = get_user_role(request.user)
    if user_role not in ['analyst', 'manager']:
        messages.error(request, 'Only Analysts and Managers can access this page.')
        return redirect('dashboard')

    shortlist_entry = Shortlist.objects.filter(id=shortlist_id).first()
    if not shortlist_entry:
        messages.error(request, 'Shortlist entry not found.')
        return redirect('shortlist')

    if user_role == 'analyst':
        profile = Profile.objects.filter(user=request.user).first()
        assigned_scout = profile.assigned_scout if profile else None

        if assigned_scout is None:
            messages.error(
                request,
                'You must be assigned to a Scout before reviewing players.'
            )
            return redirect('shortlist')

        if shortlist_entry.scout_id != assigned_scout.id:
            messages.error(
                request,
                'You are not assigned to this Scout shortlist.'
            )
            return redirect('shortlist')

    approval = PlayerApproval.objects.filter(
        shortlist_entry=shortlist_entry
    ).first()

    if request.method == 'POST':
        raw_rating = request.POST.get('analyst_rating', '0').strip()
        recommendation = request.POST.get(
            'analyst_recommendation',
            'pending'
        )
        analyst_note = request.POST.get('analyst_note', '').strip()

        try:
            rating = Decimal(raw_rating)
            valid_rating = (
                rating.is_finite()
                and Decimal('0') <= rating <= Decimal('10')
                and rating.as_tuple().exponent >= -1
            )
        except (InvalidOperation, ValueError, TypeError):
            valid_rating = False
            rating = None

        if not valid_rating:
            messages.error(
                request,
                'Invalid rating. Enter a value between 0 and 10 with at most one decimal place.'
            )
            return redirect('analyst_review', shortlist_id=shortlist_entry.id)

        if recommendation not in ['recommend', 'reject', 'pending']:
            messages.error(request, 'Invalid recommendation.')
            return redirect('analyst_review', shortlist_id=shortlist_entry.id)

        if (
            user_role == 'analyst'
            and approval is not None
            and approval.analyst_id is not None
            and approval.analyst_id != request.user.id
        ):
            messages.error(
                request,
                'This review has already been assigned to another Analyst.'
            )
            return redirect('shortlist')

        approval, created = PlayerApproval.objects.get_or_create(
            shortlist_entry=shortlist_entry,
            defaults={
                'player_id': shortlist_entry.player_id,
                'player_name': shortlist_entry.player_name,
                'scout': shortlist_entry.scout,
                'analyst': request.user if user_role == 'analyst' else None,
            }
        )

        if (
            user_role == 'analyst'
            and approval.analyst_id is not None
            and approval.analyst_id != request.user.id
        ):
            messages.error(
                request,
                'This review has already been assigned to another Analyst.'
            )
            return redirect('shortlist')

        approval.analyst_note = analyst_note
        approval.analyst_rating = rating
        approval.analyst_recommendation = recommendation

        if user_role == 'analyst':
            approval.analyst = request.user

        approval.save()

        log_activity(
            request,
            'analyst_review',
            f'Player approval {approval.id} updated with recommendation {approval.analyst_recommendation}'
        )
        messages.success(request, 'Review submitted successfully.')
        return redirect('shortlist')

    if approval is None:
        approval = PlayerApproval(
            player_id=shortlist_entry.player_id,
            player_name=shortlist_entry.player_name,
            scout=shortlist_entry.scout,
            shortlist_entry=shortlist_entry,
            analyst=request.user if user_role == 'analyst' else None,
        )

    return render(
        request,
        'scout/analyst_review.html',
        {
            'shortlist_entry': shortlist_entry,
            'approval': approval,
            'user_role': user_role,
        }
    )
@login_required
@role_required('head_scout_approvals')
def head_scout_approvals(request):
    user_role = get_user_role(request.user)
    if user_role not in ['head_scout', 'manager']:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    if request.method == 'POST':
        approval_id = request.POST.get('player_approval_id', '').strip()
        decision = request.POST.get('decision')
        head_scout_note = request.POST.get('head_scout_note', '').strip()

        if decision not in ['approved', 'rejected']:
            messages.error(request, 'Unable to record decision.')
            return redirect('head_scout_approvals')

        try:
            updated_count = PlayerApproval.objects.filter(
                pk=approval_id,
                analyst_recommendation='recommend',
                head_scout_decision='pending'
            ).update(
                head_scout_decision=decision,
                head_scout_note=head_scout_note
            )
        except (TypeError, ValueError):
            updated_count = 0

        if updated_count == 1:
            log_activity(
                request,
                'head_scout_decision',
                f'Approval {approval_id} set to {decision}'
            )
            messages.success(request, 'Decision recorded.')
        else:
            messages.error(
                request,
                'Unable to record decision. This approval may no longer be pending.'
            )

        return redirect('head_scout_approvals')

    pending_approvals = PlayerApproval.objects.filter(
        analyst_recommendation='recommend',
        head_scout_decision='pending'
    ).order_by('-updated_at')

    total_pending = pending_approvals.count()
    total_approved = PlayerApproval.objects.filter(head_scout_decision='approved').count()
    total_rejected = PlayerApproval.objects.filter(head_scout_decision='rejected').count()

    return render(
        request,
        'scout/head_scout_approvals.html',
        {
            'pending_approvals': pending_approvals,
            'total_pending': total_pending,
            'total_approved': total_approved,
            'total_rejected': total_rejected,
        }
    )


@login_required
@role_required('workflow_dashboard')
def workflow_dashboard(request):
    user_role = get_user_role(request.user)
    if user_role != 'manager':
        messages.error(request, 'Only Managers can access the workflow dashboard.')
        return redirect('dashboard')

    total_scouts = Profile.objects.filter(role='scout').count()
    total_analysts = Profile.objects.filter(role='analyst').count()
    total_shortlist = Shortlist.objects.count()
    total_recommended = PlayerApproval.objects.filter(analyst_recommendation='recommend').count()
    total_approved = PlayerApproval.objects.filter(head_scout_decision='approved').count()
    approvals = PlayerApproval.objects.all().order_by('-updated_at')

    return render(
        request,
        'scout/workflow_dashboard.html',
        {
            'total_scouts': total_scouts,
            'total_analysts': total_analysts,
            'total_shortlist': total_shortlist,
            'total_recommended': total_recommended,
            'total_approved': total_approved,
            'approvals': approvals,
        }
    )


@login_required
@admin_only
def admin_users(request):
    """Admin users management page."""
    # Sync roles from Groups to Profile
    sync_user_roles()

    all_users = User.objects.all().order_by('-date_joined')
    active_users = all_users.filter(is_active=True).count()
    inactive_users = all_users.filter(is_active=False).count()
    superusers = all_users.filter(is_superuser=True).count()
    total_users = all_users.count()

    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = 20
    total_pages = (total_users + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size
    users_page = all_users[start:end]

    return render(
        request,
        'scout/admin_users.html',
        {
            'users_list': users_page,
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'superusers': superusers,
            'current_page': page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
        }
    )


@login_required
@admin_only
def admin_audit(request):
    """Admin audit logs page."""
    # Sync roles to ensure consistency
    sync_user_roles()

    action_filter = request.GET.get('action_filter', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    logs = ActivityLog.objects.all().order_by('-timestamp')

    if action_filter:
        logs = logs.filter(action=action_filter)
    if date_from:
        from datetime import datetime
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            logs = logs.filter(timestamp__gte=date_from_obj)
        except:
            pass
    if date_to:
        from datetime import datetime
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            logs = logs.filter(timestamp__lte=date_to_obj)
        except:
            pass

    # Paginate logs (20 per page)
    page = int(request.GET.get('page', 1))
    page_size = 20
    total_logs = logs.count()
    total_pages = (total_logs + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size
    logs_page = logs[start:end]

    # Get unique action types for filter dropdown
    action_types = ActivityLog.objects.values_list('action', flat=True).distinct().order_by('action')

    return render(
        request,
        'scout/admin_audit.html',
        {
            'logs': logs_page,
            'action_filter': action_filter,
            'date_from': date_from,
            'date_to': date_to,
            'action_types': action_types,
            'current_page': page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'total_logs': total_logs,
        }
    )


@login_required
@admin_only
def admin_logs(request):
    """Admin detailed logs page."""
    # Sync roles to ensure consistency
    sync_user_roles()

    action_filter = request.GET.get('action_filter', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    user_filter = request.GET.get('user_filter', '')

    logs = ActivityLog.objects.all().order_by('-timestamp')

    if action_filter:
        logs = logs.filter(action=action_filter)
    if date_from:
        from datetime import datetime
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            logs = logs.filter(timestamp__gte=date_from_obj)
        except:
            pass
    if date_to:
        from datetime import datetime
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            logs = logs.filter(timestamp__lte=date_to_obj)
        except:
            pass
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)

    # Paginate logs (20 per page)
    page = int(request.GET.get('page', 1))
    page_size = 20
    total_logs = logs.count()
    total_pages = (total_logs + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size
    logs_page = logs[start:end]

    # Get unique action types for filter dropdown
    action_types = ActivityLog.objects.values_list('action', flat=True).distinct().order_by('action')

    # Get log statistics
    from datetime import date as date_class
    today_logs = logs.filter(timestamp__date=date_class.today()).count()
    log_stats = {
        'total': total_logs,
        'today': today_logs,
    }

    return render(
        request,
        'scout/admin_logs.html',
        {
            'logs': logs_page,
            'action_filter': action_filter,
            'date_from': date_from,
            'date_to': date_to,
            'user_filter': user_filter,
            'action_types': action_types,
            'current_page': page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1,
            'total_logs': total_logs,
            'log_stats': log_stats,
        }
    )


@login_required
@admin_only
def toggle_user_active(request, user_id):
    """Toggle an ordinary user's active status. Superusers are protected."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    user = User.objects.filter(id=user_id).first()

    if user is None:
        messages.error(request, 'User not found.')
        return redirect('admin_users')

    if user.is_superuser:
        messages.error(request, 'Superuser accounts cannot be modified here.')
        return redirect('admin_users')

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])

    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} has been {status}.')
    log_activity(
        request,
        'user_toggle',
        f'User {user.username} toggled to {status}'
    )
    return redirect('admin_users')

@login_required
@admin_only
def delete_user_admin(request, user_id):
    """Delete an ordinary user. Superusers are protected."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    user = User.objects.filter(id=user_id).first()

    if user is None:
        messages.error(request, 'User not found.')
        return redirect('admin_users')

    if user.is_superuser:
        messages.error(request, 'Superuser accounts cannot be deleted here.')
        return redirect('admin_users')

    username = user.username
    user.delete()

    messages.success(request, f'User {username} has been deleted.')
    log_activity(request, 'user_delete', f'User {username} deleted')
    return redirect('admin_users')

@login_required
@admin_only
def clear_logs(request):
    """Clear all activity logs. This action is POST-only."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    count = ActivityLog.objects.count()
    ActivityLog.objects.all().delete()

    messages.success(request, f'Cleared {count} activity log entries.')
    log_activity(
        request,
        'logs_clear',
        f'Cleared all {count} activity logs'
    )
    return redirect('admin_audit')
