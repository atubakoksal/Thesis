import re
import sys

SENTENCE_REGEX=r"^Sentence #[\d]+"
TOKEN_REGEX=r"^\[.*PartOfSpeech=(.*)\]"
DEPENDENCY_REGEX=r"^[a-z:]*\(.*\)"
DEPENDENCY_SPLIT_REGEX=r"([a-z:_]+)\(([\da-zA-Z%?.,-;':\\.\/!]+)-(\d+),\s+([\da-zA-Z%?.,-;':\\.\/!]+)-(\d+)\)"

def read_dependencies(filename):
	dependencies = []
	with open(filename, "r") as target:
		tags = []
		deps = []
		for line in target:
			sentence = re.match(SENTENCE_REGEX, line)
			token = re.match(TOKEN_REGEX, line)
			dependency = re.match(DEPENDENCY_REGEX, line)
			if sentence:
				if deps:
					dependencies.append((deps, tags))
				tags = []
				deps = []
			elif token:
				tag = token.group(1)
				tags.append(tag)
			elif dependency:
				dep = dependency.string.strip()
				deps.append(dep)
	dependencies.append((deps, tags))			
	return dependencies

def unify_dependencies(dependencies):
	converted_dependencies = []
	for deps, tags in dependencies:
		deps_new = []
		for dep in deps:
			rel, head, hid, child, cid = re.match(DEPENDENCY_SPLIT_REGEX, dep).groups()
			head_tag = tags[int(hid)-1] if int(hid)-1 >= 0 else ""
			child_tag = tags[int(cid)-1] if int(cid)-1 >= 0 else ""
			if head.lower() == "root":
				new_dep = "{}({}-{}, {}/{}-{})".format(rel, head, hid, child, child_tag, cid)
			else:
				new_dep = "{}({}/{}-{}, {}/{}-{})".format(rel, head, head_tag, hid, child, child_tag, cid)
			deps_new.append(new_dep)
		converted_dependencies.append(deps_new)
			
	return converted_dependencies

def write_dependencies(outfile, dependencies):
	with open(outfile, "w") as target:
		for deps in dependencies:
			for dep in deps:
				target.write(dep+"\n")
			target.write("\n")


if __name__=="__main__":
	if len(sys.argv) != 3:
		print("Usage : python stanfordDepConverter.py infile outfile")
		exit(0)
	infile = sys.argv[1]
	outfile = sys.argv[2]
	raw_dependencies = read_dependencies(infile)
	dependencies = unify_dependencies(raw_dependencies)
	write_dependencies(outfile, dependencies)