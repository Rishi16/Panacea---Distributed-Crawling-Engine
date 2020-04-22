from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

# Create your models here.



class team_name(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.CharField(max_length=100, blank=True)
    project = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return str(self.user)
        # return str(team_name.objects.get(team='Lazada'))

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        team_name.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.team_name.save()

# class Document(models.Model):
#     description = models.CharField(max_length=255, blank=True)
#     document = models.FileField(upload_to='documents/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)

SCRIPT_CHOICES = (
    ('lazada_ph','Lazada_PH'),
    ('lazada_sg', 'Lazada_SG'),
    ('farnell_prod','Farnell_Prod'),
    ('sample','Sample'),
)

REGION_CHOICES = (
    ('ph','Philippines'),
    ('SG', 'Singapore'),
    ('UK','United Kingdom'),
    ('DE','Germany'),
)

class db_script(models.Model):
    user_id = models.CharField(max_length=100, blank=True, unique=False)
    team = models.CharField(max_length=100, blank=True)
    supplier_name = models.CharField(max_length=100, blank=True)
    script_file = models.FileField(upload_to='crawl/script_file/%m%d%y')
    proxy_file = models.FileField(upload_to='crawl/proxy_file/%m%d%y')
    servers = models.CharField(max_length=100, blank=True)
    timeout = models.CharField(max_length=100, blank=True)
    attempt = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return str(self.supplier_name)
    # proxies_file_name = models.CharField(max_length=100, blank=True)
    # server_file_name = models.CharField(max_length=100, blank=True)

class db_batch(models.Model):
    user_id = models.CharField(max_length=100, blank=True, unique=False)
    team = models.CharField(max_length=100, blank=True)
    batch_name = models.CharField(max_length=100, blank=True)
    input_file = models.FileField(upload_to='crawl/input_file/%m%d%y')
    # script_name = models.CharField(max_length=100, blank=True, choices=SCRIPT_CHOICES)
    script_name = models.ForeignKey(db_script, on_delete=models.CASCADE)
    # proxies_file_name = models.CharField(max_length=100, blank=True)
    # server_file_name = models.CharField(max_length=100, blank=True)
    # region = models.CharField(max_length=100, blank=True, choices=REGION_CHOICES)
    creation_date = models.DateTimeField(blank=True, null=True)
    scheduled_date = models.DateField("date", default=datetime.datetime.now().strftime("%d-%m-%Y"))
    scheduled_time = models.TimeField("time", default=datetime.datetime.now().time())
    status = models.CharField(max_length=100, blank=False, default='notstarted')
    input_count = models.BigIntegerField(default=0)
    completion = models.BigIntegerField(default=0)
    completion_found = models.BigIntegerField(default=0)
    completion_pnf = models.BigIntegerField(default=0)
    completion_tag_failed = models.BigIntegerField(default=0)
    completion_proxy_blocked = models.BigIntegerField(default=0)
    completion_other = models.BigIntegerField(default=0)



# class script_upload(models.Model):
#     team = models.CharField(max_length=100, blank=True)
#     team = models.CharField(max_length=100, blank=True)
#     project = models.CharField(max_length=100, blank=True)
#     def __str__(self):
#     	return str(self.user)

# class User(models.Model):
#     username_db = models.CharField(max_length=200)
#     password_db = models.CharField(max_length=200)
#     created_date_db = models.DateTimeField('date published')
#     def __str__(self):
#         return self.username_db
#     def was_added_recently(self):
#         return self.created_date_db >= timezone.now() - datetime.timedelta(days=1)


# class Password(models.Model):
#     question = models.ForeignKey(Uername, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
#     def __str__(self):
#         return self.choice_text