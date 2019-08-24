
#!/usr/bin/python3

def build_semantics(node):

	than_node = node.find_nodes(text = 'than', dep_ = 'case')[0]
    
	if than_node.head._check_pp_comp(): 
		return pp_semantics(node)
	else:
		return nonpp_semantics(node)

def pp_semantics(node):

	more_node = node.find_nodes(text = ['more', 'less'])[0]
	#for adjectival
	adj_node = more_node.head
	#for nominal
	nom_node = ''
	if adj_node.head.pos_.startswith('NN'):
		nom_node = adj_node.head
	
	standard = more_node.find_nodes(dep_ = 'Ccomp1')[0]
	standard = standard.get_coverage_inc()
	standard = standard.split(' ')
	standard.remove('than')
	standard = ' '.join(standard)
	
	target = more_node.find_nodes(dep_ = 'Ccomp2')[0]
	target = target.get_coverage_inc() 

	#for nominal
	if nom_node:
		frame = nom_node.find_nodes(dep_ = 'nsubj')[0]
		frame = frame.get_coverage_inc()
	
		dimension = adj_node.text + ' ' + nom_node.text
		#if there is "not"
		if nom_node.fetch('neg'):
			direction = 'NOT ' + more_node.text
		else:
			direction = more_node.text
	else: #for adjectival
		frame = adj_node.find_nodes(dep_ = 'nsubj')[0]
		frame = frame.get_coverage_inc() 

		dimension = adj_node.text
		#if there is "not"
		if adj_node.fetch('neg'):
			direction = 'NOT ' + more_node.text
		else:
			direction = more_node.text
	
	result = {'standard' : standard, 'target' : target, 'frame:' : frame, 'dimension' : dimension, 'direction' : direction}
		
	return result

def nonpp_semantics(node):

	more_node = node.find_nodes(text = ['more', 'less'])[0]
	#for adjectival
	adj_node = more_node.head
	#for nominal
	nom_node = ''
	if adj_node.head.pos_.startswith('NN'):
		nom_node = adj_node.head
	
	standard = more_node.find_nodes(dep_ = 'Ccomp1')[0]
	standard = standard.get_coverage_inc()
	standard = standard.split(' ')
	standard.remove('than')
	standard = ' '.join(standard)

	#for nominal
	if nom_node:
		target = nom_node.find_nodes(dep_ = 'nsubj')[0]
		target = target.get_coverage_inc() 
		dimension = adj_node.text + ' ' + nom_node.text
		#if there is "not"
		if nom_node.fetch('neg'):
			direction = 'NOT ' + more_node.text
		else:
			direction = more_node.text
	else:#for adjectival
		target = adj_node.find_nodes(dep_ = 'nsubj')[0]
		target = target.get_coverage_inc() 
		dimension = adj_node.text
		#if there is "not"
		if adj_node.fetch('neg'):		
			direction = 'NOT ' + more_node.text
		else:
			direction = more_node.text

	result = {'standard' : standard, 'target' : target, 'dimension' : dimension, 'direction' : direction}
		
	return result

if __name__ == '__main__': 

	from converter import *
	from optparse import OptionParser

	clparser = OptionParser()
	opts, args = clparser.parse_args()

	f = open(args[0], 'r')
	
	sentences = Text2Tuple(f).sentences
	converted = Converter(sentences)

	for n in converted.nodes:	
		f = n.fix()
		if f:
			f.pprint()
			r = build_semantics(f)
			print(r)
			print("------------------------------")

	
