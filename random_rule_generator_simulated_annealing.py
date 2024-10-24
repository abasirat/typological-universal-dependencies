import pyconll
from collections import Counter

import sys

import random
import math

import pdb

def objective(a, r, b, max_rules):
    """Calculate the objective function value."""

    # dealing with the relations that have appeared in several rules
    # repeated relatiosn should be excluded i.e., increase the objective
    rules = [cc for rr,cc in zip(r,candidate_rules) if rr]
    rels = [r1 for r1,r2 in rules]
    rels += [r2 for r1,r2 in rules]
    rel_cnt = [rels.count(r) for r in rels]
    #return .99*abs(sum(r[i] * a[i] for i in range(len(a))) - b) + .01*abs(sum(r) - max_rules ) + abs(sum(rel_cnt) - len(rels))
    return abs(sum(r[i] * a[i] for i in range(len(a))) - b) + abs(sum(rel_cnt) - len(rels))

def initial_state(n):
    """Generate an initial random state."""
    return [random.randint(0, 1) for _ in range(n)]

def perturb(r):
    """Generate a neighbor state by flipping one random bit."""
    neighbor = r[:]
    index = random.randint(0, len(r) - 1)
    neighbor[index] = 1 - neighbor[index]
    return neighbor

def acceptance_probability(old_cost, new_cost, temperature):
    """Calculate the acceptance probability."""
    if new_cost < old_cost:
        return 1.0
    else:
        return math.exp((old_cost - new_cost) / temperature)

def simulated_annealing(a, b, max_rules=15, max_steps=10000, initial_temp=1.0, cooling_rate=0.999):
    """Perform simulated annealing optimization."""
    n = len(a)
    current_r = initial_state(n)
    current_cost = objective(a, current_r, b, max_rules)
    temperature = initial_temp
    
    for step in range(max_steps):
        next_r = perturb(current_r)
        next_cost = objective(a, next_r, b, max_rules)
        
        if acceptance_probability(current_cost, next_cost, temperature) > random.random():
            current_r = next_r
            current_cost = next_cost
        
        temperature *= cooling_rate
        if temperature < 1e-6:  # Prevents temperature from becoming too low
            break

    return current_r

def get_relations(corpus):
    # collect all relations and calculate their marginal frequency
    rel_count = Counter()
    for snt in corpus:
        for tok in snt:
            rel = tok.deprel
            if rel is None: continue
            rel = rel.split(':')[0] # exclude subrelations

            if rel != 'root':
                rel_count[rel] += 1
    return rel_count

def apply_rules(corpus, rules):
    for snt in corpus:
        for tok in snt:
            rel = tok.deprel
            if rel is None: continue
            rel = rel.split(':')[0] # exclude subrelations
            if rel in rules.keys():
                replacement = rules[rel]
                if replacement.endswith("_expand"):
                    exp_prb = random.random()
                    if exp_prb < .33:
                        replacement += "1"
                    elif exp_prb < 0.66:
                        replacement += "2"
                    elif exp_prb < 1:
                        replacement += "3"
                    #replacement += "1" if random.random() < 0.5 else "2"
                tok.deprel = tok.deprel.replace(rel, replacement)

    return corpus



corpus_path_train = sys.argv[1]
corpus_path_dev = sys.argv[2]
corpus_path_test = sys.argv[3]

output_path_train = sys.argv[4]
output_path_dev = sys.argv[5]
output_path_test = sys.argv[6]

rule_log_file = sys.argv[7]

train_corpus = pyconll.load_from_file(corpus_path_train)
dev_corpus = pyconll.load_from_file(corpus_path_dev)
test_corpus = pyconll.load_from_file(corpus_path_test)

relations = Counter()
total = 0
for r,c in get_relations(train_corpus).items():
    relations[r] += c
    total += c

for r,c in get_relations(dev_corpus).items():
    relations[r] += c
    total += c

for r,c in get_relations(test_corpus).items():
    relations[r] += c
    total += c

# form candidate rules and estimate their probabilities
candidate_rules = []
rule_impact = [] # rule probabilities
for rel1,cnt1 in relations.most_common():
    if (rel1,"expand") not in candidate_rules:
        #expand
        candidate_rules.append( (rel1,"expand") )
        rule_impact.append( cnt1*1.0 / total)
    for rel2,cnt2 in relations.most_common():
        if rel1 != rel2:
            # merge 
            candidate_rules.append( (rel1,rel2) )
            rule_impact.append( (cnt1+cnt2)*1.0 / total )

print(f"total number of candidate rules is {len(candidate_rules)}")


# Call the function
expected_impact = 0.28
max_rules = 15
solution= simulated_annealing(rule_impact, expected_impact, max_rules)
print(f"Subsets that sum to {expected_impact}:", solution)
rules = {}
for i,((a,b),select,impact) in enumerate(zip(candidate_rules,solution,rule_impact)):
    if select == 1:
        if a not in rules.keys():
            rules[a] = f"{a}{b}"
        else:
            print("WARNING: repeated rules found")
        
        if b not in rules.keys() and b != "expand":
            rules[b] = f"{a}{b}"
        else:
            print("WARNING: repeated rules found")

logfp = open(rule_log_file, "w")
print(f"total number of candidate rules is {len(candidate_rules)}", file=logfp)
print(f"Subsets that sum to {expected_impact}:", solution, file=logfp)
print("Achieved sum:", sum(solution[i] * rule_impact[i] for i in range(len(rule_impact))))
print("Achieved sum:", sum(solution[i] * rule_impact[i] for i in range(len(rule_impact))), file=logfp)
for rel,rule in rules.items():
    print(f"{rel} -> {rule}")
    print(f"{rel} -> {rule}", file=logfp)
logfp.close()

train_corpus = apply_rules(train_corpus, rules)
dev_corpus = apply_rules(dev_corpus, rules)
test_corpus = apply_rules(test_corpus, rules)

with open(output_path_train, 'w', encoding='utf-8') as f:
	train_corpus.write(f)

with open(output_path_dev, 'w', encoding='utf-8') as f:
	dev_corpus.write(f)

with open(output_path_test, 'w', encoding='utf-8') as f:
	test_corpus.write(f)
