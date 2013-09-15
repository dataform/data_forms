# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

%load_ext autoreload
%autoreload 2

# <codecell>

import ml_lit_anal as ml
import re
import nltk
import pickle
import operator
import google_scholar_parser as gs
import pandas as pd
import networkx as nx
import itertools
import matplotlib.pyplot as plt
import numpy as np

# <codecell>

def sorted_map(map): return sorted(map.iteritems(), key=lambda (k,v): (-v,k))

# <codecell>

df = ml.load_records('data/')
print('There are %s records in the dataset'%df.shape[0])

#clean topics
df = ml.clean_topics(df)

# <markdowncell>

# # Co-word analysis of the machine learning literature
# 

# <codecell>

#choose the set of keywords to use
de_all = [d for de in df.topics.dropna() for d in de]
de_set = set(de_all)
de_counts = {de:de_all.count(de) for de in de_set}
	#de_counts_sorted = sorted(de_counts.iteritems(), key = operator.itemgetter(1), reverse=True)

# <codecell>

	# choose top 500 keywords
keys = [t[0] for t in de_counts.items() if t[1] > 10]
print('there are %s keywords' % len(keys))

# <codecell>

# construct the coword matrix by counting how often keywords appear with each other
cow_df = ml.coword_matrix(df,keys)

# <markdowncell>

# For co-word analysis, calculate a matrix of equivalence scores and look for largest values. I'm drawing on Callon M, Courtial JP and Laville F (1991) Co-word analysis as a tool for describing the network of interactions between basic and technological research: The case of polymer chemsitry. Scientometrics, 22(1), 155–205 for this. 
# 
# They write:
# 
# > The calculation of all coefficients between all possible word pairs (even if the
# value of these coefficients is often equal to zero) generates a considerable number of
# links - far too many to able to represent graphically. This is why we have developed
# algorithms for generating sub-groups that can be more easily visualized and
# interpreted. 161
# 
# Much of their method is devoted to better ways of dealing with the proliferation of links. I'm not sure we have the same problem today, because of machine learning. 

# <codecell>

eqcow_df = ml.equivalence_matrix(cow_df, de_counts)
eq2 = eqcow_df.unstack().copy()
eq2.sort(ascending=False)
eq2[:100:2]

# <codecell>

eq2.hist(bins=500)

# <markdowncell>

# Classic coword analysis looks for clusters using thresholds. 

# <codecell>

eqnx = nx.from_numpy_matrix(eqcow_df.as_matrix())

# <codecell>

eqnx.number_of_nodes()
nx.draw_spring(eqnx, node_size=30)

# <markdowncell>

# ## Development analysis
# 
# The problem is that I'm keeping 25 years of research together. There is no chance of looking at development, or seeing relationships. 
# Before 1990, there are very few machine learning papers (less than 100). So the first snapshot could be 1990

# <codecell>

df_pre = df[df.PY <=1990]

print('There are %s papers by the end of 1990'%df_pre.shape[0])

# <markdowncell>

# There are very few abstracts in this collection, and as we will see, not too many keywords. So might need to use titles 

# <codecell>

df.TI.drop_duplicates()

# <codecell>

pre_90_keys = ml.keyword_counts(df_pre)
pre_90_keys

# <markdowncell>

# The problem is that most of the literature before 1990 have no keywords. They were not keyworded by anyone. But for those that are:

# <codecell>

print('The number of pre-1990 references that have keyword: %s'%df_pre.topics.count())
cow_df1 = ml.coword_matrix(df_pre, pre_90_keys.keys())
cow_df1.head()
pre_90_nx = nx.from_numpy_matrix(cow_df1.as_matrix())
cols = cow_df1.columns.tolist()

labels = {cols.index(l):l for l in cols}
pos = nx.spring_layout(pre_90_nx)
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(12.5,12.5)
fig.set_label('Pre-1990 keywords and their relations')

nx.draw(pre_90_nx, pos=pos, alpha=0.5, node_size=50, with_labels=True, labels=labels)
#nx.draw_networkx_labels(pre_90_nx, pos=pos,labels = labels, font_size=9)

# <markdowncell>

# What is slightly interesting here are the two different networks around learning and machine learning. But this is all based on a handful of references, so there is little point going further with it. 
# 
# # How do things go after 1990? The 1990- 1995 analysis
# 

# <codecell>

