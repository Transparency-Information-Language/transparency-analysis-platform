from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

import requests
import json
#test comment
import time
from tqdm import tqdm

sample_transport=RequestsHTTPTransport(
    url='http://localhost:4001/graphql',
    use_json=True,
    headers={
        "Content-type": "application/json",
    },
    verify=False
)

client = Client(
    retries=3,
    transport=sample_transport,
    fetch_schema_from_transport=True,
)


iab_purposes = json.loads(requests.get('https://vendorlist.consensu.org/purposes-de.json').content)

lastUpdated = iab_purposes['lastUpdated']
purposes = iab_purposes['purposes']
features = iab_purposes['features']

for p in tqdm(purposes):
    query_string = 'mutation { CreatePurpose(id: %s, name: "%s", description: "%s") { _id }}' % (p['id'], p['name'], p['description'])
    query = gql(query_string)
    client.execute(query)

for f in tqdm(features):
    query_string = 'mutation { CreateFeature(id: %s, name: "%s", description: "%s") { _id }}' % (p['id'], p['name'], p['description'])
    query = gql(query_string)
    client.execute(query)


iab_global_vendor_list = json.loads(requests.get('https://vendorlist.consensu.org/vendorinfo.json').content)

lastUpdate = iab_global_vendor_list['lastUpdated']
vendors = iab_global_vendor_list['vendors']

for v in tqdm(vendors):
    # Create Controller
    name = v['name'].replace('"', '\\"')
    query_string = 'mutation { CreateController(id: %s, name: "%s") { _id }}' % (v['id'], name)
    query = gql(query_string)
    response = client.execute(query)
    #print(response)

    for a in tqdm(v['AdServers']):
        url = a.replace('"', '\\"')
        # Create AdServers
        query = gql('mutation { CreateAdServer(url: "%s") { _id }}' % (url)) 
        response = client.execute(query)
        #print(response)

        # Link AdServers to Controller
        query = gql('mutation { AddControllerAdServers(from: {id: %s }, to: {url: "%s" }) { to { url } }}' % (v['id'], url)) 
        response = client.execute(query)
        #print(response)
