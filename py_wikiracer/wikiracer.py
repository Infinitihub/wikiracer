from py_wikiracer.internet import Internet
from typing import List
import queue
import heapq
from html.parser import HTMLParser


class Parser:

    @staticmethod
    def get_links_in_page(html: str) -> List[str]:
        """
        In this method, we should parse a page's HTML and return a list of links in the page.
        Be sure not to return any link with a DISALLOWED character.
        All links should be of the form "/wiki/<page name>", as to not follow external links.

        To do this, you can use str.find, regex, or you can
            instantiate your own subclass of HTMLParser in this function and feed it the html.
        """
        links = []
        disallowed = Internet.DISALLOWED

        # YOUR CODE HERE
        # Make sure your list doesn't have duplicates. Return the list in the same order as they appear in the HTML.
        # You can define your subclass of HTMLParser right here inside this function, or you could do it outside of this function.
        html = html.split('\n')
        a_tags = []
        unfiltered_links = []
        for line in html:
            if ('</a>' in line or '<a' in line) and 'wiki' in line:
                a_tags.append(line)
        for value in a_tags:
            value = value.split('"')
            for item in value:
                if "/wiki/" in item:
                    unfiltered_links.append(item)
        for link in unfiltered_links:
            split_link = link.split('/wiki/')
            Dis_bool = True
            for disallow in disallowed:
                if disallow in split_link[1] or split_link[0] != "":
                    Dis_bool = False
                    continue
            if Dis_bool is True and link not in links:
                links.append(link)
        # This function will be mildly stress tested.

        return links

    def path_extractor(self, visited, source, goal):
        path = []
        tracker = goal
        while source not in path and goal not in path:
            for value in visited[::-1]:
                if value[0] == tracker:
                    path.append(value[0])
                    tracker = value[1]
                if value[1] == source:
                    path.append(value[1])
                    path = path[::-1]
                    return path


# In these methods, we are given a source page and a goal page, and we should return
#  the shortest path between the two pages. Be careful! Wikipedia is very large.

# These are all very similar algorithms, so it is advisable to make a global helper function that does all of the work, and have
#  each of these call the helper with a different data type (stack, queue, priority queue, etc.)

