import igraph
import csv


def purify():
    people = {}
    to_be_discarded = set()
    with open('users.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        v_index = 0
        for row in reader:
            proc_person = row[0].strip()
            people[proc_person] = set()

            followers = row[2][1:-1].split(",")
            for person in followers:
                if person not in people:
                    people[person] = set()
                people[person].add(proc_person)
                people[proc_person].add(person)

            following = row[3][1:len(row[1]) - 1].split(",")
            for person in following:
                if person not in people:
                    people[person] = set()
                people[person].add(proc_person)
                people[proc_person].add(person)

    for person in people:
        if len(people[person]) <= 1:
            to_be_discarded.add(person)

    return to_be_discarded


# adding a edge to the map.
# vertices are concatenated with alphabetical order and "|" char.
def addToMap(map, key1, key2, value):
    if key1 < key2:
        key = key1 + '|' + key2
    else:
        key = key2 + '|' + key1
    if key in map:
        map[key] = map[key] + value
    else:
        map[key] = value


def main():
    discard = purify()
    vertexMap = {}
    g = igraph.Graph()
    edgeMap = {}

    nodes = set()
    with open('users.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        v_index = 0
        for row in reader:
            processingPerson = row[0].strip()
            if processingPerson in discard:
                continue

            languageSet = []
            languages = row[4][1:-1].split(",")
            for lang in languages:
                languageSet.append(lang)

            nodes.add(processingPerson)

            followers = row[2][1:-1].split(",")
            for person in followers:
                if person not in discard:
                    nodes.add(person)
                    addToMap(edgeMap, processingPerson, person, 0.3)

            following = row[3][1:len(row[1]) - 1].split(",")
            for person in following:
                if person not in discard:
                    nodes.add(person)
                    addToMap(edgeMap, processingPerson, person, 0.1)

    for person in nodes:
        g.add_vertex(name=person)

    count = 0
    for key, value in edgeMap.iteritems():
        count += 1
        vertices = key.split("|")
        try:
            g.add_edge(vertices[0], vertices[1], weight=value)
#            print "V: " + vertices[0] + " = " + vertices[1]
        except ValueError:
            a=0
#           print "Vertex not found: " + vertices[0] + " = " + vertices[1]

    color_list = ['red', 'blue', 'green', 'cyan', 'pink', 'orange', 'grey', 'yellow', 'white', 'black', 'purple',
                  'magenta']

    community = g.community_multilevel()
    igraph.plot(g, bbox=(0, 0, 2000, 2000), margin=(5, 5, 5, 5),
                vertex_color=[color_list[x % len(color_list)] for x in community.membership])
    print max(community.membership)  # Printed number of communties to 11
    print 'x'


if __name__ == "__main__":
    main()
