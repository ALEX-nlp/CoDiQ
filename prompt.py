de1_str = """
Dimensionality & Constraints
**🎯 Best for**: Array/Sequence/Tree problems with simple naive solutions (e.g., $O(N)$, $O(N^2)$, or $O(N^3)$).
**⚠️ Avoid when**: Original problem already requires logarithmic or sublinear complexity.
**Description**: Explode the data scale or dimensionality to invalidate simple simulation or brute force.
**Core Strategy**:
   1. **Identify** the naive complexity (e.g., $O(N)$, $O(N^2)$, or $O(N^3)$).
   2. **Impose** constraints that compel a superior complexity class (e.g., $O(\log N)$ or $O(N \log N)$).
   3. **Introduce** dynamic updates, higher-dimensional spaces, or multiple query types to break linear scans.
**Examples**:
[
    {
        "original": "Given an array of size N (N≤1000), find the sum of elements in range [L, R].",
        "upgrade": "Given an array of size N (N≤10^5), handle M (M≤10^5) operations: 1. Update range [L, R] by adding V. 2. Query sum of range [L, R]. (Requires Segment Tree with Lazy Propagation)",
        "difficulty": "Codeforces Div2 D/E"
    },
    {
        "original": "Given a grid, find the shortest path from (0,0) to (R,C) avoiding obstacles.",
        "upgrade": "Given a grid where obstacles appear and disappear at specific time intervals modulo K. Find the shortest path. (Requires BFS in State Space (x, y, time%K))",
        "difficulty": "IOI / ICPC Regional"
    },
    {
        "original": "Find the maximum value in an array.",
        "upgrade": "Given a tree with N nodes (N≤10^5), support path updates (add value V to all nodes on path u-v) and path maximum queries. (Requires Heavy-Light Decomposition)",
        "difficulty": "Codeforces Div1 D"
    },
    {
        "original": "Given a set of points, find the two closest points.",
        "upgrade": "Given a set of points in 3D space, find the size of the largest subset where every pair has Manhattan distance > D. (Requires Coordinate Transformation + Data Structures)",
        "difficulty": "ICPC World Finals"
    },
    {
        "original": "Check if a string S contains pattern P.",
        "upgrade": "Given a text S and K patterns. Support dynamic insertion of new patterns and query if any pattern appears in S. (Requires Aho-Corasick Automaton or Suffix Structures)",
        "difficulty": "Codeforces Div1 E"
    }
]
""".strip()

de2_str = """
Mathematical Abstraction
**🎯 Best for**: Problems that can be reframed into mathematical structures, e.g., simulation or iterative problems with clear patterns.
**⚠️ Avoid when**: The problem is already focused on advanced specialized theorems or complex data structures.
**Description**: Transform a procedural or descriptive problem into a formal model, e.g., using number theory, combinatorics, or game theory.
**Core Strategy**:
   1. **Increase** constraints to push beyond computational limits (e.g., $N \ge 10^{18}$), making simple iteration or simulation impossible.
   2. **Force** the discovery of underlying structures, such as closed-form formulas, recurrence relations, or invariant properties.
   3. **Introduce** formal constraints (e.g., modular arithmetic, coordinate systems) that require rigorous mathematical modeling.
**⚠️ Anti-pattern**: Simply making N large without ensuring a mathematical insight exists is not valid.
**Examples**:
[
    {
        "original": "Simulate a process where bacteria double every hour. Find count at hour N (N≤50).",
        "upgrade": "Bacteria have a complex growth rule F(n) = a*F(n-1) + b*F(n-2). Find count at hour N (N≤10^18) modulo 10^9+7. (Requires Matrix Exponentiation)",
        "difficulty": "Codeforces Div2 D"
    },
    {
        "original": "Given N items, in how many ways can you pick K items?",
        "upgrade": "Given N items with specific color constraints, calculate the number of ways to pick K items modulo 10^9+7 where N is up to 10^9. (Requires Lucas Theorem or Generating Functions)",
        "difficulty": "ICPC Regional"
    },
    {
        "original": "Two players take turns removing 1-3 stones. Who wins?",
        "upgrade": "Played on a graph with N≤10^5 nodes. A token moves along edges. A player loses if they cannot move. The graph has cycles. (Requires Game Theory on Graphs / Sprague-Grundy with loop handling)",
        "difficulty": "IOI / Codeforces Div1 D"
    },
    {
        "original": "Calculate the Greatest Common Divisor (GCD) of two numbers.",
        "upgrade": "Calculate the sum of GCD(i, j) for all 1 ≤ i, j ≤ N where N≤10^7. (Requires Euler Totient Function / Mobius Inversion)",
        "difficulty": "Codeforces Div1 C/D"
    },
    {
        "original": "Find the area of a polygon given integer coordinates.",
        "upgrade": "Given N lines in the plane, find the area of their union region accurately. Handle parallel and concurrent lines. (Requires Integration logic or Green's Theorem application)",
        "difficulty": "ICPC World Finals"
    }
]
""".strip()

