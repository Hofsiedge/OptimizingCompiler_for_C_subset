from graph_colouring import colour_graph

class BasicBlock:

    def __init__(self, parents=[], left=None, right=None):
        self.parents    = parents
        self.left       = left      # for a next block or if
        self.right      = right     # for a loop or else
        self.operations = []

    def add(self, element):
        self.operations.append(element)
        

class DU:
    def __init__(self, expression, source):
        self.source     = source
        self.expression = expression
        self.block      = None

class Definition(DU):
    def __init__(self, expression, source):
        super().__init__(expression, source)
        self.symbol = expression.name

    def __repr__(self):
        return f'<def {self.expression.name}>'


class Usage(DU):
    def __init__(self, expression, source):
        super().__init__(expression, source)

    def __repr__(self):
        return f'<use {self.expression.name}>'


class DUNode:
    def __init__(self, du: DU, left=None, right=None):
        self.left   = left
        self.right  = right
        self.du     = du
        self.chains = set()
    
    # can't handle conditional statements yet
    @staticmethod
    def from_flowgraph(flowgraph: list):

        root        = None
        prev        = None
        first_nodes = {}

        for block in flowgraph:
            if block == None:
                break
            du_list = sum([op.du for op in block.operations], [])
            for i in range(len(du_list)):
                du          = du_list[i]
                du.block    = block
                node        = DUNode(du)
                if i == 0:
                    first_nodes[block] = node
                    if root == None:
                        root = node
                if prev:
                    prev.left = node
                if i == len(du_list) - 1:
                    node.right = first_nodes[block.right] if block.right else None
                    # print(f'Node right: {node.right}, node: {node.du}')
                prev = node
    
        return root

    def __repr__(self):
        return f'[node {self.du} l:{self.left.du if self.left else None} r:{self.right.du if self.right else None}]'


class DUChain:
    def __init__(self, symbol, definition):
        self.symbol     = symbol
        self.definition = definition
        self.web        = None
        self.usages     = []

    def __and__(self, other):
        return set(self.usages) & set(other.usages)
        
    def __repr__(self):
        return f'<{self.symbol} {self.usages}>' 

    @staticmethod
    def build_chains(du_list: DUNode):

        def get_usages(chain: DUChain, du_node: DUNode, visited_nodes: set): 
            if  not du_node \
                or type(du_node.du) == Definition and du_node.du.expression.name == chain.symbol \
                or du_node in visited_nodes:

                return []
            right = get_usages(chain, du_node.right, visited_nodes | {du_node})
            # print(f'right: {right}')
            left = get_usages(chain, du_node.left, visited_nodes | {du_node})
            if left or right or du_node.du.expression.name == chain.symbol:
                du_node.chains.add(chain)
            return ([du_node] if du_node.du.expression.name == chain.symbol else []) + left + right

        du_chains   = []
        node        = du_list

        while node:
            if type(node.du) == Definition:
                chain           = DUChain(node.du.symbol, node.du)
                left            = get_usages(chain, node.left, set()) 
                right           = get_usages(chain, node.right, set()) 
                chain.usages    = left + right
                du_chains.append(chain)
            node = node.left 

        return du_chains
  

class Web:
    def __init__(self, *chains, main_nodes=None):
        self.nodes      = set()
        self.chains     = chains
        for chain in chains:
            self.nodes  = self.nodes | set(chain.usages) | {chain.definition}

    # CHECKME
    def __add__(self, other):
        new_web = Web()
        new_web.chains  = self.chains + other.chains
        new_web.nodes   = self.nodes.union(other.nodes)
        
        return new_web
    
    @staticmethod
    def from_chains(chains: list):

        webs = [Web(chain) for chain in chains]
        idx_1 = 0

        while idx_1 < len(webs):
            idx_2 = idx_1
            while idx_2 < len(webs):
                if idx_1 != idx_2 and set(webs[idx_1].nodes) & set(webs[idx_2].nodes):
                    # print(f'; JOINT {idx_1} {idx_2}')
                    new_web     = webs[idx_1] + webs[idx_2]
                    webs[idx_1] = new_web
                    del webs[idx_2]
                else:
                    idx_2 += 1
            idx_1 += 1

        for web in webs:
            for chain in web.chains:
                chain.web = web

        return webs

    def __repr__(self):
        return f'<web {self.chains[0].symbol}:{len(self.chains)}>'

        
class InterferenceGraph:

    def __init__(self, root: DUNode, webs: list):
        inverse_mapping     = {i: web for i, web in enumerate(webs)}
        node        = root
        mapping     = {web: i for i, web in enumerate(webs)}
        adj_list    = {i: [] for i in inverse_mapping}
        while node:
            current_webs = set([chain.web for chain in node.chains])
            for web_1 in current_webs:
                for web_2 in current_webs:
                    if web_1 == web_2:
                        continue
                    if mapping[web_2] not in adj_list[mapping[web_1]]:
                        adj_list[mapping[web_1]].append(mapping[web_2])
                        adj_list[mapping[web_2]].append(mapping[web_1])
            node = node.left

        self.mapping = mapping
        self.inverse_mapping = inverse_mapping
        self.adj_list = adj_list        


    def colour(self):
        colours = colour_graph(self.adj_list)
        
        colour_lists = {colour: [chain for chain in colours.keys() if colours[chain] == colour]
                            for colour in colours.values()}
        priorities = sorted(colour_lists.keys(),
                            key = lambda colour: sum([len(self.inverse_mapping[i].nodes) + 1 for i in colour_lists[colour]]),
                            reverse=True)

        registers = ['ebx', 'ecx', 'edx'] + [f's{i}' for i in range(len(colour_lists.keys()) - 3)]

        return colour_lists, priorities, registers

    def allocate(self, colour_lists, priorities, registers):
        for i in range(len(priorities)):
            colour      = priorities[i]
            register    = registers[i]
            for web_idx in colour_lists[colour]:
                web         = self.inverse_mapping[web_idx]
                for chain in web.chains:
                    chain.definition.expression.register.name = register
                    chain.definition.expression.register.real = register[0] == 'e'
