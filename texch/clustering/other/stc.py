from math import sqrt


from math import exp, log


def constant(x):
    return 1.0


def linear(x):
    return float(x)


def root(x):
    return x**0.5


def square(x):
    return x*x


def logit(x):
    try:
        return log(x)-log(1-x)
    except:
        return .0


def sigmoid(x):
    return 1.0 / exp(-x)

phi = {
   'constant': constant,
   'linear': linear,
   'square': square,
   'root': root,
   'log': log,
   'logit': logit,
   'sigmoid': sigmoid
}

def suffix(s):
    return [s[i:] for i in range(len(s))]


def radix(s):
    return [s]


def search(s, root, path, lvl = 0):
    for n in root.children:
        if n.char == s[lvl]:
            path.append(n)
            search(s, n, path, lvl + 1)


def collect_leaf_nodes(node, leafs):
    if len(node.children) == 0:
            leafs.append(node)
    for n in node.children:
        collect_leaf_nodes(n, leafs)


def print_tree(root, lvl=0):
        print ' '*lvl + ' ' +  root.char + ' ' + str(root.freq) + ' ' + str(root.min_freq)  + ' ' + str(root.max_freq)
        for i in root.children:
            print_tree(i, lvl+1)


class Node(object):
    def __init__(self, char):
        self.char = char
        self.freq = .0
        self.parent = None
        self.children = []
        self.isLeaf = False
        self.max_freq = .0
        self.min_freq = .0
        self.idf = 1


class Tree(object):
    def __init__(self, repr):
        self.root = Node('root')
        self.repr = repr
        self.scores = []
        self.scoring = .0
        self.leaves = []
        self.chains = []

    def search(self, s):
        path = []
        search(s, self.root, path)
        return path

    def add(self, s, freq = 1.0):
        subs = self.repr(s+'$')
        for sub in subs:
            path = self.search(sub)
            if len(path) == 0:
                cN = self.root
                self.root.freq += freq
                pos = 0
            else:
                self.root.freq += freq
                for n in path: n.freq += freq
                cN = path[-1]
                pos = len(path)
            for c in sub[pos:]:
                nN = Node(c)
                nN.freq += freq
                nN.parent = cN
                cN.children.append(nN)
                cN = nN

    def score(self, s, scale = 'linear', norm = 'match', noise = 0):
        result = .0
        subs = self.repr(s+'$')
        for sub in subs:
            match = self.search(sub)
            norm_factor = 1.0
            if norm == 'match':
                if len(match) > 0:
                    norm_factor = len(match)
                else:
                    norm_factor = 1.0
            elif norm == 'suffix':
                norm_factor = len(s)
            result += sum([phi[scale](n.freq / n.parent.freq) for n in match[noise:]]) / norm_factor
        return result

    def find_chain(self, node, chain):
        if node != self.root:
            chain.append(node)
            self.find_chain(node.parent,chain)
        else:
            self.chains.append(chain[::-1])
            chain = []

    def get_leaves(self):
        self.leaves = []
        collect_leaf_nodes(self.root, self.leaves)

    def get_chains(self):
        self.chains = []
        self.get_leaves()
        for leaf in self.leaves:
            chain = []
            self.find_chain(leaf, chain)

    def score_tree(self, norm='mean', norm2='no', idf='no'):
        self.get_chains()
        for chain in self.chains:
            s = .0
            if norm == 'mean':
                if idf == 'no':
                    for node in chain[:]:
                        s += node.min_freq / node.parent.min_freq + node.max_freq / node.parent.max_freq
                elif idf == 'yes':
                    for node in chain[:]:
                        s += (node.min_freq / node.parent.min_freq + node.max_freq / node.parent.max_freq) \
                             / (node.idf / node.parent.idf)
            if norm == 'sum':
                for node in chain:
                    s += 1
            if norm == 'mult':
                for node in chain:
                    if node.char == '$':
                        s += node.min_freq * node.max_freq
            if norm == 'min':
                for node in chain:
                    s += (node.min_freq) / (node.parent.min_freq)
            if norm == 'max':
                for node in chain:
                    s += (node.max_freq) / (node.parent.max_freq)
            if norm == 'geom_mean':
                for node in chain:
                    s += sqrt((node.min_freq*node.max_freq) / (node.parent.min_freq*node.parent.max_freq))
            if norm == 'harm_mean':
                for node in chain:
                    s += 2./(1./node.min_freq+1./node.max_freq) / 2./(1./node.parent.min_freq+1./node.parent.max_freq)

            self.scores.append(float(s))
            if norm2 == 'mean':
                self.scoring = sum(self.scores) / len(self.chains)
            else:
                self.scoring = sum(self.scores)


def find_paths2(leaf,  path, paths, thrsh1 = 10, thrsh2 = 15000, len_thrsh = 4):
    if leaf.freq > thrsh1:
        if not leaf.char == '$':
            path += leaf.char
        if not leaf.parent.in_path and leaf.parent.freq < thrsh2:
            print  path
            find_paths2(leaf.parent, path, paths)
        else:
            if not path[::-1] in paths and len(path) >= len_thrsh:
                paths.append(path[::-1])
    else:
        find_paths2(leaf.parent, path, paths)


def subtree(t1, t2, new_tree, node1, node2, cN):
    '''
    t3 is the  result
    '''
    for ch1 in node1.children:
        for ch2 in node2.children:
            if ch1.char == ch2.char:
                if ch1.parent == t1.root:
                    cN = new_tree.root
                    new_tree.root.max_freq = max(t1.root.freq, t2.root.freq)
                    new_tree.root.min_freq = min(t1.root.freq, t2.root.freq)
                nN = Node(ch1.char)
                nN.max_freq = max(ch1.freq, ch2.freq)
                nN.min_freq = min(ch1.freq, ch2.freq)
                nN.parent = cN
                cN.children.append(nN)
                # if cN in new_tree.leaves:
                #     new_tree.leaves.remove(cN)
                # new_tree.leaves.append(nN)
                # cN = nN
                subtree(t1, t2, new_tree, ch1, ch2, nN)


def IDF(t1, t2, node1, node2):
    for ch1 in node1.children:
        for ch2 in node2.children:
            if ch1.char == ch2.char:
                if ch1.parent == t1.root:
                    ch1.idf = t2.root.freq
                ch1.idf = ch2.freq
                IDF(t1, t2, ch1, ch2)


class DistanceSim(object):

    def __init__(self, sim_matrix):
        self.sim_matrix = sim_matrix

    def similarity_func(self, instance1, instance2):
        return self.sim_matrix[instance1][instance2]

