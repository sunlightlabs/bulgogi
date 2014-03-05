import requests
import json

from requests.auth import HTTPBasicAuth

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from foreign.local_settings import FARA_ENDPOINT, API_USER, API_PASSWORD

def about(request):
	return render(request, 'foreign/about_foreign.html',)

def incoming_arms(request):
	if request.GET.get('p'):
		page = int(request.GET.get('p'))
	else:
		page = 1
	url = "/".join([FARA_ENDPOINT, "proposed-arms"])
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
			"pdf_url": d["pdf_url"],
		}
		results.append(info)
		count += 1

	return render(request, 'foreign/incoming_arms.html', {"results":results, "page":page})

def arms_profile(request, doc_id):
	# need to build this
	url = "/".join([FARA_ENDPOINT, "proposed-arms"])
	response = requests.get(url, auth=(API_USER, API_PASSWORD), params={"doc_id":doc_id})
	data = response.json()

	date = data["date"]
	date = date.split('-')
	date = date[1] + '/' + date[2] + '/' + date[0]

	results={
		'doc_id': doc_id,
		'title': data['title'], 
		'date': date, 
		'location': data['location'], 
		'text': data['text'], 
		'pdf_url': data['pdf_url'],
	}

	if data.has_key('location_id'):
		results['location_id'] = data['location_id']

	return render(request, 'foreign/arms_profile.html', results)

# rewrite for new endpoint
def incoming_fara(request):
	if request.GET.get('p'):
		page = int(request.GET.get('p'))
	else:
		page = 1
	url = "/".join([FARA_ENDPOINT, "docs"])
	response = requests.get(url, params={"p":page,"key":API_PASSWORD})
	data = response.json()
	page = int(page)

	table_info = make_doc_table(data, page)

	return render(request, 'foreign/incoming_fara.html', {"table_info":table_info})

def form_profile(request, form_id):
	url = "/".join([FARA_ENDPOINT, "doc-profile", form_id])
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
			client_dict = {}
			client_name =  client["client_name"]
			location = client["location"]
			location_id = client["location_id"]
			client_id = client["client_id"]
		
			# I like the look of the chart this way
			if count % 2 != 0:
				row = "even"
			else:
				row = "odd"	
			count = count + 1
		
			client_dict = {"client_id":client_id, "client_name":client_name, "row":row, "location":location, "location_id":location_id}

			if client.has_key("payment"):
				client_dict["payment"] = int(client["payment"])
				payment = True			
			if client.has_key("contact"):
				client_dict["contact"] = int(client["contact"])
				contact = True

			client_list.append(client_dict)	

	if "payment" not in locals():
		payment = False
	
	if "contact" not in locals():
		contact = False


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
			"payment": payment,
			"contact": contact,
			"reg_id": reg_id,
			"doc_id": form_id
		})

def client_profile(request, client_id):
	url = "/".join([FARA_ENDPOINT, "client-profile", client_id])
	response = requests.get(url, params={"key":API_PASSWORD})
	data = response.json()
	data = data['results']
	
	results = {}
	results['client'] = data['client_name']
	results['client_id'] = client_id
	results['location'] = data['location']
	results['location_id'] = data['location_id']

	if data.has_key('total_payment'):
		results['total_payment'] = data['total_payment']
	if data.has_key('contacts'):
		results['contacts'] = data['contacts']
	if data.has_key('total_disbursement'):
		results['total_disbursement'] = data['total_disbursement']

	if data.has_key('active_reg'):
		active_reg = []
		for reg in data['active_reg']:
			reg = {'name':reg['name'], 'id':reg['reg_id']}
			active_reg.append(reg)
		results['active_reg'] = active_reg

	if data.has_key('terminated_reg'):
		terminated_reg = []
		for reg in data['terminated_reg']:
			reg= {'name':reg['name'], 'id':reg['reg_id']}
			terminated_reg.append(reg)
		results['terminated_reg'] = terminated_reg

	return render(request, 'foreign/client_profile.html', {"results":results})

