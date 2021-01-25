# aim: import data from neo4j into environment
# this can be extended as at present, its only going to retrieve the relationship triple store data

from py2neo import Graph
import pickle
import os

DATA_DIR = os.getenv('DIR_DATA')

gov_graph = Graph(scheme="https",
                  host="knowledge-graph.integration.govuk.digital",
                  port=7473,
                  secure=True,
                  # note: replace hashes with actual passwird
                  auth=('neo4j', '################'))


# test the connection
limit_1_result = gov_graph.run("MATCH (n:COVID_19) RETURN n LIMIT 1").data()
limit_1_result[0]['n']

# count of nodes
len(gov_graph.nodes)

# look at some node properties
type(limit_1_result[0]['n'])
limit_1_result[0]['n'].labels
limit_1_result[0]['n']['contentID']
limit_1_result[0]['n'].keys()
limit_1_result[0]['n']['public_updated_at']
limit_1_result[0]['n']['updated_at']
limit_1_result[0]['n']['documentType']
limit_1_result[0]['n']['contentID']
limit_1_result[0]['n']['name']
limit_1_result[0]['n']['description']
limit_1_result[0]['n']['first_published_at']
limit_1_result[0]['n']['text']
limit_1_result[0]['n']['publishing_app']
limit_1_result[0]['n']['title']

# retrieve the edge weights, triple store of: source, target, weight
# here we are restricting analysis to nodes with the Label "Cid"
result = gov_graph.run("MATCH (m:Cid) -[r:USER_MOVEMENT]-> (n:Cid) RETURN m.contentID, n.contentID, r.weight").data()
len(result)

filehandler = open(os.path.join(DATA_DIR, 'relationship_weights.bin'), 'wb')
pickle.dump(result, filehandler)

# end code
