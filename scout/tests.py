from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.urls import reverse
from unittest.mock import patch

from .models import Profile, Shortlist, PlayerApproval


class ScoutAccessTests(TestCase):

    def setUp(self):
        self.group, _ = Group.objects.get_or_create(name='Scout')
        self.user = User.objects.create_user(
            username='scout_user',
            password='testpass123'
        )
        self.user.groups.add(self.group)
        self.user.profile.role = 'scout'
        self.user.profile.save()

    @patch('scout.api_service.enrich_player')
    @patch('scout.api_service.get_player_profile')
    def test_scout_can_access_compare(self, mock_get_player_profile, mock_enrich_player):
        mock_get_player_profile.return_value = {'id': 1, 'name': 'Test Player'}
        mock_enrich_player.side_effect = lambda profile: profile

        self.client.login(username='scout_user', password='testpass123')
        response = self.client.get(
            reverse('compare'),
            {'ids': [1]}
        )

        self.assertEqual(response.status_code, 200)

    @patch('scout.api_service.get_player_stats')
    @patch('scout.api_service.format_player_stats')
    @patch('scout.api_service.get_player_match_stats')
    @patch('scout.api_service.enrich_player')
    @patch('scout.api_service.get_player_profile')
    def test_scout_can_access_stats_api(
        self,
        mock_get_player_profile,
        mock_enrich_player,
        mock_get_player_match_stats,
        mock_format_player_stats,
        mock_get_player_stats,
    ):
        mock_get_player_profile.return_value = {
            'id': 1,
            'name': 'Test Player',
            'photo': 'https://example.com/photo.png'
        }
        mock_enrich_player.side_effect = lambda profile: profile
        mock_get_player_match_stats.return_value = {'matches': []}
        mock_get_player_stats.return_value = {}
        mock_format_player_stats.return_value = {}

        self.client.login(username='scout_user', password='testpass123')
        response = self.client.get(reverse('player_stats_api', args=[1]))

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {
                'ok': True,
                'match_stats': {'matches': []},
                'af_stats': {},
                'image_url': 'https://example.com/photo.png',
            }
        )


class SignalRegistrationTests(TestCase):

    def test_user_creation_triggers_profile_signal(self):
        user = User.objects.create_user(
            username='profile_user',
            password='testpass123'
        )

        self.assertTrue(Profile.objects.filter(user=user).exists())



class AuthenticationHardeningTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='security_admin',
            email='security_admin@example.test',
            password='Admin#Secure2026!'
        )
        self.client.login(
            username='security_admin',
            password='Admin#Secure2026!'
        )

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'new_scout_weak',
                'password': '123',
                'role': 'Scout',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'password', html=False)
        self.assertFalse(User.objects.filter(username='new_scout_weak').exists())

    def test_registration_rejects_unknown_role_without_creating_group(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'new_scout_invalid_role',
                'password': 'Strong#Password2026',
                'role': 'Unexpected Role',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid role selected.')
        self.assertFalse(User.objects.filter(username='new_scout_invalid_role').exists())
        self.assertFalse(Group.objects.filter(name='Unexpected Role').exists())

    def test_registration_creates_user_with_hashed_password_and_valid_role(self):
        raw_password = 'Strong#Password2026'
        response = self.client.post(
            reverse('register'),
            {
                'username': 'new_analyst',
                'password': raw_password,
                'role': 'Analyst',
            }
        )

        self.assertRedirects(response, reverse('admin_users'))
        user = User.objects.get(username='new_analyst')
        self.assertTrue(user.check_password(raw_password))
        self.assertNotEqual(user.password, raw_password)
        self.assertEqual(user.profile.role, 'analyst')
        self.assertTrue(user.groups.filter(name='Analyst').exists())

    def test_get_logout_is_rejected_and_keeps_session(self):
        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)

    def test_post_logout_ends_session(self):
        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