def reg_profile(request, reg_id):
	url = "/".join([FARA_ENDPOINT, "reg-profile", reg_id])
	response = requests.get(url, params={"key":API_PASSWORD})
	data = response.json()
	data = data['results']
	results = {}
	results['reg_id'] = reg_id
	if data['registrant'].has_key('name'):
		results['reg_name'] = data['registrant']['name']
	
	if data['registrant'].has_key('total_contributions'):
		results['total_contributions'] = data['registrant']['total_contributions']
	
	if data['registrant'].has_key('total_payments'):
		results['total_payments'] = data['registrant']['total_payments']

	if data['registrant'].has_key('total_disbursements'):
		results['total_disbursements'] = data['registrant']['total_disbursements']

	if data['registrant'].has_key('total_contacts'):
		results['total_contacts'] = data['registrant']['total_contacts']

	if data.has_key('clients'):
		clients = []
		for c in data['clients']:
			client = {}
			client['name'] = c['client_name']
			client['location'] = c['location']
			client['location_id'] = c['location_id']
			client['client_id'] = c['client_id']
			if c.has_key('contact'):
				client['contact'] = c['contact']
			if c.has_key('payment'):
				client['payment'] = c['payment']
			if c.has_key('disbursemant'):
				client['disbursement'] = c['disbursement']
			
			clients.append(client)
		results['clients'] = clients
	
	if data.has_key('terminated_clients'):
		terminated_clients = []
		for c in data['terminated_clients']:
			client = {}
			client['name'] = c['client_name']
			client['location'] = c['location']
			client['location_id'] = c['location_id']
			client['client_id'] = c['client_id']
			if c.has_key('contact'):
				client['contact'] = c['contact']
			if c.has_key('payment'):
				client['payment'] = c['payment']
			if c.has_key('disbursement'):
				client['disbursement'] = c['disbursement']
			
			terminated_clients.append(client)
		results['terminated_clients'] = terminated_clients

	#document table
	if request.GET.get('p'):
		page = int(request.GET.get('p'))
	else:
		page = 1
	url = "/".join([FARA_ENDPOINT, "docs"])
	response = requests.get(url, params={"p":page,"key":API_PASSWORD,"reg_id":reg_id})
	data = response.json()
	page = int(page)

	table_info = make_doc_table(data, page)

	return render(request, 'foreign/reg_profile.html', {"results":results, "table_info":table_info})

def location_profile(request, location_id):
	url = "/".join([FARA_ENDPOINT, "place-profile", location_id])
	response = requests.get(url, params={"key":API_PASSWORD})
	data = response.json()
	data = data['results']
	results = {}
	
	results['location'] = data['location_name']
	results['location_id'] = location_id

	if data.has_key('proposed_sales'):
		results['proposed_sales'] = data['proposed_sales']
		print results['proposed_sales']
	else:
		results['proposed_sales'] = None

	if data.has_key('clients'):
		results['clients'] = data['clients']

	return render(request, 'foreign/location_profile.html', {"results":results})

def make_doc_table(data, page):
	docs = []
	count = 1
	if page != 	1:
		page = {"previous":page-1, "this":page, "next":page+1,}
	else:
		page = {"this":page, "next":page+1}

	for d in data['results']:
		doc_id = str(d["doc_id"])
		doc_type = d["doc_type"]
		processed = d["processed"]
		stamp_date = d["stamp_date"]
		reg_id = d["reg_id"]
		profile_url = "form-profile/" + doc_id
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
	return info

	return render(request, 'foreign/location_profile.html', {"results":results})

def contact_table(request):
	url = "/".join([FARA_ENDPOINT, "contact-table"])
	
	query_params = {}
	query_params['key'] = API_PASSWORD
	if request.GET.get('reg_id'):
		query_params['reg_id'] = request.GET.get('reg_id')
	if request.GET.get('doc_id'):
		query_params['doc_id'] = request.GET.get('doc_id')
	if request.GET.get('client_id'):
		query_params['client_id'] = request.GET.get('client_id')
	if request.GET.get('recipient_id'):
		query_params['recipient_id'] = request.GET.get('recipient_id')
	if request.GET.get('contact_id'):
		query_params['contact_id'] = request.GET.get('contact_id')
	if request.GET.get('location_id'):
		query_params['location_id'] = request.GET.get('location_id')
	if request.GET.get('p'):
		page = int(request.GET.get('p'))
		p = request.GET.get('p')
		query_params['p'] = p
	else:
		p = 1
	page ={}
	page['this'] = p
	page['previous'] = p - 1
	page['next'] = p + 1
	response = requests.get(url, params=query_params)
	data = response.json()

	return render(request, 'foreign/contact_table.html', {"title":data['title'], "page":page, "contacts":data['results']})



# Converts the original url to the sunlight url
def http_link(link):
	link = "http://fara.sunlightfoundation.com.s3.amazonaws.com/html/" + link[25:-4] + "/index.html"
	return link

