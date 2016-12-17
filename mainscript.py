import igraph
import csv
import Queue
import operator
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
        addToMap.counter += 1


def addMap(map,  key, value):
    if key != " " and key != "":
        if key in map:
            map[key] = map[key] + value
        else:
            map[key] = value


def main():

    addToMap.counter = 0

    g = igraph.Graph()

    map = {}
    mainperson = ""
    count = 0
    vertices = set()
    edgeMap = {}
    with open('users.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            processingPerson = row[0].strip()
            if count == 0:
                mainperson = processingPerson
            map[processingPerson] = row
            count += 1
    print "Reading done"
    queue = Queue.Queue()
    print "Mainperson: " + mainperson
    vertices.add(mainperson)

    row = map.get(mainperson)

    followers = row[2][1:-1].split(",")
    following = row[3][1:len(row[1]) - 1].split(",")

    for person in followers:
        addToMap(edgeMap, mainperson, person, 0.2)
        queue.put(person)

    for person in following:
        addToMap(edgeMap, mainperson, person, 0.3)
        queue.put(person)

    queue.put("!!!!!")

    while queue.qsize() > 0:

        popped = queue.get()
        if popped == "!!!!!":
            break
        else:
            vertices.add(popped)

            row = map.get(popped)

            if row:
                followers = row[2][1:-1].split(",")
                following = row[3][1:len(row[1]) - 1].split(",")

                if followers:
                    for person in followers:
                        addToMap(edgeMap, popped, person, 0.2)
                        queue.put(person)
                        vertices.add(person)
                if following:
                    for person in following:
                        addToMap(edgeMap, popped, person, 0.3)
                        queue.put(person)
                        vertices.add(person)

    while queue.qsize() > 0:
        popped = queue.get()

        row = map.get(popped)

        if row:
            followers = row[2][1:-1].split(",")
            following = row[3][1:len(row[1]) - 1].split(",")

            if followers:
                for person in followers:
                    if person in vertices:
                        addToMap(edgeMap, popped, person, 0.2)
            if following:
                for person in following:
                    if person in vertices:
                        addToMap(edgeMap, popped, person, 0.3)

    print "Mapping done."

    for vertex in vertices:
        if vertex:
            g.add_vertex(vertex, label=vertex)

    print "Edges: " + str(addToMap.counter)
    count = 0
    a = 0
    for key, value in edgeMap.items():
        count += 1
        vertices = key.split("|")
        try:
            if vertices[0]:
                if vertices[1]:
                    g.add_edge(vertices[0], vertices[1], weight=value)
            del edgeMap[key]
            #           print "V: " + vertices[0] + " = " + vertices[1]
        except ValueError:
            a += 1
            # print "Vertex not found: " + vertices[0] + " = " + vertices[1]

    print "Edges are added to the graph. Count is: " + str(count) + " | Errors:" + str(a)

    color_list = ['red', 'blue', 'green', 'cyan', 'pink', 'orange', 'grey', 'yellow', 'white', 'black', 'purple',
                  'magenta']

    community = g.community_multilevel(weights="weight")

    arrays = []

    i = 0
    while i < community._len:
        arrays.append([])
        i += 1

    x = 0
    for vertex in g.vs["label"]:
        if vertex:
            arrays[community.membership[x]].append(vertex)
            x += 1

    #Report part
    i = 0
    while i < community._len:
        languages = {}
        orgcomp = {}
        for vertex in arrays[i]:
            row = map.get(vertex)

            if row:

                if row[1]:
                    comp = row[1].replace(" ", "")
                    if comp:
                        addMap(orgcomp, comp, 1)

                org = row[5][1:len(row[5]) - 1].split(",")

                for organization in org:
                    if org:
                        organization = organization.replace(" ", "")
                        addMap(orgcomp, organization, 1)

                langs = row[4][1:len(row[4]) - 1].split(",")

                for lang in langs:
                    if lang:
                        lang = lang.replace(" ", "")
                        if lang != "None":
                            addMap(languages, lang, 1)

        print "For community i: " + str(i) + " (shown in " + color_list[i] + " )"
        first = max(orgcomp.iteritems(), key=operator.itemgetter(1))[0]
        del orgcomp[first]
        second = max(orgcomp.iteritems(), key=operator.itemgetter(1))[0]
        del orgcomp[second]
        third = max(orgcomp.iteritems(), key=operator.itemgetter(1))[0]
        print "Organizations : \n1. %s \n2. %s \n3. %s" % (first, second, third)

        first = max(languages.iteritems(), key=operator.itemgetter(1))[0]
        del languages[first]
        second = max(languages.iteritems(), key=operator.itemgetter(1))[0]
        del languages[second]
        third = max(languages.iteritems(), key=operator.itemgetter(1))[0]
        print "Languages : \n1. %s \n2. %s \n3. %s" % (first, second, third)

        i += 1

    layout = g.layout("automatic")

    igraph.plot(community,layout=layout, target = "graph.pdf", asp=0.35, bbox=(0, 0, 2000, 2000), margin=(100, 100, 100, 100),
                vertex_color=[color_list[x % len(color_list)] for x in community.membership])

    print max(community.membership)  # Printed number of communties


if __name__ == "__main__":
    main()

"""
   while q.qsize() != 0:
        poped = q.get()

        if poped != "!!!!":
            followers = f1.get(poped)
            following = f2.get(poped)

            c1 = 0
            c2 = 0
            for person in followers:
                addToMap(edgeMap, processingPerson, person, 0.3)
                q.put(person)

            for person in following:
                addToMap(edgeMap, processingPerson, person, 0.1)
                q.put(person)
"""