de3_str = """
Inverse & Constructive
**🎯 Best for**: Problems with well-defined algorithms and a clear "input → algorithm → output" flow.
**⚠️ Avoid when**: The original problem's core challenge is already in the "design/construction" phase rather than "computation/processing" (i.e., problems that lack a standard algorithm to reverse).
**Description**: Instead of asking for the result of a process, ask for the input that produces a specific result.
**Core Strategy**:
   1. **Reverse** the problem direction: from "Given X, find Y" to "Construct X such that Y holds".
   2. **Require** understanding of structural properties (e.g., what makes a graph have a specific flow?).
   3. **Add** multiple constraints to make construction non-trivial.
**Examples**:
[
    {
        "original": "Given a graph, find the shortest path from A to B.",
        "upgrade": "Construct a graph with N vertices and M edges such that the shortest path from 1 to N is exactly L, and the MST weight is exactly W.",
        "difficulty": "Codeforces Div2 E"
    },
    {
        "original": "Sort an array using QuickSort.",
        "upgrade": "Construct a permutation of size N that causes a standard QuickSort implementation (with first element as pivot) to hit its worst-case O(N^2) time complexity.",
        "difficulty": "ICPC Regional"
    },
    {
        "original": "Given a binary tree, print its pre-order traversal.",
        "upgrade": "Given the pre-order and post-order traversals, reconstruct all possible binary trees. Determine if the solution is unique or count how many such trees exist.",
        "difficulty": "Codeforces Div2 D"
    },
    {
        "original": "Check if a string is a palindrome.",
        "upgrade": "Construct a string of length N containing exactly K distinct palindromic substrings. Prove that no such string exists if K exceeds a certain bound.",
        "difficulty": "IOI / Codeforces Div1 D"
    },
    {
        "original": "Find the maximum flow in a network.",
        "upgrade": "Given a desired max flow value F, construct a network with minimum edges that achieves this flow, subject to capacity constraints on each edge.",
        "difficulty": "ICPC World Finals"
    }
]
""".strip()

de4_str = """
State Explosion
**🎯 Best for**: Problems with simple, polynomial DP states that can be enriched.
**⚠️ Avoid when**: The original state space is already exponential (e.g., TSP); adding dimensions would make it computationally infeasible.
**Description**: Add complex dependencies or history requirements that necessitate advanced Dynamic Programming or Network Flow by expanding the state space.
**Core Strategy**:
   1. **Redefine** the state: move from simple states (e.g., `dp[i]`) to composite, multi-dimensional states (e.g., adding an exponential `mask` for sets or a polynomial `remainder` for constraints).
   2. **Introduce** constraints that depend on past choices or specific history (e.g., "cannot visit a node visited k steps ago," requiring a sliding window or history state).
   3. **Add** multiple orthogonal restrictions (e.g., count, parity, or modularity) that must be tracked simultaneously.
**⚠️ Anti-pattern**: Simply adding variables that don't interact. The new dimensions must fundamentally change the recurrence logic or transition dependencies.
**Examples**:
[
    {
        "original": "Climb stairs taking 1 or 2 steps. How many ways?",
        "upgrade": "Cover a 3×N grid with 1×2 dominoes. How many ways modulo 10^9+7? (Requires Broken Profile DP / Bitmask DP to track cross-section state)",
        "difficulty": "Codeforces Div1 C/D"
    },
    {
        "original": "Knapsack Problem: Max value with weight limit W.",
        "upgrade": "Knapsack on a Tree: Each node has value/weight. Max value by selecting nodes such that no two selected nodes are adjacent, and total weight ≤ W. (Requires Tree DP + Knapsack dimensions)",
        "difficulty": "ICPC Regional"
    },
    {
        "original": "Longest Increasing Subsequence in an array.",
        "upgrade": "Count the number of permutations of length N that have a Longest Increasing Subsequence of length exactly K. (Requires DP with Young Tableaux or RSK correspondence)",
        "difficulty": "IOI / ICPC World Finals"
    },
    {
        "original": "Find min cost to traverse a grid.",
        "upgrade": "Find min cost to traverse a grid with K 'batteries' to jump obstacles; recharge depends on grid value modulo M, and cells must be unlocked in order. (State: position + battery_count + mod_state + lock_mask)",
        "difficulty": "Codeforces Div1 E"
    },
    {
        "original": "Edit Distance between two strings.",
        "upgrade": "Given strings A and B, find the number of strings S of length L such that EditDistance(A, S) ≤ K and EditDistance(B, S) ≤ K. (Requires DP on DP / Automaton DP)",
        "difficulty": "ICPC World Finals"
    }
]
""".strip()

