from pathlib import Path
from xlwt import Workbook

from graph import GraphData
from scripts.node_graph import NodeGraph
from scripts.sub_areas import Areas
from paralel_tracks import ParalelTracks

from scripts.xmeans import xmeans_clustering
from scripts.genetic import run_evolution_test

from scripts.computational_thread import ClusteringThread, ComputationalThread, GeneticThreadTest, PlotThread, VisibilityGraphThread

def main():
    maps = ['map1.kml', 'map2.kml', 'map3.kml']
    wb = Workbook()
    iter = 0

    for map in maps:

        home_dir = str(Path.cwd()) + "/maps/"+ str(map)
        width = 0.5

        


        angles = [0,45,90,135]
        sheet = wb.add_sheet('test metody '+str(map))
        sheet.write(0,0,'Test zavislosti uhlu na poctu clusteru atd')
        sheet.write(1,0, 'Width')
        sheet.write(1,1, width)
        x_offset = 0

        for angle in angles:

            graph = GraphData(home_dir)
            graph.set_coords(graph.file_name)
            graph.setWidth(width)
            graph.setAngle(angle)
            graph.get_outer_inner()

            tracks = ParalelTracks(graph.outer, graph.inner, width, graph.angle)
                # print(f"tracks lookalike: {tracks.paralels}")
            tracks.getUpperPoints()



            arr = []
            input_arr = []

            for i in range(len(tracks.upper)):
                arr.append((tracks.upper[i].point))
                input_arr.append([tracks.upper[i].point[0],tracks.upper[i].point[1]])


            clusters, clusters_count, centers = xmeans_clustering(input_arr)

            objects = [graph.outer]
            for item in graph.inner:
                objects.append(item)

            areas = Areas(tracks.paralels, clusters, objects, width, None, graph.outer_index)
            print(f'Number of clusters: {clusters_count}')

            #VISIBILITY PART
            node_states = []
            group_ids = []
            path_distances = []
            for i in range(len(areas.sub_areas)):
                area = areas.sub_areas[i]
                for k in range(len(area.node_states)):
                    node_states.append(area.node_states[k])
                    group_ids.append(i)
                    path_distances.append(area.path_distances[k])

            node_graph = NodeGraph(node_states, group_ids, path_distances, objects)

            # sample_count = 8
            sample_count = len(areas.sub_areas)

            orig_seq = list(range(0,sample_count))

            areas_nodes = []

            for i in orig_seq:
                areas_nodes.append(areas.sub_areas[i])

            node_graph.set_areas(areas_nodes)


            max_iter = len(maps)*5*len(angles)

            

                
            genetic_iter_limit = 2000
            genetic_time_limit = 1800
            
            # 0 - elitism, 1 - 2-opt
            genetic_type = 1

            
            


            

            #GENETIC START
            genetic_popsize = 16

            sheet.write(4,x_offset, 'angle')
            sheet.write(4,x_offset+1, angle)

            y_offset = 5



        

            sample_count = len(areas.sub_areas)

            orig_seq = list(range(0,sample_count))

            areas_nodes = []

            for i in orig_seq:
                areas_nodes.append(areas.sub_areas[i])

            node_graph.set_areas(areas_nodes)


            for _ in range(5):
                seq, time_genetic = run_evolution_test(sample_count, genetic_iter_limit, node_graph.get_value_fitness, genetic_popsize, genetic_time_limit, genetic_type, sheet, x_offset, y_offset)
                x_offset = x_offset + 2
                print(f'Iteration {iter}/{max_iter}')
                iter = iter + 1
            x_offset = x_offset + 1

    wb.save('test_number_second_1.xls')
    print(f'test done and saved')



if __name__ == '__main__':
    main()
