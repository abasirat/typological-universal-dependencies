import pyconll
import sys

input_path = sys.argv[1]
output_path = sys.argv[2]

corpus = pyconll.load_from_file(input_path)
for sentence in corpus:
	for token in sentence:
		croftdep = token.deprel
		if croftdep != None:
			if 'nsubj' in croftdep:
				croftdep = croftdep.replace('nsubj', 'sbj')
			elif 'csubj' in croftdep:
				croftdep = croftdep.replace('csubj', 'sbj')
			elif 'iobj' in croftdep:
				croftdep = croftdep.replace('iobj', 'obj')
			elif 'ccomp' in croftdep:
				croftdep = croftdep.replace('ccomp', 'comp')
			elif 'xcomp' in croftdep:
				if token.upos == 'VERB':
					croftdep = croftdep.replace('xcomp', 'comp')
				else:
					croftdep = croftdep.replace('xcomp', 'sec')
			elif 'advmod' in croftdep:
				if 'AdvType' in token.feats.keys():
					if 'Man' in token.feats['AdvType']:
						croftdep = croftdep = croftdep.replace('advmod', 'sec')
					elif 'Deg' in token.feats['AdvType']:
						croftdep = croftdep.replace('advmod', 'qlfy')
					elif 'Mod' in token.feats['AdvType']:
						croftdep = croftdep.replace('advmod', 'aux')
					else: # including if token.feats['AdvType'] == 'Loc' or token.feats['AdvType'] == 'Tim'
						croftdep = croftdep.replace('advmod', 'obl')
				else:
					croftdep = croftdep.replace('advmod', 'obl')
			elif 'cop' in croftdep:
				croftdep = croftdep.replace('cop', 'cxp')
			elif 'nummod' in croftdep:
				croftdep = croftdep.replace('nummod', 'mod')
			elif 'amod' in croftdep:
				croftdep = croftdep.replace('amod', 'mod')
			elif 'det' in croftdep:
				croftdep = croftdep.replace('det', 'mod')
			elif 'compound' in croftdep:
				if sentence[token.head].upos == 'VERB':
					croftdep = croftdep.replace('compound', 'cxp')
		token.deprel = croftdep
with open(output_path, 'w', encoding='utf-8') as f:
    print(f"output file: {output_path}")
    corpus.write(f)