class AnalystAssignmentSecurityTests(TestCase):

    def setUp(self):
        self.scout = User.objects.create_user(
            username='assigned_scout',
            password='testpass123'
        )

        self.other_scout = User.objects.create_user(
            username='other_scout',
            password='testpass123'
        )

        self.analyst = User.objects.create_user(
            username='security_analyst',
            password='testpass123'
        )
        self.analyst.profile.role = 'analyst'
        self.analyst.profile.save()

        self.shortlist = Shortlist.objects.create(
            scout=self.scout,
            player_id=101,
            player_name='Test Player'
        )

        self.client.force_login(self.analyst)

    def test_unassigned_analyst_cannot_review_shortlist(self):
        response = self.client.get(
            reverse('analyst_review', args=[self.shortlist.id])
        )

        self.assertRedirects(response, reverse('shortlist'))
        self.assertFalse(
            PlayerApproval.objects.filter(
                shortlist_entry=self.shortlist
            ).exists()
        )

    def test_analyst_cannot_review_another_scout_shortlist(self):
        self.analyst.profile.assigned_scout = self.other_scout
        self.analyst.profile.save()

        response = self.client.get(
            reverse('analyst_review', args=[self.shortlist.id])
        )

        self.assertRedirects(response, reverse('shortlist'))
        self.assertFalse(
            PlayerApproval.objects.filter(
                shortlist_entry=self.shortlist
            ).exists()
        )

    def test_analyst_can_view_assigned_scout_shortlist_without_creating_review(self):
        self.analyst.profile.assigned_scout = self.scout
        self.analyst.profile.save()

        response = self.client.get(
            reverse('analyst_review', args=[self.shortlist.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['approval'].pk)
        self.assertFalse(
            PlayerApproval.objects.filter(
                shortlist_entry=self.shortlist
            ).exists()
        )

    def test_valid_analyst_post_creates_review(self):
        self.analyst.profile.assigned_scout = self.scout
        self.analyst.profile.save()

        response = self.client.post(
            reverse('analyst_review', args=[self.shortlist.id]),
            {
                'analyst_note': 'Strong performance',
                'analyst_rating': '8.5',
                'analyst_recommendation': 'recommend',
            }
        )

        self.assertRedirects(response, reverse('shortlist'))
        approval = PlayerApproval.objects.get(
            shortlist_entry=self.shortlist
        )
        self.assertEqual(approval.analyst, self.analyst)
        self.assertEqual(approval.analyst_rating, 8.5)
        self.assertEqual(approval.analyst_recommendation, 'recommend')

    def test_invalid_rating_is_rejected_without_creating_review(self):
        self.analyst.profile.assigned_scout = self.scout
        self.analyst.profile.save()

        response = self.client.post(
            reverse('analyst_review', args=[self.shortlist.id]),
            {
                'analyst_note': 'Invalid rating test',
                'analyst_rating': 'not-a-number',
                'analyst_recommendation': 'recommend',
            }
        )

        self.assertRedirects(
            response,
            reverse('analyst_review', args=[self.shortlist.id])
        )
        self.assertFalse(
            PlayerApproval.objects.filter(
                shortlist_entry=self.shortlist
            ).exists()
        )

    def test_rating_above_ten_is_rejected(self):
        self.analyst.profile.assigned_scout = self.scout
        self.analyst.profile.save()

        response = self.client.post(
            reverse('analyst_review', args=[self.shortlist.id]),
            {
                'analyst_rating': '10.1',
                'analyst_recommendation': 'recommend',
            }
        )

        self.assertRedirects(
            response,
            reverse('analyst_review', args=[self.shortlist.id])
        )
        self.assertFalse(
            PlayerApproval.objects.filter(
                shortlist_entry=self.shortlist
            ).exists()
        )

    def test_invalid_recommendation_is_rejected(self):
        self.analyst.profile.assigned_scout = self.scout
        self.analyst.profile.save()

        response = self.client.post(
            reverse('analyst_review', args=[self.shortlist.id]),
            {
                'analyst_rating': '7.5',
                'analyst_recommendation': 'approve-everything',
            }
        )

        self.assertRedirects(
            response,
            reverse('analyst_review', args=[self.shortlist.id])
        )
        self.assertFalse(
            PlayerApproval.objects.filter(
                shortlist_entry=self.shortlist
            ).exists()
        )

    def test_analyst_cannot_overwrite_another_analysts_review(self):
        self.analyst.profile.assigned_scout = self.scout
        self.analyst.profile.save()

        other_analyst = User.objects.create_user(
            username='another_analyst',
            password='testpass123'
        )
        other_analyst.profile.role = 'analyst'
        other_analyst.profile.assigned_scout = self.scout
        other_analyst.profile.save()

        approval = PlayerApproval.objects.create(
            shortlist_entry=self.shortlist,
            player_id=self.shortlist.player_id,
            player_name=self.shortlist.player_name,
            scout=self.scout,
            analyst=other_analyst,
            analyst_note='Original review',
            analyst_rating='7.0',
            analyst_recommendation='pending',
        )

        response = self.client.post(
            reverse('analyst_review', args=[self.shortlist.id]),
            {
                'analyst_note': 'Attempted overwrite',
                'analyst_rating': '9.5',
                'analyst_recommendation': 'recommend',
            }
        )

        self.assertRedirects(response, reverse('shortlist'))
        approval.refresh_from_db()
        self.assertEqual(approval.analyst, other_analyst)
        self.assertEqual(approval.analyst_note, 'Original review')
        self.assertEqual(approval.analyst_rating, 7.0)
        self.assertEqual(approval.analyst_recommendation, 'pending')

class HeadScoutWorkflowSecurityTests(TestCase):

    def setUp(self):
        self.scout = User.objects.create_user(
            username='workflow_scout',
            password='testpass123'
        )

        self.analyst = User.objects.create_user(
            username='workflow_analyst',
            password='testpass123'
        )
        self.analyst.profile.role = 'analyst'
        self.analyst.profile.assigned_scout = self.scout
        self.analyst.profile.save()

        self.head_scout = User.objects.create_user(
            username='workflow_head_scout',
            password='testpass123'
        )
        self.head_scout.profile.role = 'head_scout'
        self.head_scout.profile.save()

        self.shortlist = Shortlist.objects.create(
            scout=self.scout,
            player_id=202,
            player_name='Workflow Test Player'
        )

        self.client.force_login(self.head_scout)

    def create_approval(self, recommendation='recommend', decision='pending'):
        return PlayerApproval.objects.create(
            player_id=self.shortlist.player_id,
            player_name=self.shortlist.player_name,
            scout=self.scout,
            analyst=self.analyst,
            shortlist_entry=self.shortlist,
            analyst_recommendation=recommendation,
            head_scout_decision=decision
        )

    def post_decision(self, approval_id, decision='approved'):
        return self.client.post(
            reverse('head_scout_approvals'),
            {
                'player_approval_id': approval_id,
                'decision': decision,
                'head_scout_note': 'Reviewed by Head Scout',
            }
        )

    def test_head_scout_can_decide_pending_recommendation(self):
        approval = self.create_approval()

        response = self.post_decision(approval.id, 'approved')

        self.assertRedirects(
            response,
            reverse('head_scout_approvals')
        )

        approval.refresh_from_db()
        self.assertEqual(approval.head_scout_decision, 'approved')
        self.assertEqual(
            approval.head_scout_note,
            'Reviewed by Head Scout'
        )

    def test_head_scout_cannot_decide_rejected_analyst_recommendation(self):
        approval = self.create_approval(recommendation='reject')

        self.post_decision(approval.id, 'approved')

        approval.refresh_from_db()
        self.assertEqual(approval.head_scout_decision, 'pending')

    def test_head_scout_cannot_change_already_decided_approval(self):
        approval = self.create_approval(decision='approved')

        self.post_decision(approval.id, 'rejected')

        approval.refresh_from_db()
        self.assertEqual(approval.head_scout_decision, 'approved')

    def test_head_scout_invalid_approval_id_does_not_crash(self):
        response = self.post_decision('not-a-valid-id', 'approved')

        self.assertRedirects(
            response,
            reverse('head_scout_approvals')
        )

    def test_head_scout_rejects_invalid_decision_value(self):
        approval = self.create_approval()

        self.post_decision(approval.id, 'pending')

        approval.refresh_from_db()
        self.assertEqual(approval.head_scout_decision, 'pending')


class AdminEndpointSecurityTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='security_admin',
            email='admin@example.com',
            password='testpass123'
        )
        self.target = User.objects.create_user(
            username='ordinary_target',
            password='testpass123'
        )
        self.other_admin = User.objects.create_superuser(
            username='protected_admin',
            email='protected@example.com',
            password='testpass123'
        )
        self.client.force_login(self.admin)

    def test_toggle_user_requires_post(self):
        response = self.client.get(
            reverse('toggle_user_active', args=[self.target.id])
        )
        self.assertEqual(response.status_code, 405)
        self.assertTrue(self.target.is_active)

    def test_delete_user_requires_post(self):
        response = self.client.get(
            reverse('delete_user_admin', args=[self.target.id])
        )
        self.assertEqual(response.status_code, 405)
        self.assertTrue(User.objects.filter(id=self.target.id).exists())

    def test_clear_logs_requires_post(self):
        response = self.client.get(reverse('clear_logs'))
        self.assertEqual(response.status_code, 405)

    def test_cannot_deactivate_superuser(self):
        response = self.client.post(
            reverse('toggle_user_active', args=[self.other_admin.id])
        )
        self.assertEqual(response.status_code, 302)
        self.other_admin.refresh_from_db()
        self.assertTrue(self.other_admin.is_active)

    def test_cannot_delete_superuser(self):
        response = self.client.post(
            reverse('delete_user_admin', args=[self.other_admin.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.filter(id=self.other_admin.id).exists()
        )

    def test_toggle_missing_user_does_not_raise_exception(self):
        response = self.client.post(
            reverse('toggle_user_active', args=[99999999])
        )
        self.assertEqual(response.status_code, 302)

    def test_delete_missing_user_does_not_raise_exception(self):
        response = self.client.post(
            reverse('delete_user_admin', args=[99999999])
        )
        self.assertEqual(response.status_code, 302)
