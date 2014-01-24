import requests
import json

from requests.auth import HTTPBasicAuth

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from foreign.local_settings import FARA_ENDPOINT, API_USER, API_PASSWORD

def incoming_fara(request):
	if request.GET.get('p'):
		page = int(request.GET.get('p'))
	else:
		page = 1
	url = "/".join([FARA_ENDPOINT, "docs"])
	response = requests.get(url, auth=(API_USER, API_PASSWORD), params={"p":page})
	data = response.json()
	docs = []
	page = int(page)
	if page != 	1:
		page = {"previous":page-1, "this":page, "next":page+1,}
	else:
		page = {"this":page, "next":page+1}
	
	count = 1
	for d in data[0]:
		doc_id = str(d["id"])
		doc_type = d["doc_type"]
		processed = d["processed"]
		stamp_date = d["stamp_date"]
		reg_id = d["reg_id"]
		profile_url = "form_profile/" + doc_id
		if count % 2 != 0:
			place = "even"
		else:
			place = "odd"	
		count = count + 1
		url = "/".join([FARA_ENDPOINT, "registrant"])
		response = requests.get(url, auth=(API_USER, API_PASSWORD), params={"reg_id":reg_id})
		data = response.json()
		print data
		reg_name = data["reg_name"]

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
	url = "/".join([FARA_ENDPOINT, "docs"])
	response = requests.get(url, auth=(API_USER, API_PASSWORD), params={"doc_id":form_id})
	data = response.json()
	print data
	source_url = data["url"]
	reg_id = data["reg_id"]
	stamp_date = data["stamp_date"]
	doc_type = data["doc_type"]
	processed = data["processed"]

	url = "/".join([FARA_ENDPOINT, "registrant"])
	response = requests.get(url, auth=(API_USER, API_PASSWORD), params={"reg_id":reg_id})
	data = response.json()
	registrant = data["reg_name"]
	clients = data["clients"]
	view_doc_url= http_link(source_url)

	client_list = []
	count = 1
	for client in clients:
		client_name =  client["client_name"]
		client_id = client["id"]
		# I like the look of the chart this way
		if count % 2 != 0:
			place = "even"
		else:
			place = "odd"	
		count = count + 1
		client_list.append([client_id, client_name, place])

	
	return render(request, 'foreign/form_profile.html', {
			"source_url":source_url,
			"stamp_date":stamp_date,
			"doc_type": doc_type,
			"registrant": registrant,
			"view_doc_url": view_doc_url,
			"clients": client_list,
			"processed": processed,
		})

def http_link(link):
	link = "http://fara.sunlightfoundation.com.s3.amazonaws.com/html/" + link[25:-4] + "/index.html"
	return link


