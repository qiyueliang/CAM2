from django.db import models
from datetime import datetime
from django.core.exceptions import ValidationError

def renameToPrimaryKey(instance, filename):
	ext = filename.split('.')
	if instance.pk:
		currCaseID = camera.objects.get(id=instance.pk).caseID
		return 'filter/static/images/'+str(currCaseID)+'/'+'{}.{}'.format(instance.pk,ext[1].lower())
	else:
		return 'filter/static/images/DNE.' + ext[1].lower()

def validateFile(value):
	if not value.name.endswith('.jpg'):
		if not value.name.endswith('.JPG'):
			raise ValidationError(u'Error! Please use .jpg files only!')

class camera(models.Model):
	caseID = models.CharField(max_length=10) #Some case IDs are longer than 3 digits. Max length of 10 to be safe. Maybe remove this constraint?
	latitude = models.FloatField()
	longitude = models.FloatField()
	priorityIndex = models.FloatField()
	numFloors = models.PositiveIntegerField(default=0)
	floorArea_m2 = models.PositiveIntegerField(default=0)
	totalFloorArea_m2 = models.PositiveIntegerField(default=0)
	lastModifiedUser = models.CharField(max_length=140, default="")
	lastModifiedDate = models.DateTimeField(auto_now=True)
	photo = models.ImageField(upload_to=renameToPrimaryKey, default='static/images/'+str(datetime.now), validators=[validateFile])

	def __str__(self):
		return self.caseID

