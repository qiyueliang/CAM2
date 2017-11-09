# CAM2
Current stage: try to upload multiple csv files</br>
Next step:successfuly match up case id, extract all the metadata(from the two csv files uploaded) correspond to the case id

The following are directly related codes:</br>
filterIndex.html(mysite/filter/templates) controlls upload button and upload request on the webpage</br>
views.py(mysite/filter) controlls unzip function and can access the csv file, it provides an upload function that is cited in the html code
