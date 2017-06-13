# from texch.preprocessing.base import PreprocessStep
# from texch.similarity.ast import Tree, suffix, subtree, IDF
#
#
# class SuffixTreeSimMatrixFromFreqDist(PreprocessStep):
#     verbose_name = 'Suffix Tree Similarity Matrix from FreqDists'
#
#     def _create_trees(self, n_most_common):
#         trees = []
#         for num_text, text in enumerate(self.input_data):
#             tree = Tree(suffix)
#             compressed_text = text.most_common(n_most_common)
#             for value, freq in compressed_text:
#                 tree.add(' '.join(value), freq)
#             trees.append(tree)
#             tree.get_chains()
#         return trees
#
#     def process(self, n_most_common=None):
#
#         trees = self._create_trees(n_most_common)
#
#         sim = []
#
#         general_tree = Tree(suffix)
#         for num_text, text in enumerate(self.input_data):
#             for token in text:
#                 # n-grams
#                 if isinstance(token, (tuple, list)):
#                     value = ' '.join(token)
#                 else:
#                     value = token
#                 general_tree.add(value)
#         for i, tokens in enumerate(self.input_data):
#             t1 = trees[i]
#             # scoring1 = len(t1.chains)
#             for j in xrange(i, len(self.input_data)):
#                 t2 = trees[j]
#                 t3 = Tree(suffix)
#                 subtree(t1, t2, t3, t1.root, t2.root, t3.root)
#                 IDF(t3, general_tree, t3.root, general_tree.root)
#                 t3.get_chains()
#                 t3.score_tree('mean', 'mean', 'yes')
#                 sim[i][j] = t3.scoring
#                 sim[j][i] = sim[i][j]
#         return sim
#
#
# class SuffixTreeSimMatrixFromTokens(PreprocessStep):
#     verbose_name = 'Suffix Tree Similarity Matrix from Tokens'
#
#     def _create_trees(self, n_features):
#         trees = []
#         for num_text, text in enumerate(self.input_data):
#             tree = Tree(suffix)
#             if n_features is not None:
#                 text = text[:n_features]
#             for value, freq in text:
#                 tree.add(' '.join(value))
#             trees.append(tree)
#             tree.get_chains()
#         return trees
#
#     def process(self, n_features=None):
#
#         trees = self._create_trees(n_features)
#
#         sim = []
#
#         general_tree = Tree(suffix)
#         for num_text, text in enumerate(self.input_data):
#             for token in text:
#                 general_tree.add(token)
#         for i, tokens in enumerate(self.input_data):
#             t1 = trees[i]
#             # scoring1 = len(t1.chains)
#             for j in xrange(i, len(self.input_data)):
#                 t2 = trees[j]
#                 t3 = Tree(sufr fix)
#                 subtree(t1, t2, t3, t1.root, t2.root, t3.root)
#                 IDF(t3, general_tree, t3.root, general_tree.root)
#                 t3.get_chains()
#                 t3.score_tree('mean', 'mean', 'yes')
#                 sim[i][j] = t3.scoring
#                 sim[j][i] = sim[i][j]
#         return sim
