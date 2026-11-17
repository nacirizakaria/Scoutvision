from django.db import models


# =========================================================
# SHORTLIST
# =========================================================

class Shortlist(models.Model):

    scout = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    player_id = models.IntegerField()

    player_name = models.CharField(
        max_length=200
    )

    position = models.CharField(
        max_length=100,
        blank=True
    )

    team = models.CharField(
        max_length=200,
        blank=True
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    notes = models.TextField(
        blank=True
    )

    class Meta:
        unique_together = (
            'scout',
            'player_id'
        )

    def __str__(self):

        return self.player_name


# =========================================================
# PLAYER NOTES
# =========================================================

class PlayerNote(models.Model):

    scout = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    player_id = models.IntegerField()

    note = models.TextField()

    rating = models.IntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return f'Note for player {self.player_id}'


# =========================================================
# USER PROFILE
# =========================================================

class Profile(models.Model):

    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE
    )

    ROLE_CHOICES = [
        ('scout', 'Scout'),
        ('analyst', 'Analyst'),
        ('head_scout', 'Head Scout'),
        ('manager', 'Manager'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='scout'
    )

    assigned_scout = models.ForeignKey(
        'auth.User',
        null=True,
        blank=True,
        related_name='analysts',
        on_delete=models.SET_NULL
    )

    bio = models.TextField(
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    @property
    def avatar_initials(self):
        if self.user.username:
            initials = self.user.username[:2].upper()
            return initials
        return 'US'

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'


class PlayerApproval(models.Model):

    RECOMMENDATION_CHOICES = [
        ('recommend', 'Recommend'),
        ('reject', 'Reject'),
        ('pending', 'Pending'),
    ]

    DECISION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ]

    player_id = models.IntegerField()
    player_name = models.CharField(max_length=200)
    scout = models.ForeignKey(
        'auth.User',
        related_name='scout_approvals',
        on_delete=models.CASCADE
    )
    analyst = models.ForeignKey(
        'auth.User',
        null=True,
        blank=True,
        related_name='analyst_approvals',
        on_delete=models.SET_NULL
    )
    shortlist_entry = models.ForeignKey(
        Shortlist,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    analyst_note = models.TextField(
        blank=True
    )
    analyst_rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0
    )
    analyst_recommendation = models.CharField(
        max_length=10,
        choices=RECOMMENDATION_CHOICES,
        default='pending'
    )
    head_scout_decision = models.CharField(
        max_length=10,
        choices=DECISION_CHOICES,
        default='pending'
    )
    head_scout_note = models.TextField(
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-updated_at', '-created_at']

    def __str__(self):
        return f'{self.player_name} ({self.scout.username})'


# =========================================================
# ACTIVITY LOG
# =========================================================

class ActivityLog(models.Model):

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    action = models.CharField(
        max_length=255
    )

    detail = models.TextField(
        blank=True
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} — {self.action} at {self.timestamp}"
