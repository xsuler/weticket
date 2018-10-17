from django.db import models
import os
import uuid

def rename(instance, filename):
    upload_to = 'static/activity_image/'
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid1().hex, ext)
    return os.path.join(upload_to, filename)

class ActivityImage(models.Model):
    image = models.ImageField(upload_to = rename, default = 'static/activity_image/None/no-img.jpg')