class BFSProblem:
    def __init__(self, internet: Internet):
        self.internet = internet

    # Example in/outputs:
    #  bfs(source = "/wiki/Computer_science", goal = "/wiki/Computer_science") == ["/wiki/Computer_science", "/wiki/Computer_science"]
    #  bfs(source = "/wiki/Computer_science", goal = "/wiki/Computation") == ["/wiki/Computer_science", "/wiki/Computation"]
    # Find more in the test case file.

    # Do not try to make fancy optimizations here. The autograder depends on you following standard BFS and will check all of the pages you download.
    # Links should be inserted into the queue as they are located in the page, and should be obtained using Parser's get_links_in_page.
    # Be very careful not to add things to the "visited" set of pages too early. You must wait for them to come out of the queue first. See if you can figure out why.
    #  This applies for bfs, dfs, and dijkstra's.
    # Download a page with self.internet.get_page().
    def bfs(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia"):
        links = queue.Queue()
        links.put([source, source])
        visited = []
        path_help_list = []
        parser = Parser()
        while not links.empty():
            link = links.get()
            visited.append(link[0])
            if link[0] != source:
                path_help_list.append(link)
            html = self.internet.get_page(link[0])
            for val in parser.get_links_in_page(html):
                if val == goal:
                    path_help_list.append([val, link[0]])
                    path = parser.path_extractor(path_help_list, source, goal)
                    return path
                if val not in visited:
                    links.put([val, link[0]])
        return None  # if no path exists, return None


class DFSProblem:
    def __init__(self, internet: Internet):
        self.internet = internet

    # Links should be inserted into a stack as they are located in the page. Do not add things to the visited list until they are taken out of the stack.
    def dfs(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia"):
        links = queue.LifoQueue()
        links.put([source, source])
        visited = []
        path_help_list = []
        parser = Parser()
        while not links.empty():
            link = links.get()
            visited.append(link[0])
            if link[0] != source:
                path_help_list.append(link)
            html = self.internet.get_page(link[0])
            for val in parser.get_links_in_page(html):
                if val == goal:
                    path_help_list.append([val, link[0]])
                    path = parser.path_extractor(path_help_list, source, goal)
                    return path
                if val not in visited:
                    links.put([val, link[0]])
        return None  # if no path exists, return None


class Matrix:
    def __init__(self):
        self.matrix = {}

    def add_link(self, link):
        if link not in self.matrix:
            self.matrix[link] = {}

    def add_connection(self, link, new_link, cost):
        if link not in self.matrix:
            self.add_link(link)
        if new_link not in self.matrix:
            self.add_link(new_link)
        self.matrix[link][new_link] = cost

    def get_cost(self, link, new_link):
        return self.matrix[link][new_link]


class DijkstrasProblem:
    def __init__(self, internet: Internet):
        self.internet = internet

    # Links should be inserted into the heap as they are located in the page.
    # By default, the cost of going to a link is the length of a particular destination link's name. For instance,
    #  if we consider /wiki/a -> /wiki/ab, then the default cost function will have a value of 8.
    # This cost function is overridable and your implementation will be tested on different cost functions. Use costFn(node1, node2)
    #  to get the cost of a particular edge.
    # You should return the path from source to goal that minimizes the total cost. Assume cost > 0 for all edges.
    def dijkstras(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia", costFn=lambda x, y: len(y)):
        heap = [[0, source]]
        distances = {source: 0}
        parents = {source: None}
        visited = set()
        matrix = Matrix()
        parser = Parser()
        while heap:
            pair = heapq.heappop(heap)
            distance = pair[0]
            this_link = pair[1]
            if this_link in visited:
                continue
            visited.add(this_link)
            html = self.internet.get_page(this_link)
            for next_link in parser.get_links_in_page(html):
                if next_link not in distances:
                    distances[next_link] = float('infinity')
                matrix.add_connection(this_link, next_link, costFn(this_link, next_link))
                adjusted_distance = distance + matrix.get_cost(this_link, next_link)
                if adjusted_distance < distances[next_link]:
                    distances[next_link] = adjusted_distance
                    parents[next_link] = this_link
                    heapq.heappush(heap, [adjusted_distance, next_link])
                if next_link == goal:
                    path = []
                    if this_link == goal:
                        path.append(this_link)
                    while next_link:
                        path.append(next_link)
                        next_link = parents[next_link]
                    path = path[::-1]
                    return path
        return None


class WikiracerProblem:
    def __init__(self, internet: Internet):
        self.internet = internet

    # Time for you to have fun! Using what you know, try to efficiently find the shortest path between two wikipedia pages.
    # Your only goal here is to minimize the total amount of pages downloaded from the Internet, as that is the dominating time-consuming action.

    # Your answer doesn't have to be perfect by any means, but we want to see some creative ideas.
    # One possible starting place is to get the links in `goal`, and then search for any of those from the source page, hoping that those pages lead back to goal.

    # Note: a BFS implementation with no optimizations will not get credit, and it will suck.
    # You may find Internet.get_random() useful, or you may not.

    def wikiracer(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia"):
        for_links = queue.Queue()
        for_links.put([source, source])
        back_links = queue.Queue()
        back_links.put([goal, goal])
        for_visited = []
        back_visited = []
        parser = Parser()
        if source == goal:
            return [source, source]
        while not for_links.empty() and not back_links.empty():
            link = for_links.get()
            for_visited.append(link[0])
            html = self.internet.get_page(link[0])
            for_page_links = parser.get_links_in_page(html)
            for val in for_page_links:
                if val not in for_visited:
                    for_links.put([val, link[0]])

            link = back_links.get()
            back_visited.append(link[0])
            html = self.internet.get_page(link[0])
            back_page_links = parser.get_links_in_page(html)
            for val in back_page_links:
                if val not in for_visited:
                    back_links.put([val, link[0]])

            temp_for_links = []
            temp_for_queue = self.copy_queue(for_links)
            temp_back_links = []
            temp_back_queue = self.copy_queue(back_links)
            for temp in range(for_links.qsize()):
                val = for_links.get()
                temp_for_links.append(val)
            for temp in range(back_links.qsize()):
                val = back_links.get()
                temp_back_links.append(val)
            for_links = self.copy_queue(temp_for_queue)
            back_links = self.copy_queue(temp_back_queue)

            intersect = self.check_intersection(for_visited, back_visited, temp_for_links, temp_back_links)
            if intersect is not None:
                return intersect
        return None  # if no path exists, return None

    def copy_queue(self, the_queue):
        copy = queue.Queue()
        temp_list = []
        for count in range(the_queue.qsize()):
            item = the_queue.get()
            temp_list.append(item)
            copy.put(item)
        for item in temp_list:
            the_queue.put(item)
        return copy

    def check_intersection(self, for_v, back_v, for_link, back_link):
        temp_for_link = []
        temp_back_link = []
        for val in for_link:
            temp_for_link.append(val[0])
        for val in back_link:
            temp_back_link.append(val[0])
        if len(set(for_v).intersection(set(back_v))) > 0:
            intersect = list(set(for_v).intersection(set(back_v)))[0]
            back_v = back_v[::-1]
            path = []
            count = 1
            for value in for_v:
                if value == intersect:
                    count = 0
                if count == 1:
                    path.append(value)
            for value in back_v:
                if value == intersect:
                    count = 1
                if count == 1:
                    path.append(value)
            return path
        if len(set(temp_for_link).intersection(set(temp_back_link))) > 0:
            intersect = list(set(temp_for_link).intersection(set(temp_back_link)))[0]
            forward_visited = None
            backward_visited = None
            for val in for_link:
                if val[0] == intersect:
                    forward_visited = val[1]
            for val in back_link:
                if val[0] == intersect:
                    backward_visited = val[1]
            path = []
            back_v = back_v[::-1]
            for val in for_v:
                path.append(val)
                if val == forward_visited:
                    path.append(intersect)
                    break
            count = 0
            for val in back_v:
                if val != backward_visited and count == 1:
                    path.append(val)
                if val == backward_visited:
                    path.append(val)
                    count = 1
            return path
        if len(set(temp_for_link).intersection(set(back_v))) > 0:
            intersect = list(set(temp_for_link).intersection(set(back_v)))[0]
            forward_visited = None
            backward_visited = intersect
            for val in for_link:
                if val[0] == intersect:
                    forward_visited = val[1]
            path = []
            back_v = back_v[::-1]
            for val in for_v:
                path.append(val)
                if val == forward_visited:
                    path.append(intersect)
                    break
            count = 0
            for val in back_v:
                if val != backward_visited and count == 1:
                    path.append(val)
                if val == backward_visited:
                    path.append(val)
                    count = 1
            return path
        if len(set(for_v).intersection(set(temp_back_link))) > 0:
            intersect = list(set(for_v).intersection(set(temp_back_link)))[0]
            forward_visited = intersect
            backward_visited = None
            for val in back_link:
                if val[0] == intersect:
                    backward_visited = val[1]
            path = []
            back_v = back_v[::-1]
            for val in for_v:
                path.append(val)
                if val == forward_visited:
                    path.append(intersect)
                    break
            count = 0
            for val in back_v:
                if val != backward_visited and count == 1:
                    path.append(val)
                if val == backward_visited:
                    path.append(val)
                    count = 1
            return path


# KARMA
class FindInPageProblem:
    def __init__(self, internet: Internet):
        self.internet = internet

    # This Karma problem is a little different. In this, we give you a source page, and then ask you to make up some heuristics that will allow you to efficiently
    #  find a page containing all of the words in `query`. Again, optimize for the fewest number of internet downloads, not for the shortest path.

    def find_in_page(self, source="/wiki/Calvin_Li", query=["ham", "cheese"]):
        raise NotImplementedError("Karma method find_in_page")

        path = [source]

        # find a path to a page that contains ALL of the words in query in any place within the page
        # path[-1] should be the page that fulfills the query.
        # YOUR CODE HERE

        return path  # if no path exists, return None
