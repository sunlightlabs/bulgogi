import requests
import json

from requests.auth import HTTPBasicAuth

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from django.conf import settings


def about(request):
	return render(request, 'foreign/about_foreign.html',)

def methodology(request):
	return render(request, 'foreign/methodology.html',)

def incoming_arms(request):
	if request.GET.get('p'):
		p = int(request.GET.get('p'))
	else:
		p = 1
	url = "/".join([settings.FARA_ENDPOINT, "proposed-arms"])
	response = requests.get(url, params={"p":p, "key":settings.API_PASSWORD})
	data = response.json()
	data = data['results']
	docs = []

	page ={}
	page['this'] = p
	page['previous'] = p - 1
	page['next'] = p + 1
	page['total'] = data['page']['num_pages']

	count = 1
	results = []
	for d in data['proposed_sales']:
		if count % 2 != 0:
			row = "even"
		else:
			row = "odd"

		if d.has_key("date"):
			date = d["date"]
		else:
			print d, "Has no date"
			date =  None


		info ={
			"date": date,
			"id": d["id"],
			"title": d["title"],
			"row": row,
		}


		results.append(info)
		count += 1

	return render(request, 'foreign/incoming_arms.html', {"results":results, "page":page})

def arms_profile(request, doc_id):
	# need to build this
	url = "/".join([settings.FARA_ENDPOINT, "proposed-arms"])
	## problem
	response = requests.get(url, params={"doc_id":doc_id, "key":settings.API_PASSWORD})
	data = response.json()
	if data.has_key('date'):
		date = data['date']
	else:
		date = None
	results={
		'doc_id': doc_id,
		'title': data['title'],
		'date': date,
		'location': data['location'],
		'pdf_url': data['pdf_url'],
	}

	if data.has_key('location_id'):
		results['location_id'] = data['location_id']

	return render(request, 'foreign/arms_profile.html', results)



def incoming_fara(request):
	if request.GET.get('p'):
		p = int(request.GET.get('p'))
	else:
		p = 1
	url = "/".join([settings.FARA_ENDPOINT, "docs"])
	response = requests.get(url, params={"p":p,"key":settings.API_PASSWORD})
	data = response.json()
	page = {}
	page['this'] = p
	page['previous'] = p - 1
	page['next'] = p + 1
	page['total'] = data['page']['num_pages']

	table_info = make_doc_table(data, p)

	return render(request, 'foreign/incoming_fara.html', {"table_info":table_info, 'page':page})

def form_profile(request, form_id):
	url = "/".join([settings.FARA_ENDPOINT, "doc-profile", form_id])
	response = requests.get(url, params={"doc_id":form_id, "key":settings.API_PASSWORD})
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

	totals = {}
	if data.has_key('total_contribution'):
		totals['total_contribution'] = data['total_contribution']
	if data.has_key('total_contact'):
		totals['total_contact'] = data['total_contact']
	if data.has_key('total_payment'):
		totals['total_payment'] = data['total_payment']
	if data.has_key('total_disbursement'):
		totals['total_disbursement'] = data['total_disbursement']
	if data.has_key('amended'):
		amended = True
	else:
		amended = False

	client_list = []
	count = 1
	if data.has_key('clients'):
		for client in data['clients']:
			client_dict = {}
			# I like the look of the chart this way
			if count % 2 != 0:
				row = "even"
			else:
				row = "odd"
			count = count + 1
			client_dict = {"client_id": client["client_id"],
							"client_name": client["client_name"],
							"row": row,
							"location": client["location"],
							"location_id": client["location_id"],
			}
			if client.has_key("payment"):
				client_dict["payment"] = int(client["payment"])
			if client.has_key("contact"):
				client_dict["contact"] = int(client["contact"])
			if client.has_key("disbursement"):
				client_dict["disbursement"] = int(client["disbursement"])

			client_list.append(client_dict)
	if data.has_key('terminated_clients'):
		terminated_list = []
		for client in data['terminated_clients']:
			client_dict = {}
			# I like the look of the chart this way
			if count % 2 != 0:
				row = "even"
			else:
				row = "odd"
			count = count + 1
			client_id = client["client_id"]
			client_name = client["client_name"]


			client_dict = {"client_id": client_id,
							"client_name": client_name,
							"row": row,
							"location": client["location"],
							"location_id": client["location_id"],
			}
			if client.has_key("payment"):
				client_dict["payment"] = int(client["payment"])
			if client.has_key("contact"):
				client_dict["contact"] = int(client["contact"])
			if client.has_key("disbursement"):
				client_dict["disbursement"] = int(client["disbursement"])
			terminated_list.append(client_dict)

	download = 'http://fara.sunlightfoundation.com.s3.amazonaws.com/spreadsheets/forms/form_' + form_id + '.zip'
	r = requests.head(download)
	if r.status_code == requests.codes.ok:
		download = download
	else:
		download = None

	r = requests.head(source_url)
	if r.status_code == requests.codes.ok:
		source_url = download
	else:
		source_url = None

	return render(request, 'foreign/form_profile.html', {
			"source_url": source_url,
			"stamp_date": stamp_date,
			"doc_type": doc_type,
			"registrant": registrant,
			"view_doc_url": view_doc_url,
			"clients": client_list,
			"terminated_clients": terminated_list,
			"processed": processed,
			"download": download,
			"reg_id": reg_id,
			"doc_id": form_id,
			"totals": totals,
			"amended": amended,
		})

