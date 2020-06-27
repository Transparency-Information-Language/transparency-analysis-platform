import { ApolloClient } from "apollo-boost"; 

const client = new ApolloClient( {
    uri: 'http://localhost:4001/'
});

client.query({
    query: gql`query {
        DataProtectionOfficer(filter: { name_contains: "Burns" }) {
          name
          _id
        }
      }
      `
}).then(
    result => console.log(result)
    );
