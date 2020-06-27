from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

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

contentFile = open('contents.json', 'r')
lines = contentFile.readlines()

# for line in lines:
#    query = gql('mutation { CreateController(' + line.strip() + ') {_id}}')
#    print(query)
#    print(client.execute(query))


contentFile = reversed(list(open('contents.json', 'r')))
for line in lines:
    dpo = line.strip().split('",')
    del dpo[0] # id
    del dpo[1] # fullName 
    del dpo[4] # website
    del dpo[4] # policy

    result = ''
    for d in dpo:
        result = result + d + '",'
    result = result[:-2]

    query = gql('mutation { CreateDataProtectionOfficer(' + result + ') {_id}}')
    #print('mutation { CreateDataProtectionOfficer(' + result + ') {_id}}')
    
    client.execute(query)