de5_str = """
Theorem Disguise
**🎯 Best for**: Problems that can map to classic high-level algorithms but appear in unrelated or abstract domains.
**⚠️ Avoid when**: The original problem explicitly mentions the algorithm or data structure.
**Description**: Hide a sophisticated algorithmic core behind a narrative or alternative mathematical structure that misleads intuition.
**Core Strategy**:
   1. **Map** the problem to a well-known non-trivial algorithm (e.g., Network Flow, Linear Basis, Generating Functions, or Advanced DS).
   2. **Remove** all technical terminology and explicit constraints that hint at the solution.
   3. **Create** a "Red Herring" narrative that suggests an intuitive but suboptimal approach (e.g., Greedy, simple DP, or naive Simulation).
   4. **Ensure** the bridge between the surface problem and the hidden theorem requires a deep structural insight.
**Examples**:
[
    {
        "original": "Find the maximum number of meetings one can attend.",
        "upgrade": "Given a set of intervals, color them with minimum colors so no overlapping intervals share a color. Some intervals are 'VIP' and must use specific colors. (Disguised as Greedy, actually Interval Graph Coloring / Dilworth's Theorem with constraints)",
        "difficulty": "Codeforces Div2 E"
    },
    {
        "original": "Can we partition an array into two equal sum subsets?",
        "upgrade": "Given a graph, determine if it is bipartite. If not, remove minimum edges to make it bipartite while preserving connectivity. (Disguised Graph Theory, actually Odd Cycle Transversal / Max Cut variant)",
        "difficulty": "ICPC Regional"
    },
    {
        "original": "Assign tasks to workers to minimize total time.",
        "upgrade": "N workers and M tasks. Each pair (worker, task) has a cost. Some workers conflict and cannot work simultaneously. Minimize total cost. (Disguised Minimum Cost Maximum Flow with conflict resolution)",
        "difficulty": "Codeforces Div1 D"
    },
    {
        "original": "Find the maximum number of compatible intervals.",
        "upgrade": "Given a circle with N chords represented by their endpoints. Find the maximum number of non-intersecting chords. (Disguised DP on Circle Graph or Catalan-related structure)",
        "difficulty": "IOI"
    },
    {
        "original": "Find a number in an array that appears more than N/2 times.",
        "upgrade": "Given a stream of N elements, find all elements appearing more than N/K times using O(K) space and one pass. Handle K up to 10^3. (Disguised Boyer-Moore Voting generalized / Misra-Gries Algorithm)",
        "difficulty": "ICPC World Finals"
    }
]
""".strip()