def client_profile(request, client_id):
	url = "/".join([settings.FARA_ENDPOINT, "client-profile", client_id])
	response = requests.get(url, params={"key":settings.API_PASSWORD})
	data = response.json()
	data = data['results']

	results = {}
	results['client'] = data['client_name']
	results['client_id'] = client_id
	results['location'] = data['location']
	results['location_id'] = data['location_id']

	if data.has_key('running_total_13'):
		results['running_total_13'] = data['running_total_13']
	if data.has_key('total_payment'):
		results['total_payment'] = data['total_payment']
	if data.has_key('contacts'):
		results['contacts'] = data['contacts']
	if data.has_key('total_disbursement'):
		results['total_disbursement'] = data['total_disbursement']
	if data.has_key('description'):
		results['description'] = data['description']
	if data.has_key('client_type'):
		results['client_type'] = data['client_type']

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
	url = "/".join([settings.FARA_ENDPOINT, "reg-profile", reg_id])
	response = requests.get(url, params={"key":settings.API_PASSWORD})
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

	if data['registrant'].has_key('payments2013'):
		results['payments2013'] = data['registrant']['payments2013']

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
			if c.has_key('disbursement'):
				client['disbursement'] = c['disbursement']

			clients.append(client)
		for c in data['terminated_clients']:
			if c.has_key('contact') or c.has_key('payment') or c.has_key('disbursement'):
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
		p = int(request.GET.get('p'))
	else:
		p = 1
	url = "/".join([settings.FARA_ENDPOINT, "docs"])
	response = requests.get(url, params={"p":p,"key":settings.API_PASSWORD,"reg_id":reg_id, "doc_type":"all", "all_records":"True"})
	data = response.json()

	table_info = make_doc_table(data, p)

	page = {}
	page['this'] = p
	page['previous'] = p - 1
	page['next'] = p + 1
	page['total'] = data['page']['num_pages']

	return render(request, 'foreign/reg_profile.html', {"results":results, "table_info":table_info, 'page':page})

def location_profile(request, location_id):
	url = "/".join([settings.FARA_ENDPOINT, "place-profile", location_id])
	response = requests.get(url, params={"key":settings.API_PASSWORD})
	data = response.json()
	data = data['results']
	results = {}
	results['location'] = data['location_name']
	results['location_id'] = location_id
	if data.has_key('location_contacts'):
		results['location_contacts'] = data['location_contacts']
	if data.has_key('location_payments'):
		results['location_payments'] = data['location_payments']
	if data.has_key('location_disbursements'):
		results['location_disbursements'] = data['location_disbursements']

	if data.has_key('clients'):
		results['clients'] = data['clients']

		location_id
	url = "/".join([settings.FARA_ENDPOINT, "proposed-arms"])
	response = requests.get(url, params={"key":settings.API_PASSWORD, 'location_id':location_id})
	data = response.json()
	results['proposed_sales'] = data['results']['proposed_sales']

	return render(request, 'foreign/location_profile.html', {"results":results})

