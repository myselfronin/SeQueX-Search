import math

class ExpansionTermRanking:
    def __init__(self):
        pass

    def semantic_similarity(A, B, ontology_tree):
        """
        Calculate the semantic similarity between two nodes based on a tree structure.

        :param A, B: Nodes in the ontology tree.
        :param ontology_tree: An object representing the ontology tree structure.
        :return: Semantic similarity score.
        """
        # Set the parameters
        alpha = 0.6
        beta = 0.2
        gamma = 0.2

        # Calculate Dist(A, B)
        dist = math.exp(-ontology_tree.shortest_path_length(A, B))

        # Calculate Depth(A, B)
        depth_A = ontology_tree.node_depth(A)
        depth_B = ontology_tree.node_depth(B)
        depth = abs(depth_A - depth_B) + 1 / (depth_A + depth_B)

        # Calculate Density(A, B)
        common_ancestor = ontology_tree.common_ancestor(A, B)
        n = len(ontology_tree.direct_children(common_ancestor))
        m = len(ontology_tree.all_children(common_ancestor))
        density = n / m if m != 0 else 0

        # Calculate the overall similarity
        similarity = alpha * dist + beta * depth + gamma * density
        return similarity