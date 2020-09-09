from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from hashlib import sha256

from tilt import tilt

import requests
import json

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

# Import tilt file and convert to local python instance
file = json.loads(requests.get('https://raw.githubusercontent.com/Transparency-Information-Language/schema/master/tilt.json').content)
instance = tilt.tilt_from_dict(file)

# Create DataController
meta_id = abs(hash(instance.meta.id)) % (10 ** 8)
query_string = 'mutation { CreateController(id: %s, name: "%s", privacyPolicy: "%s") { _id }}' % (meta_id, instance.meta.name, instance.meta.url)
query = gql(query_string)
client.execute(query)

# Loop through all data disclosed items
for dC in instance.data_disclosed:
    p_id = 0
    for p in tqdm(dC.purposes):
        p_id = abs(hash(p)) % (10 ** 8) # number-only hash
        name = p.purpose
        description = p.description
        query_string = 'mutation { CreatePurpose(id: %s, name: "%s", description: "%s", descriptionLegal: "%s") { _id }}' % (p_id, name, description, '')
        query = gql(query_string)
        client.execute(query)
    
        query = gql('mutation { AddControllerPurposes(from: {id: %s}, to: {id: %s}) {from{id}, to{id}}}' % (meta_id, p_id))
        client.execute(query)

    for r in tqdm(dC.recipients):
        r_id = abs(hash(r.name)) % (10 ** 8)
        if r.name == None:
            r.name = r.category
        query_string = 'mutation { CreateController(id: %s, name: "%s", privacyPolicy: "%s") { _id }}' % (r_id, 'Recipient: ' + r.name, '')
        query = gql(query_string)
        client.execute(query)
        
        query = gql('mutation { AddControllerPurposes(from: {id: %s}, to: {id: %s}) {from{id}, to{id}}}' % (r_id, p_id))
        client.execute(query)