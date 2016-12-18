import igraph
import csv
import Queue
import random
import itertools
import operator


color_list = []


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


def _plot(g, membership=None, name="graph.pdf"):
    if membership is not None:
        gcopy = g.copy()
        edges = []
        edges_colors = []
        for edge in g.es():
            if membership[edge.tuple[0]] != membership[edge.tuple[1]]:
                edges.append(edge)
                edges_colors.append("gray")
            else:
                edges_colors.append("black")
        gcopy.delete_edges(edges)
        layout = gcopy.layout("kk")
        g.es["color"] = edges_colors
    else:
        layout = g.layout("kk")
        g.es["color"] = "gray"
    visual_style = {}
    visual_style["vertex_label_dist"] = 0
    visual_style["vertex_shape"] = "circle"
    visual_style["edge_color"] = g.es["color"]
    # visual_style["bbox"] = (4000, 2500)
    visual_style["vertex_size"] = 30
    visual_style["layout"] = layout
    visual_style["bbox"] = (2000, 2000)
    visual_style["margin"] = 50
    visual_style["target"] = name
    # visual_style["edge_label"] = g.es["weight"]
    # for vertex in g.vs():
    #     vertex["label"] = vertex.name
    if membership is not None:
        colors = []
        for i in range(0, max(membership) + 1):
            colors.append('%06X' % random.randint(0, 0xFFFFFF))
            color_list.append('%06X' % random.randint(0, 0xFFFFFF))
        for vertex in g.vs():
            vertex["color"] = str('#') + colors[membership[vertex.index]]
        visual_style["vertex_color"] = g.vs["color"]
    igraph.plot(g, **visual_style)


def addMap(map, key, value):
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
    organizations_and_company = {}
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
    following = row[3][1:-1].split(",")
    orgs = row[5][0:-1].split(",")
    comp = row[1][0:-1].strip()

    if comp not in organizations_and_company:
        organizations_and_company[comp] = set()
        organizations_and_company[comp].add(mainperson)

    for org in orgs:
        if org.strip() not in organizations_and_company:
            organizations_and_company[org.strip()] = set()
        organizations_and_company[org.strip()].add(mainperson)

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
                processingPerson = row[0].strip()
                followers = row[2][1:-1].split(",")
                following = row[3][1:-1].split(",")
                orgs = row[5][0:-1].split(",")
                comp = row[1][0:-1].strip()

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

                if comp not in organizations_and_company:
                    organizations_and_company[comp] = set()

                organizations_and_company[comp].add(processingPerson)

                for org in orgs:
                    org = org.strip()
                    if org not in organizations_and_company:
                        organizations_and_company[org] = set()
                    organizations_and_company[org].add(processingPerson)

    while queue.qsize() > 0:
        popped = queue.get()

        row = map.get(popped)

        if row:
            followers = row[2][1:-1].split(",")
            following = row[3][1:len(row[1]) - 1].split(",")

            if followers:
                for person in followers:
                    if person in vertices:
                        addToMap(edgeMap, popped, person, 0.02)
            if following:
                for person in following:
                    if person in vertices:
                        addToMap(edgeMap, popped, person, 0.03)

    count = 0
    for key in organizations_and_company:
        if key is not None and key.strip() is not "" and len(organizations_and_company[key]) >= 2:
            for i, j in itertools.combinations(organizations_and_company[key], 2):
                addToMap(edgeMap, i, j, 0.6)
                count += 1

    print("orgy times: " + str(count))

    print "Mapping done."

    for vertex in vertices:
        if vertex:
            g.add_vertex(vertex, label=vertex)

    print "Edges: " + str(addToMap.counter)
    count = 0
    a = 0
    edgeWeights = []
    for key, value in edgeMap.items():
        count += 1
        vertices = key.split("|")
        try:
            if vertices[0]:
                if vertices[1]:
                    g.add_edge(vertices[0], vertices[1], weight=value)
                    edgeWeights.append(value)

            del edgeMap[key]
            #           print "V: " + vertices[0] + " = " + vertices[1]
        except ValueError:
            a += 1
            # print "Vertex not found: " + vertices[0] + " = " + vertices[1]

    print "Edges are added to the graph. Count is: " + str(count) + " | Errors:" + str(a)

    community = g.community_walktrap(weights=edgeWeights, steps=4)
    _plot(g, community.as_clustering().membership, name="graph_wt5.pdf")

    arrays = []

    i = 0
    while i < community.as_clustering()._len:
        arrays.append([])
        i += 1

    x = 0
    for vertex in g.vs["label"]:
        if vertex:
            arrays[community.as_clustering().membership[x]].append(vertex)
            x += 1

    # Report part
    i = 0
    while i < len(community.as_clustering()):
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

        first = ""
        second = ""
        third = ""
        if len(orgcomp) > 0:
            print "For community i: " + str(i) + " (shown in " + color_list[i] + " )"
            first = max(orgcomp.iteritems(), key=operator.itemgetter(1))[0]
            del orgcomp[first]
            if len(orgcomp) > 0:
                second = max(orgcomp.iteritems(), key=operator.itemgetter(1))[0]
                del orgcomp[second]
                if len(orgcomp) > 0:
                    third = max(orgcomp.iteritems(), key=operator.itemgetter(1))[0]

        print "Organizations : \n1. %s \n2. %s \n3. %s" % (first, second, third)
        first,second,third = "","",""

        if len(languages) > 0:
            first = max(languages.iteritems(), key=operator.itemgetter(1))[0]
            del languages[first]
            if len(languages) > 0:
                second = max(languages.iteritems(), key=operator.itemgetter(1))[0]
                del languages[second]
                if len(languages) > 0:
                    third = max(languages.iteritems(), key=operator.itemgetter(1))[0]

        print "Languages : \n1. %s \n2. %s \n3. %s" % (first, second, third)

        i += 1

    print max(community.as_clustering().membership)  # Printed number of communties



if __name__ == "__main__":
    main()