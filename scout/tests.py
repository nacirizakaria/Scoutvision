from django.test import TestCase
from django.contrib.auth.models import Group, User
from django.urls import reverse
from unittest.mock import patch

from .models import Profile


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
