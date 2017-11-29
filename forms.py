from django import forms
from filter.models import camera
from django.core.exceptions import ValidationError

def validateCSV(value):
	if not value.name.endswith('.csv'):
		if not value.name.endswith('.CSV'):
			raise ValidationError(u'Error! Please use .csv files only!')
def validateZIP(value):
	if not value.name.endswith('.zip'):
		if not value.name.endswith('.ZIP'):
			raise ValidationError(u'Error! Please use .zip files only!')

class editForm(forms.ModelForm):
	class Meta:
		model = camera
		fields = ('caseID','latitude','longitude','priorityIndex','numFloors','floorArea_m2','totalFloorArea_m2','photo')

class newForm(forms.ModelForm):
	class Meta:
		model = camera
		fields = ('caseID','latitude','longitude','priorityIndex','numFloors','floorArea_m2','totalFloorArea_m2','photo')

class uploadCSVForm(forms.Form):
	csvFile = forms.FileField(required=False,label="Upload and Combine CSV File Here",validators=[validateCSV])
	imageFiles = forms.FileField(required=False,label="Upload ZIP Here", validators=[validateZIP])