de6_str = """
Edge Case & Rigor Engineering
**🎯 Best for**: Problems with simple logic but tricky implementation details.
**⚠️ Avoid when**: The original problem is already highly technical or implementation-heavy.
**Description**: Focus on logical pitfalls, geometric precision, tricky edge cases, or requiring formal proof for correctness.
**Core Strategy**:
   1. **Target** weaknesses of standard data types (e.g., float precision, integer overflow, empty sets).
   2. **Introduce** degenerate cases (e.g., disconnected graphs, collinear points, zero denominators).
   3. **Require** strict mathematical proofs (like "Exchange Arguments") to justify a strategy where intuition fails.
   4. **Add** precision constraints (e.g., "answer accurate to 10^-9") or handle extreme ranges.
**Examples**:
[
    {
        "original": "Given coordinates of 3 points, calculate the area of the triangle.",
        "upgrade": "Given N (N≤10^5) lines in a plane. Find the area of the finite region formed by their intersection. Handle parallel lines, lines at infinity, and precision errors. (Requires Half-plane Intersection with strict boundary handling and epsilon comparison)",
        "difficulty": "ICPC World Finals"
    },
    {
        "original": "Find if there is a path from A to B in a graph.",
        "upgrade": "Find if A reaches B. The graph may contain self-loops, multiple edges, and consists of up to 10^5 disconnected components. Answer 10^5 online queries. Handle the case where A=B and the case where A or B doesn't exist. (Tests Edge Cases: Connectivity, Disjoint Set Union with path compression, query validation)",
        "difficulty": "Codeforces Div2 D"
    },
    {
        "original": "Divide A by B.",
        "upgrade": "Divide A by B where A and B are strings representing integers up to 10^1000. Handle B=0, negative signs, leading zeros, and output the quotient and remainder. Prove your division algorithm's correctness. (Requires BigInteger Implementation + comprehensive Edge Case handling)",
        "difficulty": "ICPC Regional"
    },
    {
        "original": "Greedy: Always pick the largest coin available to make change.",
        "upgrade": "Given a non-standard coin system (e.g., 1, 3, 4), find the smallest value V where the greedy approach fails to find the minimum number of coins. Prove that for all values below V, greedy is optimal. (Requires finding the Edge Case of the algorithm itself + Exchange Argument)",
        "difficulty": "IOI / Codeforces Div1 C"
    },
    {
        "original": "Sort an array of tasks by duration.",
        "upgrade": "Given N tasks with processing time and decay rates. Each task loses value at a different rate while waiting. Find a processing order to minimize total decay. Prove your sorting strategy using an Exchange Argument. (Requires formal proof to derive the correct comparator; simple sorting is wrong)",
        "difficulty": "ICPC Regional"
    }
]
""".strip()


easy_to_hard_1 = """\
# Problem Difficulty Upgrade Generator

## Task Description
You are an expert competitive programming problem creator. Your task is to take a given problem and create a **significantly more challenging, competition-level version**.

"""

easy_to_hard_upgrade_1 = """\
# Problem Difficulty Upgrade Generator

## Task Description
You are an expert competitive programming problem creator. Your task is to take a given problem and create a **significantly more challenging, competition-level version** by strategically adding difficulty elements that test deeper understanding and more complex reasoning.

## Design Standards (Mandatory Quality Check)
To ensure the upgraded problem is competition-worthy, you must strictly adhere to these principles:
1. **Deep Synthesis**: The difficulty element must naturally intertwine with the original logic. The solution should feel like a single cohesive challenge, not a "patchwork".
2. **Multi-Step Reasoning**: The solution must require 2-3 non-trivial intermediate logical jumps. The solver must derive lemmas or intermediate states before applying standard algorithms.
3. **No Trivial Upgrades**: Avoid simply increasing N to $10^5$ if the logic remains $O(N)$. The upgrade must force a change in complexity class (e.g., from Greedy to Flow, from Simulation to Matrix Exponentiation).
4. **Disguise & Abstraction**: (If applicable) Hide the core theorem or data structure behind a unique story or abstract mathematical setting. Never explicitly name the required algorithm.

## Difficulty Elements Library (Select 1-2 distinct elements)

### Category A: {de1_str}

### Category B: {de2_str}

### Category C: {de3_str}

### Category D: {de4_str}

### Category E: {de5_str}

### Category F: {de6_str}

## Construction Protocol (Internal Thinking Process)
1. **Analyze Original**: Identify the naive solution and its complexity.
2. **Select Category**: Choose 1-2 categories from the library above that best fit the problem's potential.
3. **Apply Core Strategy**: Use the "Core Strategy" defined in your selected category to redesign the problem constraints and objectives.
4. **Review**: Check against the "Design Standards". Does it require multi-step reasoning? Is the theorem disguised?
5. **Final Output**: Write the problem statement clearly using standard CP formatting.

"""
easy_to_hard_2 = """
## Input
**Original Problem:**
```
{original_problem}
```

## Output Format
Return ONLY the new upgraded problem, nothing else.

[Your upgraded competitive programming problem here]
""".strip()

easy_to_hard_upgrade_1 = easy_to_hard_upgrade_1.format(de1_str=de1_str, de2_str=de2_str, de3_str=de3_str, de4_str=de4_str, de5_str=de5_str, de6_str=de6_str)

if __name__ == "__main__":
    print(easy_to_hard_upgrade_1)
