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
        languages = row[4][1:-1].split(",")
        for lang in languages:
            languageSet.append(lang)

        print "Adding" + processingPerson

        g.add_vertex(name = processingPerson)

        followers = row[2][1:-1].split(",")
        for person in followers:
            addToMap(edgeMap,processingPerson,person, 0.3)

        following = row[3][1:len(row[1]) - 1].split(",")
        for person in following:
            addToMap(edgeMap, processingPerson, person, 0.1)


count = 0
for key,value in edgeMap.iteritems():
    count += 1
    vertices = key.split("|")
    try:
        g.add_edge(vertices[0],vertices[1],weight = value)
        print "V: " + vertices[0] + " = " + vertices[1]
    except ValueError:
        print "Vertex not found: " + vertices[0] + " = " + vertices[1]

color_list = ['red', 'blue', 'green', 'cyan', 'pink', 'orange', 'grey', 'yellow', 'white', 'black', 'purple', 'magenta']


community = g.community_multilevel()


igraph.plot(g, bbox=(0,0,2000,2000), margin = (5,5,5,5), vertex_color=[color_list[x] for x in community.membership])
print max(community.membership) #Printed number of communties to 11
print 'x';

