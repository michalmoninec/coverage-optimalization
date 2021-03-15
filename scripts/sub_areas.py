def get_sub_areas(tracks, clusters, plot, plot_point):
    sub_areas = []

    for i in range(len(clusters)):
        subset = []
        for k in range(len(clusters[i])):
            subset.append([tracks[clusters[i][k]][0],tracks[clusters[i][k]][1]])
        # print(f'subset looks like: {subset}')
        sub_areas.append(subset)

    # print(f'whole areas: {sub_areas[0]}')

    print(f"len on sub_areas: {len(sub_areas)}")
    seq = [0,4,8]

    for k in seq:
        for i in range(len(sub_areas[k])):
            plot(sub_areas[k][i][0],sub_areas[k][i][1], [0,0,150], 'solo item')
        # print(f'last item, perhaps: {sub_areas[k][0][0][0]}')
        plot_point((sub_areas[k][0][0][0],sub_areas[k][0][1][0]), [0,155,0])
        plot_point((sub_areas[k][-1][0][0],sub_areas[k][-1][1][0]), [155,0,0])

    return sub_areas