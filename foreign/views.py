import requests
import json

from requests.auth import HTTPBasicAuth

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from foreign.local_settings import FARA_ENDPOINT, API_USER, API_PASSWORD

def incoming_arms(request):
	if request.GET.get('p'):
		page = int(request.GET.get('p'))
	else:
		page = 1
	url = "/".join([FARA_ENDPOINT, "proposed_arms"])
	response = requests.get(url, auth=(API_USER, API_PASSWORD), params={"p":page})
	data = response.json()
	docs = []
	
	page = int(page)
	if page != 	1:
		page = {"previous":page-1, "this":page, "next":page+1,}
	else:
		page = {"this":page, "next":page+1}

	count = 1

	results = []
	for d in data['results']:
		if count % 2 != 0:
			row = "even"
		else:
			row = "odd"
		date = d["date"]
		date = date.split('-')
		date = date[1] + '/' + date[2] + '/' + date[0]

		info ={
			"date": date,
			"id": d["id"],
			"title": d["title"],
			"row": row,
			"pdf_url": d["pdf_url"]
		}
		results.append(info)
		count += 1

	return render(request, 'foreign/incoming_arms.html', {"results":results, "page":page})

def arms_profile(request, doc_id):
	# need to build this
	url = "/".join([FARA_ENDPOINT, "proposed_arms"])
	response = requests.get(url, auth=(API_USER, API_PASSWORD), params={"doc_id":doc_id})
	data = response.json()

	results={
		'title': data['title'], 
		'date': data['date'], 
		'location': data['location'], 
		'text': data['text'], 
	}

	return render(request, 'foreign/arms_profile.html', results)

# rewrite for new endpoint
def incoming_fara(request):
	if request.GET.get('p'):
		page = int(request.GET.get('p'))
	else:
		page = 1
	# change to agentfeed
	url = "/".join([FARA_ENDPOINT, "docs"])
	response = requests.get(url, params={"p":page,"key":API_PASSWORD})
	data = response.json()
	docs = []
	
	page = int(page)
	if page != 	1:
		page = {"previous":page-1, "this":page, "next":page+1,}
	else:
		page = {"this":page, "next":page+1}
	
	count = 1
	for d in data['results']:
		doc_id = str(d["doc_id"])
		doc_type = d["doc_type"]
		processed = d["processed"]
		stamp_date = d["stamp_date"]
		reg_id = d["reg_id"]
		profile_url = "form_profile/" + doc_id
		if d.has_key("reg_name"):
			reg_name = d["reg_name"]
		else:
			reg_name = ''

		if count % 2 != 0:
			place = "even"
		else:
			place = "odd"	
		count = count + 1

		docs.append({
			"reg_name": reg_name,
			"doc_id": doc_id,
			"doc_type": doc_type,
			"processed": processed,
			"stamp_date": stamp_date,
			"profile_url": profile_url,
			"place": place,
		})
		


	info = [{"page": page}, docs]	
	return render(request, 'foreign/incoming_fara.html', {"info":info})

def fara_profile(request, form_id):
	url = "/".join([FARA_ENDPOINT, "doc_profile", form_id])
	response = requests.get(url, params={"doc_id":form_id, "key":API_PASSWORD})
	data = response.json()
	data = data['results']

	source_url = data["url"]
	reg_id = data["reg_id"]
	stamp_date = data["stamp_date"]
	doc_type = data["doc_type"]
	processed = data["processed"]
	view_doc_url= http_link(source_url)

	if data.has_key('reg_name'):
		registrant = data["reg_name"]
	else:
		registrant = None

	client_list = []
	count = 1
	if data.has_key('clients'):
		for client in data['clients']:
			client_name =  client["client_name"]
			location = client["location"]
			client_id = client["client_id"]
		
			# I like the look of the chart this way
			if count % 2 != 0:
				row = "even"
			else:
				row = "odd"	
			count = count + 1
		
			client_list.append([client_id, client_name, row, location])
	

	download = 'http://fara.sunlightfoundation.com.s3.amazonaws.com/spreadsheets/forms/form_' + form_id + '.zip'
	r = requests.head(download)
	if r.status_code == requests.codes.ok:
		download = download
	else:
		download = None
	
	return render(request, 'foreign/form_profile.html', {
			"source_url": source_url,
			"stamp_date": stamp_date,
			"doc_type": doc_type,
			"registrant": registrant,
			"view_doc_url": view_doc_url,
			"clients": client_list,
			"processed": processed,
			"download": download,
		})

# I font think I am using this
def http_link(link):
	link = "http://fara.sunlightfoundation.com.s3.amazonaws.com/html/" + link[25:-4] + "/index.html"
	return link


