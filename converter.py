#!/usr/bin/python3

import re
import sys

class Text2Tuple:
	
	def __init__(self, file):

		self.sentences = self._parseFile(file)

	def _parseFile(self,file):
		
		#each sent is a set of dep tuples 
		sents = [] 
		
		sent_buffer = []

		for line in file.readlines():
			if line == '\n':
				sents.append([x for x in sent_buffer])
				sent_buffer = [] 
			else:
				sent_buffer.append(self._procLine(line))
		
		return sents
	
	
	def _procLine(self, line):
		#!!!!!!!!!!!!!!!!! degisiklik
		REGEX=r"([a-z:_]+)\(([\da-zA-Z%$?.,;'-:\\.\/!]+-\d+),\s+([\da-zA-Z%$?.,;'-:\\.\/!]+-\d+)\)"
		line = line.strip()
		pattern = re.compile(REGEX)
		dependency = pattern.match(line).group(1)
		head = self._splitWord(pattern.match(line).group(2))
		child = self._splitWord(pattern.match(line).group(3))

		return dependency, head, child 
	
	def _splitWord(self, word):
		
		lex_second = word.split('/')
		
		if lex_second[0] == 'ROOT-0':
			lex, postag, index = ['ROOT','ROOT', '0']
		else:
			second = lex_second[-1]
			lex = '/'.join(lex_second[:-1])
			postag, index = second.split('-')
			
		return lex, postag, index

class Converter:

	def __init__(self, sents):
		"""each sent is a set of tuples of the form (dependency, (lex-head,pos-head,index-head), (lex-child,pos-child,index-child)"""

		self.nodes = []

		for sent in sents:
			self.nodes.append(self._procSent(sent))
	
	def _procSent(self,sent):
		
		#keep a store of all the recognized nodes
		store = []

		while sent:
			current = sent.pop(0)

			dep, head, child = current[0], current[1], current[2]

			h_index = float(head[2])
			c_index = float(child[2])

			checkHeadExists = self._fetchByIndex(h_index, store)
			checkChildExists = self._fetchByIndex(c_index, store)

			head = checkHeadExists or Node(head)
			child = checkChildExists or Node(child)
			
			if not checkHeadExists: store.append(head)
			if not checkChildExists: store.append(child)

			head.add_dependent(child, dep)

		return self._fetchByIndex(0, store)
			

	def _fetchByIndex(self, index, store):
		
		for x in store: 
			if x.idx == index:
				return x


