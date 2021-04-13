from pathlib import Path
from xlwt import Workbook

from graph import GraphData
from paralel_tracks import ParalelTracks
from scripts.sub_areas import Areas
from scripts.node_graph import NodeGraph

from scripts.xmeans import xmeans_clustering
from scripts.genetic import run_evolution



home_dir = str(Path.cwd()) + "/maps/zahrada_complete.kml"
graph = GraphData(home_dir)

graph.set_coords(graph.file_name)
graph.get_outer_inner()

width = 0.1
angles = [0,15,30,45,60,75,90,105,120,135,150,165,180]
number_of_iterations = 10
sample_count = 7
number_of_generations = 100
population_size = 10

wb = Workbook()
sheet = wb.add_sheet('sheet1')
sheet.write(0,0,'Test')

sheet.write(1,0, 'sample_count')
sheet.write(1,1, sample_count)

sheet.write(2,0,'mower width')
sheet.write(2,1, width)

sheet.write(3,0, 'number of iterations')
sheet.write(3,1, number_of_iterations)

sheet.write(4,0, 'pouplation size:')
sheet.write(4,1, population_size)

sheet.write(5,0, 'angle:')

d_angle = 5

d = d_angle+1

for i in range(number_of_iterations):
    sheet.write(i+d,0,f"percentage diff of {i}")



def run_test():
    for index,angle in enumerate(angles):
        sheet.write(d_angle, index+1, angle)
        graph.setAngle(angle)
        for ii in range(number_of_iterations):


            tracks = ParalelTracks(graph.outer, graph.inner, width, graph.angle)
            tracks.getUpperPoints()

            arr = []
            input_arr = []

            for i in range(len(tracks.upper)):
                arr.append((tracks.upper[i].point))
                input_arr.append([tracks.upper[i].point[0],tracks.upper[i].point[1]])

            clusters, clusters_count, centers = xmeans_clustering(input_arr, 5)

            objects = [graph.outer]
            for item in graph.inner:
                objects.append(item)

            areas = Areas(tracks.paralels, clusters, objects, width, None, graph.outer_index)

            node_states = []
            group_ids = []
            path_distances = []
            for i in range(len(areas.sub_areas)):
                area = areas.sub_areas[i]
                for k in range(len(area.node_states)):
                    node_states.append(area.node_states[k])
                    group_ids.append(i)
                    path_distances.append(area.path_distances[k])


            node_graph = NodeGraph(node_states, group_ids, path_distances)

            objects = [graph.outer]
            for item in graph.inner:
                objects.append(item)

            # sample_count = 8
            orig_seq = list(range(0,sample_count))

            areas_nodes = []

            for i in orig_seq:
                areas_nodes.append(areas.sub_areas[i])

            node_graph.set_areas(areas_nodes)

            exact_seq, exact_val, max_val, time_exact = node_graph.get_exact_solution(areas_nodes, sample_count)

            seq, time_genetic = run_evolution(sample_count, number_of_generations, node_graph.get_value_fitness, population_size)

            seq_areas = [areas_nodes[ind] for ind in seq ]

            final_seq, final_val = node_graph.get_value(seq_areas)

            percentage = ((final_val - exact_val)/(max_val - exact_val))*100
            percentage = round(percentage,2)

            # print(50*'--')
            # print(f'Time exact: {time_exact}')
            # print(f'Time genetic: {time_genetic}')
            # print(f'Percentage differnce: {percentage}')
            # print(f'Number of samples: {sample_count}')
            print(50*'--')
            print('computing...')
            sheet.write(d_angle+1+ii,index+1,percentage)

run_test()
print(f'Test completed. File saved.')

wb.save('some.xls')