from django.db import models

# Create your models here.

class User(models.Model):
    username_db = models.CharField(max_length=200)
    password_db = models.CharField(max_length=200)
    created_date_db = models.DateTimeField('date published')
    def __str__(self):
        return self.username_db
    def was_added_recently(self):
        return self.created_date_db >= timezone.now() - datetime.timedelta(days=1)


# class Password(models.Model):
#     question = models.ForeignKey(Uername, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)
#     def __str__(self):
#         return self.choice_text