df_pre2 = df[(df.PY <= 1995) & (df.PY >1990)]
keys_90_95 = ml.keyword_counts(df_pre2)
print('There are %s keywords in the 1990-95 literature' % len(keys_90_95))

# <codecell>

cow_df2 = ml.coword_matrix(df_pre2,keys_90_95.keys())
arry = cow_df2.as_matrix()
np.fill_diagonal(arry, 0)
pre_95_nx = nx.from_numpy_matrix(arry)
cols = cow_df2.columns.tolist()

# <codecell>

labels = {cols.index(l):l for l in cols}
pos = nx.spring_layout(pre_95_nx)
fig = matplotlib.pyplot.gcf()
fig.set_size_inches(10.5,10.5)
fig.set_label('Pre-1995 keywords and their relations')

nx.draw(pre_95_nx, pos=pos, alpha=0.5, node_size=50, with_labels=False, labels=labels)

# <markdowncell>

# This is a much more complicated structure. This couple of dozen keywords have morphed into hundres and there is some degree of structure here. 

# <codecell>

degree_c = nx.degree_centrality(pre_95_nx)
degree_cs = sorted_map(degree_c)
degree_cs

# <codecell>

pre_95_nx_trim = ml.trim_degrees(pre_95_nx, 12)
len(pre_95_nx_trim.nodes())

# <codecell>

labels_trimmed = {n:labels[n] for n in pre_95_nx_trim.nodes()}
len(labels_trimmed)

# <codecell>

fig = matplotlib.pyplot.gcf()
fig.set_size_inches(12.5,12.5)
nx.draw(pre_95_nx_trim,  alpha=0.5, node_size=50, with_labels=True, labels= labels_trimmed)

# <markdowncell>

# Not entirely clear what is happening here, a couple of things stand out. There are all the database-mining, bridge design(!), knowledge-discovery, image-processing, fault diagnosis, information retrieval, as well as quite a lot on the epistemology of learning -- inductive inference, learning from examples, etc. Pattern recognition and decision support are quite important. 
# In terms of particular techniques, neural networks, decision trees and interestingly id3 (need to check that one out).  As well as some that would seem odd now -- genetic algorithms, self-organization and fuzzy sets. 

# <markdowncell>

# The presence of these particular algorithms -- neural networks, decision tree and id3 would be worth tracking more over time. These techniques might need to be treat in their own right. 

# <markdowncell>

# # Can't remember what this section was meant to do ... 

# <codecell>

print(cow_df2.ix[1:4,1:4])
c2 = cow_df2.unstack().copy()
c2.describe()
c2[c2>1].hist(bins=200)

# <codecell>

c2.index[1]
G = nx.Graph()
c2.index[0]
[G.add_edge(st[0], st[1], weight =w)  for (st, w) in zip(c2.index, c2)]

# <codecell>

fig = matplotlib.pyplot.gcf()
fig.set_size_inches(12.5,12.5)

elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] >=2]
esmall=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <=1]

pos=nx.spring_layout(G) # positions for all nodes


# nodes
nx.draw_networkx_nodes(G,pos,node_size=70)

# edges
nx.draw_networkx_edges(G,pos,edgelist=elarge, width=6)
#nx.draw_networkx_edges(G,pos,edgelist=esmall,width=6,alpha=0.5,edge_color='b',style='dashed')

# labels
l = nx.draw_networkx_labels(G,pos,font_size=9,font_family='sans-serif')

# <codecell>

#construct node list for all edges with weight greater than 1
nodel =[[e[0], e[1]] for e in G.edges_iter(data=True) if e[2]['weight'] >2 ]
nodes = list({v for i in nodel for v in i})

# <codecell>

fig = matplotlib.pyplot.gcf()
fig.set_size_inches(12.5,12.5)

elarge=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] >=2]
#esmall=[(u,v) for (u,v,d) in G.edges(data=True) if d['weight'] <=1]

pos=nx.spring_layout(G) # positions for all nodes


# nodes
nx.draw_networkx_nodes(G,pos,node_size=70, nodelist=nodes)

# edges
nx.draw_networkx_edges(G,pos,edgelist=elarge, width=2)
#nx.draw_networkx_edges(G,pos,edgelist=esmall,width=6,alpha=0.5,edge_color='b',style='dashed')

# labels
l = nx.draw_networkx_labels(G,pos,font_size=9,font_family='sans-serif')

# <markdowncell>

# TBC: look at the development of keywords over later years

