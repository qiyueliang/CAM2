from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from filter.models import camera
from filter.forms import editForm, newForm, uploadCSVForm
from datetime import datetime
import os, zipfile, csv,sys

# Create your views here.
def filter(request):
	#Establishing filter constraints
	pImin = 0;
	pImax = 99;
	priorityIndexRange = (pImin,pImax)
	latmin = -90;
	latmax = 90;
	latitudeRange = (latmin,latmax)
	longmin = -180;
	longmax = 180;
	longitudeRange = (longmin,longmax)
	numFloorsmin=0
	numFloorsmax=1000
	numFloorsRange = (numFloorsmin,numFloorsmax)	
	floorAreamin=0
	floorAreamax=9999999
	floorArea_m2Range = (floorAreamin,floorAreamax)
	totalFloorAreamin = 0
	totalFloorAreamax = 9999999
	totalFloorArea_m2Range = (totalFloorAreamin,totalFloorAreamax)

	querysets=camera.objects.filter(latitude__range=latitudeRange, longitude__range=longitudeRange, priorityIndex__range=priorityIndexRange, numFloors__range=numFloorsRange, floorArea_m2__range=floorArea_m2Range, totalFloorArea_m2__range=totalFloorArea_m2Range).order_by("caseID")
	columnHeaders = camera._meta.get_fields()
	columnHeaders = list(map(str,columnHeaders))
	columnHeaders = ['{0}'.format(columnHeader.split('.')[2]) for columnHeader in columnHeaders]
	#columnHeaders.pop(0) #do not allow filtering by primary key (which is 'id' column in database)
	columnHeaders = columnHeaders[2:-3] #do not allow filtering by lastModifiedUser or lastModifiedDate (can be added later)
	if(request.POST.get('filter')):
		min1 = request.POST.get('min1');
		max1 = request.POST.get('max1');
		var1 = request.POST.get('filter1');
		exec(var1+'min'+"=min1")
		exec(var1+'max'+"=max1")
		exec(var1+'Range'+"= (eval(var1+'min'),eval(var1+'max'))")

		min2 = request.POST.get('min2');
		max2 = request.POST.get('max2');
		var2 = request.POST.get('filter2');
		exec(var2+'min'+"=min2")
		exec(var2+'max'+"=max2")
		exec(var2+'Range'+"= (eval(var2+'min'),eval(var2+'max'))")
    
		min3 = request.POST.get('min3');
		max3 = request.POST.get('max3');
		var3 = request.POST.get('filter3');
		exec(var3+'min'+"=min3")
		exec(var3+'max'+"=max3")
		exec(var3+'Range'+"= (eval(var3+'min'),eval(var3+'max'))")

		querysets=camera.objects.filter(latitude__range=latitudeRange, longitude__range=longitudeRange, priorityIndex__range=priorityIndexRange, numFloors__range=numFloorsRange, floorArea_m2__range=floorArea_m2Range, totalFloorArea_m2__range=totalFloorArea_m2Range).order_by("caseID")
	
	if(request.POST.get('search')):
		keyword = request.POST.get('caseID');
		querysets=camera.objects.filter(caseID__exact=keyword);
	if(request.POST.get('search1')):
		keyword = request.POST.get('lastModifiedUser');
		querysets=camera.objects.filter(lastModifiedUser__exact=keyword);
	#remember queryset is ordered by caseID -> objects with same caseID are adjacent to each other
	#Removing duplicates to show results by album
	i = 0
	while(i < len(querysets)-1):
		currCaseId = querysets[i].caseID
		if(querysets[i+1].caseID == currCaseId):
			querysets = querysets[:i] + querysets[i+1:] 
		i+=1

	if (request.POST.get('Upload')):
		formCSV = uploadCSVForm(request.POST, request.FILES)
		formCSV1 = uploadCSVForm(request.POST, request.FILES)
		if formCSV.is_valid() and formCSV1.is_valid():
			parseCSVs(request.FILES.get('myfiles'))
			parseZIP(request.FILES.get('imageFiles'))
			#unZipAndStore(request) #Handle uploaded files
			return HttpResponseRedirect('/filter/')
	else:
		formCSV = uploadCSVForm()

	return render(request, 'filterIndex.html', {'querysets':querysets,'columnHeaders':columnHeaders, 'CSVform':formCSV})
#upload multiple csvs

#Form to edit image
def editImage(request, pk):
	tempCaseID = camera.objects.get(id=pk).caseID
	image = get_object_or_404(camera, pk=pk)
	if request.method == 'POST':
		formEdit = editForm(request.POST, request.FILES,instance=image)
		if formEdit.is_valid():
			image = formEdit.save(commit=False)
			image.lastModifiedUser = str(request.user)
			image.lastModifiedDate = datetime.now
			image.save() #Save form to database
			currCaseID = image.caseID
			#rename form to follow image storage guidelines (image name is it's primaryKey)
			for filename in os.listdir("filter/static/images/"+str(currCaseID)+'/'):
				ext = filename.split('.')
				if filename.startswith(pk+'_'):
					os.rename('filter/static/images/'+str(currCaseID)+'/'+filename, 'filter/static/images/'+str(currCaseID)+'/'+pk+'.'+ext[1])
					break
			return redirect('filter')	
	else:
		formEdit = editForm(instance=image)
	return render(request, 'filterEdit.html', {'formEdit':formEdit, 'id':pk, 'caseID':tempCaseID,})