class Node:

	def __init__(self, triple):
		
		self.text = triple[0] 
		self.head = None 
		self.dep_ = None 
		self.idx = float(triple[2])
		self.pos_ = triple[1]
		self.children = [] 

	def is_terminal(self):
		return not self.children
	
	def is_root(self):
		return not self.head
	
	def set_children(self, children):
		self.children = children
	
	def get_child(self, deplabel):
		"""return the child with the deplabel, if there is one; otherwise return None
		   TODO: adapt if there is a need to access multiple children with the same label
		"""
		for c in self.children:
			if c.dep_ == deplabel:
				return c
	
	def get_coverage(self):
		"""get the text representation of what is dominated by this node"""
		return ' '.join([(lambda y: y[0])(x) for x in  sorted(self._get_coverage(), key=lambda x:x[1])])

	def _get_coverage(self, first = True):
		"""collect what is covered by the node into a list of pairs [[text,idx]...]"""

		if self.is_terminal():
			return [[self.text, self.idx]]
		else:
			if not first:
				store = [[self.text, self.idx]]
			else:
				store = []

			for child in self.children:
				store += child._get_coverage(False)

			return store

	def get_coverage_inc(self):
		"""get the text representation of what is dominated by this node including itself"""
		return ' '.join([(lambda y: y[0])(x) for x in  sorted(self._get_coverage(False), key=lambda x:x[1])])


	def find_nodes(self, dir='down', **properties):
		"""fetch all the nodes in the tree that fulfill the properties 
		   E.g. node.find_nodes(text='than', dep_='acomp') returns all the nodes in the tree
		   whose text is 'than' and dep_ is 'acomp' -- you can have as many properties as you like.
		   set dir ('down' or 'up') according to the direction you want.
		"""
		store = []
		self._find_nodes(store, dir, properties)
		return store

	def _find_nodes(self, store, dir, properties):

		if self._match_properties(properties):
			store += [self]

		if dir == 'down':
			for child in self.children: 
				child._find_nodes(store, dir, properties)
		else:
			head = self.head
			if head:
				self.head._find_nodes(store, dir, properties)

	
	def _match_properties(self, dict):

		for key in dict.keys():
			value_we_have = eval("self."+key)
			value_wanted = dict[key]
			if type(value_wanted) is list: 
				if not value_we_have in value_wanted:
					return False
			else:
				if value_we_have != value_wanted: 
					return False

		return True

	
	def fetch(self, *path):
		"""fetch the node that can be reached following the *path, if exists.
		   The default direction is to go down (to children); if you want to search up,
		   add '!' in front of the dependency label.

		   E.g. node.fetch('!dobj', 'prep') checks whether the node is the dobj child
		   of a parent which has a prep child, and returns that child if exists.
		"""
		return self._fetch(self, list(path))
	
	def _fetch(self, node, path):
		if not path:
			return node
		else:
			label = path[0]
			if label[0] == '!':
				if node.dep_ == label[1:]: 
					return self._fetch(node.head,path[1:])
				else:
					return None
			else:
				match = node.get_child(label)
				if match:
					return self._fetch(match,path[1:])
				else:
					return None

	def pprint(self, level=0):
		if self.is_terminal(): 
			self._pprint(level)
		else:
			self._pprint(level)
			for c in self.children:
				c.pprint(level+1)

	def _pprint(self,level):
		try:
			headindex = self.head.idx
		except AttributeError:
			headindex = -1

		print(level*"\t", self.dep_, self.idx, self.text)


	def add_dependent(self,node,deprel):
		"""Add node as a dependent with the dependency relation deprel""" 
		node.dep_ = deprel
		node.head = self

		position = len(self.children) - 1

		for i in range(position):
			if self.children[i].idx > node.idx:
				position = i
				break

		self.children.insert(position, node)

	def remove_dependent(self,node):
		"""Remove the dependent node"""
		try:
			self.children.remove(node)
		except ValueError:
			sys.stderr.write("Attempt to remove a non-existing dependent from node " + self.text + "\n")
	
	def detect_comparative(self):

		than_node = self.find_nodes(text = 'than', dep_ = 'case')
		if not than_node:
			return False
		else:
			than_node = than_node[0]

		type_node = than_node.head.head

		type_pos = type_node.pos_
		
		#ADJECTIVAL
		if type_pos == 'JJR' or (type_pos == 'JJ' and type_node.find_nodes(pos_ = ['RBR','JJR'], dep_ = 'advmod')):
			return 'ADJECTIVAL'
		#NOMINAL
		elif type_pos.startswith('NN'):
			if type_node.fetch('amod', 'advmod') and type_node.fetch('amod', 'advmod').pos_ == 'RBR':
				return 'NOMINAL'
			elif type_node.fetch('amod') and type_node.fetch('amod').pos_ == 'JJR':
				return 'NOMINAL'
			elif type_node.fetch('amod') and type_node.fetch('amod').pos_ == 'RBR': #for idiomatics
				return 'NOMINAL'
		else:
			return False
			
			
	def _check_pp_comp(self):

				for c in self.children:
					if c.pos_ == 'IN' and c.text != 'than':
						return True
		
				return False

	def fix(self):

		ctype = self.detect_comparative()

		if not ctype:
			return False
		
		print(self.get_coverage())
		
		ctype = self.detect_comparative()

		than_node = self.find_nodes(text = 'than', dep_ = 'case')[0]
		ccomp = than_node.head

		# check if the head of than has another prep dependent
		pp_than = ccomp._check_pp_comp()

		# find adjective or nominal
		root_node = ccomp.head

		adj_node = root_node
		# if adjectival root_node = adj_node, else nominal:	
		if ctype == 'NOMINAL':
			adj_node = root_node.fetch('amod') 

		# check analyticity
		syn = adj_node.pos_ == 'JJR'
		
		# find or form the more node
		if syn:
			index = adj_node.idx - 0.5
			more_node = Node(('more', 'RBR', index))  
			adj_node.add_dependent(more_node, 'advmod')
		else:
			try:
				more_node = adj_node.find_nodes(pos_ = ['RBR','JJR'], dep_ = 'advmod')[0]
			except AttributeError:
				sys.stderr.write('ERROR: More is not child of adjective in ADJECTIVAL')
		
		root_node.remove_dependent(ccomp)


		if pp_than:		
			pp_nom = root_node.find_nodes(pos_ = 'IN')[0]
			root_node.remove_dependent(pp_nom.head)
			more_node.add_dependent(pp_nom.head, 'Ccomp2')
		else:
			prep = ''

		more_node.add_dependent(ccomp, 'Ccomp1')

		return self

if __name__ == '__main__': 

	from optparse import OptionParser

	clparser = OptionParser()
	opts, args = clparser.parse_args()

	f = open(args[0], 'r')
	
	s = Text2Tuple(f).sentences
	c = Converter(s)


	for n in c.nodes:
		

		f = n.fix()
		if f:
			f.pprint()			

