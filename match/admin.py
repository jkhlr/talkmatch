from django.contrib import admin

from match.models import Participant, Group, Match

admin.site.register(Group)
admin.site.register(Participant)
admin.site.register(Match)