def newImage(request):
	if request.method == 'POST':
		formNew = newForm(request.POST, request.FILES)
	else:
		formNew = newForm()
	if formNew.is_valid():
		image = formNew.save(commit=False)
		image.lastModifiedUser = str(request.user)
		image.lastModifiedDate = datetime.now
		image.save()
		currCaseID = image.caseID
		
		#create caseID directory if it doesn't exist		
		if(not os.path.isdir("filter/static/images/"+str(currCaseID)+'/')):
			os.makedirs("filter/static/images/"+str(currCaseID)+'/')

		for filename in os.listdir("filter/static/images/"):
			if filename.startswith("DNE"):
				ext = filename.split('.')
				os.rename('filter/static/images/'+filename, 'filter/static/images/'+str(currCaseID)+'/'+str(image.pk)+'.'+ext[1])
				break
		return redirect('filter')
	return render(request, 'filterEdit.html', {'formEdit':formNew})

def deleteImage(request, pk):
	imageToDelete = camera.objects.get(id=pk)
	deletePhoto(pk)
	imageToDelete.delete()
	return HttpResponseRedirect('/filter/')

def deletePhoto(pk):
	imageToDelete = camera.objects.get(id=pk)
	currCaseID = imageToDelete.caseID
	for filename in os.listdir("filter/static/images/"+str(currCaseID)+'/'):
		if filename.startswith(str(pk)) and '_' not in filename:
			os.remove('filter/static/images/'+str(currCaseID)+'/'+filename)
	dirContents=os.listdir("filter/static/images/"+str(currCaseID)+'/')
	if not dirContents:
		os.rmdir("filter/static/images/"+str(currCaseID)+'/')

def parseCSVs(CSVFile, CSVFile1):
	if CSVFile is None and CSVFILe1 is None:
		return

	with open('filter/static/metadata.csv', 'wb+') as destination:
		for chunk in CSVFile.chunks():
			destination.write(chunk)
	with open('filter/static/metadata1.csv', 'web+') as destination:
		for chunk in CSVFile1.chunks():
			destination.write(chunk)

def parseZIP(ZIPFile):
	if ZIPFile is None:
		return

	with open('filter/static/metadata.zip', 'wb+') as destination:
		for chunk in ZIPFile.chunks():
			destination.write(chunk)

def caseIDView(request,caseID):
	querysets = camera.objects.filter(caseID=caseID)
	return render(request,'filterCaseIDView.html',{'querysets':querysets, 'firstElement':querysets[0],})

def deleteAlbum(request, pk):
	currCaseID = camera.objects.get(id=pk).caseID
	queryset = camera.objects.filter(caseID=currCaseID)
	for query in queryset:
		deletePhoto(query.id) #delete stored file
		query.delete() #delete database entry
	return HttpResponseRedirect('/filter/')

def unZipAndStore(request):
	#Unzip csv files, get the caseID
	zipRef = zipfile.ZipFile("filter/static/metadata.zip",'r')
	zipRef.extractall("filter/static/images/")
	zipRef.close()
	os.remove("filter/static/metadata.zip") #delete zip file as it is not needed anymore

	#Store info in CSV to database
        #'filter/static/metadata.csv' = sys.argv[1]
        
	with open('filter/static/metadata.csv','r') as f:
		#next(f)
		reader = csv.reader(f)		
		rows = list(reader)
		#just to debug
		currCaseID = rows[1]
		#currCaseID = str(rows[1][3])
		currLat = float(rows[1][3])
		currLong = float(rows[2][3])
		currPriorityIdx = float(rows[3][3])
		currNumFloors = float(rows[4][3])
		currFloorArea = float(rows[5][3])   
		currTotalFloorArea = float(rows[6][3])
                
	with open('filter/static/metadata1.csv','r') as	f:
		reader = csv.reader(f)
		rows = list(reader)
			
		#Add the info to a new form, and save it to the database
		newCSVImageForm = newForm()
		newImageForm = newCSVImageForm.save(commit=False)
		newImageForm.caseID = currCaseID
		newImageForm.latitude = currLat
		newImageForm.longitude = currLong
		newImageForm.priorityIndex = currPriorityIdx
		newImageForm.numFloors = currNumFloors
		newImageForm.floorArea_m2 = currFloorArea
		newImageForm.totalFloorArea_m2 = currTotalFloorArea
		newImageForm.lastModifiedUser = str(request.user)
		newImageForm.lastModifiedDate = datetime.now
		newImageForm.save()

	os.remove("filter/static/metadata.csv") #delete csv file as it is not needed anymore

