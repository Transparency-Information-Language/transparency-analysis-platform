from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# from rich.console import Console

import requests
import json

import time
from tqdm import tqdm

# console = Console()

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

iab_global_vendor_list = json.loads(requests.get('https://vendorlist.consensu.org/v2/vendor-list.json').content)

lastUpdate = iab_global_vendor_list['lastUpdated']
print(("Retrieved global vendor list with last update: %s") % str(lastUpdate))


purposes = iab_global_vendor_list['purposes']

print('Purposes:')

for i in tqdm(range(1, len(purposes) + 1)):
    p = purposes['%s' % (i)]
    description = p['description'].replace('"', '\\"').replace(':', '\:"')
    descriptionLegal = p['descriptionLegal'].replace('"', '\\"').replace('\n', '')
    query_string = 'mutation { CreatePurpose(id: %s, name: "%s", description: "%s", descriptionLegal: "%s") { _id }}' % (p['id'], p['name'], description, descriptionLegal)
    query = gql(query_string)
    client.execute(query)
    i = i + 1

specialPurposes = iab_global_vendor_list['specialPurposes']
print('SpecialPurposes:')
for i in tqdm(range(1, len(specialPurposes) + 1)):
    p = purposes['%s' % (i)]
    description = p['description'].replace('"', '\\"').replace(':', '\:"')
    descriptionLegal = p['descriptionLegal'].replace('"', '\\"').replace('\n', '')
    query_string = 'mutation { CreateSpecialPurpose(id: %s, name: "%s", description: "%s", descriptionLegal: "%s") { _id }}' % (p['id'], p['name'], description, descriptionLegal)
    query = gql(query_string)
    client.execute(query)
    i = i + 1

features = iab_global_vendor_list['features']
print('Features:')
for i in tqdm(range(1, len(features) + 1)):
    f = features['%s' % (i)]
    description = f['description'].replace('"', '\\"').replace(':', '\:"')
    descriptionLegal = f['descriptionLegal'].replace('"', '\\"').replace('\n', '')
    query_string = 'mutation { CreateFeature(id: %s, name: "%s", description: "%s", descriptionLegal: "%s") { _id }}' % (f['id'], f['name'], description, descriptionLegal)
    query = gql(query_string)
    client.execute(query)
    i = i + 1

specialFeatures = iab_global_vendor_list['specialFeatures']
print('SpecialFeatures:')
for i in tqdm(range(1, len(specialFeatures) + 1)):
    f = features['%s' % (i)]
    description = f['description'].replace('"', '\\"').replace(':', '\:"')
    descriptionLegal = f['descriptionLegal'].replace('"', '\\"').replace('\n', '')
    query_string = 'mutation { CreateSpecialFeature(id: %s, name: "%s", description: "%s", descriptionLegal: "%s") { _id }}' % (f['id'], f['name'], description, descriptionLegal)
    query = gql(query_string)
    client.execute(query)
    i = i + 1

stacks = iab_global_vendor_list['stacks']
print('Stacks:')
for i in tqdm(range(1, len(stacks) + 1)):
    s = stacks['%s' % (i)]
    description = s['description'].replace('"', '\\"').replace(':', '\:"')
    query_string = 'mutation { CreateStack(id: %s, name: "%s", description: "%s") { _id }}' % (s['id'], s['name'], description)
    query = gql(query_string)
    client.execute(query)

    for p in tqdm(s['purposes']):
        # Link Purposes to Stack
        query = gql('mutation {AddStackPurposes(from: {id: %s}, to: {id: %s}) {from{id}, to{id}}}' % (s['id'], p)) 
        response = client.execute(query)

    for p in tqdm(s['specialFeatures']):
        # Link SpecialFeatures to Stack
        query = gql('mutation {AddStackSpecialFeatures(from: {id: %s}, to: {id: %s}) {from{id}, to{id}}}' % (s['id'], p)) 
        response = client.execute(query)

    i = i + 1

vendors = iab_global_vendor_list['vendors']
vendors_not_exist = []
# print('Vendors:')
# print(vendors)
print('---')
#for i in tqdm(range(1, len(vendors) + 1)):
for vendor in tqdm(vendors):    
    try:
        v = vendors['%s' % (vendor)]
        
        print(v)

        policy = v['policyUrl']
        query_string = 'mutation { CreateController(id: %s, name: "%s", privacyPolicy: "%s") { _id }}' % (v['id'], v['name'], policy)
        query = gql(query_string)
        client.execute(query)

        status = 'vendor'

        for p in tqdm(v['purposes']):
            status = 'purposes'
            query = gql('mutation { AddControllerPurposes(from: {id: %s}, to: {id: %s}) {from{id}, to{id}}}' % (v['id'], p))
            response = client.execute(query)

        for p in tqdm(v['legIntPurposes']):
            status = 'legIntPurposes'
            query = gql('mutation { AddControllerPurposesNonConsentable(from: {id: %s}, to: {id: %s}) {from{id}, to{id}}}' % (v['id'], p))
            response = client.execute(query)

        for p in tqdm(v['flexiblePurposes']):
            status = 'flexiblePurposes'
            query = gql('mutation { AddControllerPurposesFlexible(from: {id: %s}, to: {id: %s}) {from{id}, to{id}}}' % (v['id'], p))
            response = client.execute(query)

        for p in tqdm(v['specialPurposes']):
            status = 'specialPurposes'
            query = gql('mutation { AddControllerPurposesSpecial(from: {id: %s}, to: {id: %s}) {from{id}, to{id}}}' % (v['id'], p))
            response = client.execute(query)

        for p in tqdm(v['features']):
            status = 'features'
            query = gql('mutation { AddControllerFeatures(from: {id: %s}, to: {id: %s}) {from{id}, to{id}}}' % (v['id'], p))
            response = client.execute(query)

        for p in tqdm(v['specialFeatures']):
            status = 'specialFeatures'
            query = gql('mutation { AddControllerFeaturesSpecial(from: {id: %s}, to: {id: %s}) {from{id}, to{id}}}' % (v['id'], p))
            response = client.execute(query)
    except:
        vendors_not_exist.append((i, status))
        i = i + 1

print(('Vendors skipped (probably do not exist): %s') % (vendors_not_exist))

