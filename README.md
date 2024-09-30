# Path coverage optimization

This project handles path coverage for mower and was part of my diploma thesis.
Input is a map in keyhole markup language and output is optimized path for automower.

### Code needs massive refactoring and it serves the purpose of demonstrating complexity of code.

# How it works

-   Area is split with parallel lines.
-   Intersection of map and parallel lines creates groups of lines.
-   Upper points of these intersection are clustered with kmeans.
-   Each of this sub-areas are trivial and its inner path is optimal.
-   Sequence of sub-areas is computed with genetic algorithm using 2-opt and dynamic programming.
    -   Fitness function is length of the path.
-   Whole path is smoothed with Dubin's curve.
