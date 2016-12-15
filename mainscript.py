import igraph
import csv


#login,followers,following,languages,organizations

class Vertex:
    def __init__(self,name,languages):
        self.name = name
        self.languages = languages

# adding a edge to the map.
# vertices are concatenated with alphabetical order and "|" char.

def addToMap (map, key1, key2, value):
    if key1< key2:
        key = key1 + '|' + key2
    else:
        key = key2 + '|' + key1
    if key in map:
        map[key] = map[key] + value
    else:
        map[key] = value

vertexMap = {}
g = igraph.Graph()
edgeMap = {}
with open('users.csv','rb') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        processingPerson = row[0].strip()

        languageSet = []
        languages = row[3][1:len(row[3]) - 1].split(",")
        for lang in languages:
            languageSet.append(lang)

        v = Vertex(processingPerson, languageSet)
        v_index = g.add_vertex(v)
        vertexMap[processingPerson] = v_index


        followers = row[1][1:len(row[1])-1].split(",")
        for person in followers:
            addToMap(edgeMap,processingPerson,person, 0.4)

        following = row[1][1:len(row[1]) - 1].split(",")
        for person in following:
            addToMap(edgeMap, processingPerson, person, 0.6)

count = 0
for key,value in edgeMap.iteritems():
    print count
    count += 1
    vertices = key.split("|")
    v1 = vertexMap.get(vertices[0])
    v2 = vertexMap.get(vertices[1])
    g.add_edge(v1,v2,weight = value)

a = g.community_leading_eigenvector(weights='weight')


print 'x';

