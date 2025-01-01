# Path coverage optimization

This project handles path coverage for an automatic mower and was part of my diploma thesis.
Input is a map in KML format and output is an optimized path for automatic mower.

### ! Code needs massive refactoring and this repo mainly serves the purpose of demonstrating complexity of solved problem !

# How it works

-   Area is split with a parallel lines.
-   Intersection of the map and the parallel lines creates groups of lines.
-   Upper points of these intersection are clustered with kmeans.
-   Each of this sub-areas are trivial and its inner path is optimal.
-   Sequence of the sub-areas is computed with genetic algorithm using 2-opt and dynamic programming.
    -   Fitness function is the length of the path.
-   Whole path is smoothed with Dubin's curve.