def recipient_profile(request, recip_id):
	url = "/".join([settings.FARA_ENDPOINT, "recipient-profile", recip_id])
	response = requests.get(url, params={"key":settings.API_PASSWORD})
	data = response.json()
	r = data['results']

	# Congressional results include staff and leadership PACs
	if len(r) > 1 or r[0]['agency'] == 'Congress':
		results = {}
		results["congress_member"] = True
		bioguide_id = r[0]['bioguide_id']
		results['bioguide'] = bioguide_id
		records = []
		for entity in data['results']:
			records.append(entity)
			if entity['agency'] == "Congress":
				results['name'] = entity['name']
				results['title'] = entity['title']
		results['records'] = records

		url = "/".join(["http://congress.api.sunlightfoundation.com", "committees"])
		response = requests.get(url, params={"apikey":settings.CONGRESS_PASSWORD, "member_ids":bioguide_id})
		committee_data = response.json()
		#### still need to do some check for multiple pages of results?
		results["committee_data"] = committee_data["results"]

		ie_profile = 'http://influenceexplorer.com/bioguide/' + bioguide_id
		r = requests.head(ie_profile)
		print r.status_code
		if r.status_code == 302:
			results['ie_profile'] = ie_profile

	else:
		results = data['results'][0]

	results['recipient_id'] = recip_id

	return render(request, 'foreign/recipient_profile.html', {"results":results})


### add agency profile

### tables
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
	url = "/".join([settings.FARA_ENDPOINT, "contact-table"])
	query_params = {}
	query_params['key'] = settings.API_PASSWORD

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
		p = int(request.GET.get('p'))
		query_params['p'] = p
	else:
		p = 1

	response = requests.get(url, params=query_params)
	data = response.json()

	page ={}
	page['this'] = p
	page['previous'] = p - 1
	page['next'] = p + 1
	page['total'] = data['page']['num_pages']
	url_param = ''
	for key in query_params.keys():
		if key != "key" and key != "p":
			query = str(key) + "=" + str(query_params[key]) + "&"
			url_param = url_param + query
	page['query_params'] = url_param

	return render(request, 'foreign/contact_table.html', {"title":data['title'], "page":page, "contacts":data['results'], "buttons":data['buttons']})

def payment_table(request):
	url = "/".join([settings.FARA_ENDPOINT, "payment-table"])
	query_params = {}
	query_params['key'] = settings.API_PASSWORD

	if request.GET.get('reg_id'):
		query_params['reg_id'] = request.GET.get('reg_id')

	if request.GET.get('doc_id'):
		query_params['doc_id'] = request.GET.get('doc_id')

	if request.GET.get('client_id'):
		query_params['client_id'] = request.GET.get('client_id')

	if request.GET.get('payment_id'):
		query_params['payment_id'] = request.GET.get('payment_id')

	if request.GET.get('location_id'):
		query_params['location_id'] = request.GET.get('location_id')

	if request.GET.get('p'):
		page = int(request.GET.get('p'))
		p = int(request.GET.get('p'))
		query_params['p'] = p
	else:
		p = 1

	response = requests.get(url, params=query_params)
	data = response.json()

	page ={}
	page['this'] = p
	page['previous'] = p - 1
	page['next'] = p + 1
	page['total'] = data['page']['num_pages']
	url_param = ''
	for key in query_params.keys():
		if key != "key" and key != "p":
			query = str(key) + "=" + str(query_params[key]) + "&"
			url_param = url_param + query
	page['query_params'] = url_param

	return render(request, 'foreign/payment_table.html', {"title":data['title'], "page":page, "buttons":data['buttons'], "payments":data['results']})

def disbursement_table(request):
	url = "/".join([settings.FARA_ENDPOINT, "disbursement-table"])
	query_params = {}
	query_params['key'] = settings.API_PASSWORD

	if request.GET.get('disbursement_id'):
		query_params['disbursement_id'] = request.GET.get('disbursement_id')

	if request.GET.get('reg_id'):
		query_params['reg_id'] = request.GET.get('reg_id')

	if request.GET.get('doc_id'):
		query_params['doc_id'] = request.GET.get('doc_id')

	if request.GET.get('client_id'):
		query_params['client_id'] = request.GET.get('client_id')

	if request.GET.get('location_id'):
		query_params['location_id'] = request.GET.get('location_id')

	if request.GET.get('p'):
		page = int(request.GET.get('p'))
		p = int(request.GET.get('p'))
		query_params['p'] = p
	else:
		p = 1

	response = requests.get(url, params=query_params)
	data = response.json()

	page ={}
	page['this'] = p
	page['previous'] = p - 1
	page['next'] = p + 1
	page['total'] = data['page']['num_pages']
	url_param = ''
	for key in query_params.keys():
		if key != "key" and key != "p":
			query = str(key) + "=" + str(query_params[key]) + "&"
			url_param = url_param + query
	page['query_params'] = url_param

	return render(request, 'foreign/disbursement_table.html', {"title":data['title'], "page":page, "buttons":data['buttons'], "disbursements":data['results']})