# <markdowncell>

# ## 1995- 2000 keywords

# <codecell>

df_pre3 = df[(df.PY > 1995) & (df.PY <= 2000)]
keys_pre_2000 = ml.keyword_counts(df_pre3)
print('There are %s keywords in the 1995-2000 literature' % len(keys_pre_2000))

# <codecell>

cow_df3 = ml.coword_matrix(df_pre2,keys_pre_2000.keys())

# <codecell>

arry = cow_df3.as_matrix()
np.fill_diagonal(arry, 0)
pre_2000_nx = nx.from_numpy_matrix(arry)
cols = cow_df3.columns.tolist()

# <codecell>

nx.draw(pre_2000_nx)

# <codecell>

pre_2000_nx_trim = ml.trim_degrees(pre_2000_nx, 1)
len(pre_2000_nx_trim.nodes())

# <markdowncell>

# ## Digression: Support Vector Machine & Neural Networks over time
# 
# I wanted to see how these two techniques have changed over time. 

# <codecell>

##beginning of svm

nn_df = ml.keyword_years(df, 'neural network')
nn_df.PY.hist(bins=23, alpha=0.5)
svm_df = ml.keyword_years(df, 'support vector machine')
svm_df.PY.hist(bins=15,alpha=0.7)
dt_df = ml.keyword_years(df, 'decision tree')
dt_df.PY.hist(bins=23)

# <codecell>

svm_df_full = df.ix[svm_df.index]
print(svm_df_full.shape)
svm_keys = ml.keyword_counts(svm_df_full)
print('There are %d keywords associated with "support vector machine"' % len(svm_keys))

# <codecell>

svm_keys

# <markdowncell>

# This is pretty amazing -- only 14000 of the 23000 references have keywords, so if 1400 or so have svm as a keyword, then it is a heavily used technique. Also there are lots of keywords associated with svm. 

# <markdowncell>

# Compare with this with neural networks:

# <codecell>

nn_df_full = df.ix[nn_df.index]
print(nn_df_full.shape)
nn_keys = ml.keyword_counts(nn_df_full)
print('There are %d keywords associated with "neural network"' % len(nn_keys))

# <markdowncell>

# I guess the picture is much the same. What about the 'decision tree?'

# <codecell>

dt_df_full = df.ix[dt_df.index]
print(dt_df_full.shape)
dt_keys = ml.keyword_counts(dt_df_full)
print('There are %d keywords associated with "decision tree"' % len(dt_keys))

# <markdowncell>

# Ok, for decision tree, a much older technique, things look different. Still quite a few keywords, but the less than half for the other techniques. This is not to say that decision trees are not incredibly widely used. But they are not being relayed in the same way through the literature. 
# 
# To deal too many keywords, break into a couple of time periods.

# <codecell>

svm_keys_pre_2000 = ml.keyword_counts(svm_df_full[svm_df_full.PY<2001])
svm_keys_pre_2000

# <codecell>

cow_svm = ml.coword_matrix(svm_df_full[svm_df_full.PY<2001],svm_keys_pre_2000.keys())
arry = cow_svm.as_matrix()
arry.shape

svm_nx = nx.from_numpy_matrix(arry)
cols = cow_svm.columns.tolist()

# <codecell>

cols

# <codecell>

fig = matplotlib.pyplot.gcf()
fig.set_size_inches(8.5,8.5)
labels = {cols.index(l):l for l in cols}
nx.draw_spring(svm_nx, with_labels=True, labels = labels, font_size=10,font_family='sans-serif')

# <markdowncell>

# Between 2000- 2005, there is much growth. 

# <codecell>

svm_keys_2001_on = ml.keyword_counts(svm_df_full[(svm_df_full.PY >= 2001) & (svm_df_full.PY <2003)])
cow_svm = ml.coword_matrix(svm_df_full[(svm_df_full.PY >= 2001) & (svm_df_full.PY <2003)],svm_keys_2001_on.keys())
arry = cow_svm.as_matrix()
arry.shape

svm_nx = nx.from_numpy_matrix(arry)
cols = cow_svm.columns.tolist()

# <codecell>

fig = matplotlib.pyplot.gcf()
fig.set_size_inches(12.5,14.5)
labels = {cols.index(l):l for l in cols}
nx.draw_spring(svm_nx, with_labels=True, labels = labels, font_size=9,font_family='sans-serif')

# <codecell>

