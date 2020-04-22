from django.contrib import admin
from .models import User, team_name
from django import forms
from django.db import models

# Register your models here.



class team_name_Admin(admin.ModelAdmin):
   def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # if db_field.name == "user_id":
        user = User.objects.get(username=request.user)
        user_team = user.team_name.team
        if not request.user.is_superuser:
            kwargs["queryset"] = team_name.objects.filter(team=user_team)
        else:
        	kwargs["queryset"] = team_name.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
   def get_queryset(self, request):
      qs = super(team_name_Admin, self).get_queryset(request)
      user = User.objects.get(username=request.user)
      user_team = user.team_name.team
      if request.user.is_superuser:
            return qs
      return qs.filter(team=user_team)
   def get_readonly_fields(self, request, obj=None):
        if obj: # editing an existing object
            if request.user.is_superuser:
            	return self.readonly_fields
            else:
                return self.readonly_fields + ('team', 'project')
        return self.readonly_fields
   def save_model(self, request, obj, form, change):
        # if not obj.author.id:
        #     obj.author = request.user
        obj.team = team_name.objects.get(user_id=request.user.id).team
        obj.team = 'aaabbb'
        obj.save()


admin.site.register(team_name,team_name_Admin)


