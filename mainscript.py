import igraph
import csv
import Queue
import random
import itertools


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
        for vertex in g.vs():
            vertex["color"] = str('#') + colors[membership[vertex.index]]
        visual_style["vertex_color"] = g.vs["color"]
    igraph.plot(g, **visual_style)


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
        print "Poped: " + popped
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
        g.add_vertex(vertex, label=vertex)

    print "Edges: " + str(addToMap.counter)
    count = 0
    a = 0
    edgeWeights = []
    for key, value in edgeMap.items():
        count += 1
        vertices = key.split("|")
        try:
            g.add_edge(vertices[0], vertices[1], weight=value)
            edgeWeights.append(value)
            #           print "V: " + vertices[0] + " = " + vertices[1]
        except ValueError:
            a += 1
            # print "Vertex not found: " + vertices[0] + " = " + vertices[1]

    print "Edges are added to the graph. Count is: " + str(count) + " | Errors:" + str(a)

    color_list = ['red', 'blue', 'green', 'cyan', 'pink', 'orange', 'grey', 'yellow', 'white', 'black', 'purple',
                  'magenta']

    # community3 = g.community_infomap(edge_weights=edgeWeights)

    # print ("cm3 is done")
    # community4 = g.community_multilevel(weights=edgeWeights)
    # print ("cm4 is done")
    # community5 = g.community_fastgreedy(weights=edgeWeights)
    # print ("cm5 is done")
    # community6 = g.community_leading_eigenvector(weights=edgeWeights)
    # print ("cm6 is done")
    #  community7 = g.community_edge_betweenness(weights=edgeWeights)
    #  community8 = g.community_walktrap(weights=edgeWeights, steps=4)
    community9 = g.community_walktrap(weights=edgeWeights, steps=4)

    print("cm is done!")

    # _plot(g,community3.membership, name="graph_im.pdf")
    # _plot(g,community4.membership, name="graph_ml.pdf")
    # _plot(g,community5.as_clustering().membership, name="graph_fg.pdf")
    # _plot(g,community6.membership, name="graph_lev.pdf")
    # _plot(g,community7.membership, name="graph_eb.pdf")
    # _plot(g,community8.as_clustering().membership, name="graph_wt4.pdf")
    _plot(g, community9.as_clustering().membership, name="graph_wt5.pdf")
    #    layout = g.layout("automatic")
    #     igraph.plot(community3, target="graph_im.pdf", asp=0.8, bbox=(0, 0, 2000, 2000),
    #                 margin=(100, 100, 100, 100),
    #                 vertex_color=[color_list[x % len(color_list)] for x in community3.membership])

    #    print max(community5.as_clustering().membership)
    print max(community9.as_clustering().membership)


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
