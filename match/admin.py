from django.contrib import admin
from django_object_actions import DjangoObjectActions

from match.controller import match, goodbye
from match.models import Participant, Group, Match

# admin.site.register(Group)
admin.site.register(Participant)
admin.site.register(Match)


@admin.register(Group)
class GroupAdmin(DjangoObjectActions, admin.ModelAdmin):
    def match(self, request, obj):
        match(obj)

    def goodbye(self, request, obj):
        goodbye(obj)

    change_actions = ('match', 'goodbye')

    def get_change_actions(self, request, object_id, form_url):
        obj = self.model.objects.get(pk=object_id)
        actions = list(self.change_actions)
        if obj.matched:
            actions.remove('match')
        if obj.goodbye_sent:
            actions.remove('goodbye')
        return actions