def contribution_table(request):
	url = "/".join([settings.FARA_ENDPOINT, "contribution-table"])
	query_params = {}
	query_params['key'] = settings.API_PASSWORD
	if request.GET.get('contribution_id'):
		query_params['contribution_id'] = request.GET.get('contribution_id')

	if request.GET.get('reg_id'):
		query_params['reg_id'] = request.GET.get('reg_id')

	if request.GET.get('doc_id'):
		query_params['doc_id'] = request.GET.get('doc_id')

	if request.GET.get('recipient_id'):
		query_params['recipient_id'] = request.GET.get('recipient_id')

	if request.GET.get('recipient'):
		query_params['recipient'] = request.GET.get('recipient')

	if request.GET.get('date'):
		query_params['date'] = request.GET.get('date')

	if request.GET.get('amount'):
		query_params['amount'] = request.GET.get('amount')

	if request.GET.get('registrant'):
		query_params['registrant'] = request.GET.get('registrant')

	if request.GET.get('p'):
		page = int(request.GET.get('p'))
		p = int(request.GET.get('p'))
		query_params['p'] = p
	else:
		p = 1

	response = requests.get(url, params=query_params)
	data = response.json()

	page ={}
	page['this'] = p
	page['previous'] = p - 1
	page['next'] = p + 1
	page['total'] = data['page']['num_pages']

	url_param = ''
	for key in query_params.keys():
		if key != "key" and key != "p":
			query = str(key) + "=" + str(query_params[key]) + "&"
			url_param = url_param + query
	page['query_params'] = url_param

	return render(request, 'foreign/contribution_table.html', {"title":data['title'], "page":page,"buttons":data['buttons'], "contributions":data['results']})

def reg_totals13(request):
	url = "/".join([settings.FARA_ENDPOINT, "reg-2013"])
	query_params = {}
	query_params['key'] = settings.API_PASSWORD
	response = requests.get(url, params=query_params)
	data = response.json()

	return render(request, 'foreign/registrants_2013.html', {"data":data['results']})

# Converts the original url to the sunlight url
def http_link(link):
	link = "http://fara.sunlightfoundation.com.s3.amazonaws.com/html/" + link[25:-4] + "/index.html"
	return link

def clients(request):
	url = "/".join([settings.FARA_ENDPOINT, "locations"])
	query_params = {}
	query_params['key'] = settings.API_PASSWORD
	response = requests.get(url, params=query_params)
	data = response.json()

	return render(request, 'foreign/client_list.html', {"data":data['results']})

def search(request):
	url = "/".join([settings.FARA_ENDPOINT, "search"])
	# url = "/".join([settings.FARA_ENDPOINT, "search"])
	query_params = {}
	if request.GET.get('q'):
		q = request.GET.get('q')
		query_params['q'] = q

	else:
		return render(request, 'foreign/search_results.html', {"results":None})

	query_params['key'] = settings.API_PASSWORD
	response = requests.get(url, params=query_params)
	try:
		results = response.json()
	except:
		return render(request, 'foreign/search_results.html', {"results":None})

	data = {}
	if results['clients']['hits']['hits']:
		c = []
		for r in results['clients']['hits']['hits']:
			c.append({'id':r['_id'], 'info':r['_source']})
		data['clients'] = c


	if results['registrants']['hits']['hits']:
		reg = []
		for r in results['registrants']['hits']['hits']:
			reg.append({'id':r['_id'], 'info':r['_source']})
		data['registrants'] = reg

	if results['people_org']['hits']['hits']:
		p = []
		for r in results['people_org']['hits']['hits']:
			p.append({'id':r['_id'], 'info':r['_source']})
		data['people_org'] = p

	if results['arms']['hits']['hits']:
		a = []
		for r in results['arms']['hits']['hits']:
			a.append({'id':r['_id'], 'info':r['_source']})
		data['arms'] = a

	if results['interactions']['hits']['hits']:
		i = []
		for r in results['interactions']['hits']['hits']:
			i.append({'id':r['_id'], 'info':r['_source']})
		data['interactions'] = i


	if results['locations']['hits']['hits']:
		l = []
		for r in results['locations']['hits']['hits']:
			l.append({'id':r['_id'], 'info':r['_source']})
		data['locations'] = l

	if results['docs']['hits']['hits']:
		d = []
		for r in results['docs']['hits']['hits']:
			d.append({'id':r['_id'], 'info':r['_source']})
		data['docs'] = d

	return render(request, 'foreign/search_results.html', {"results":data, 'q':q})



