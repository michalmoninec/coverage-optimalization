from random import random, choices, shuffle, randint, randrange
import time
import math

from pathlib import Path
from xlwt import Workbook

def not_valid(a, b):
    if ((len(set(a)) == len(a)) and ((len(set(b)) == len(b)))):
        return False
    else:
        # print(f"Not suitable crossover.")
        return True

def mutate(genom):
    prob = 0.2
    if random() < prob:
        # print(f'I will mutate this bitch!')
        p1 = randrange(0, len(genom))
        p2 = randrange(0, len(genom))
        while p1 == p2:
            p2 = randrange(0, len(genom))
        
        genom_copy = genom.copy()
        genom_copy[p1] = genom[p2]
        genom_copy[p2] = genom[p1]
        # print(f'genom orgig: {genom}')
        # print(f'genom mutated: {genom_copy}')
        return genom_copy
    return genom


def single_point_crossover(parents):
    a = parents[0]
    b = parents[1]
    point = randint(0, len(parents[0])-1)
    a_c = a[0:point] + b[point:]
    b_c = b[0:point] + a[point:]

    while not_valid(a_c, b_c):
        point = randint(0, len(parents[0])-1)
        a_c = a[0:point] + b[point:]
        b_c = b[0:point] + a[point:]
    
    return a_c, b_c





def selection_parents(population, fitness_func):
    not_found = True
    while not_found:
        parents = choices(
            population=population,
            weights= [ (1/(fitness_func(gene)**2)) for gene in population],
            k = 2)
        if parents[0] != parents[1]:
            not_found = False
            return parents




def init_population(len_limit, pop_count):
    arr_out = []
    for i in range(pop_count):
        arr = list(range(0, len_limit))
        shuffle(arr)
        arr_out.append(arr)
    return arr_out

def gsx_crossover(parents):
    parent1 = parents[0]
    parent2 = parents[1]
    cross_point = parent1[randint(0,len(parent1)-1)]
    # print(f'cross_point is: {cross_point}')
    # cross_point = 'B'

    arr1 = parent1[parent1.index(cross_point)+1:]
    arr2 = parent2[0:parent2.index(cross_point)]
    arr2 = arr2[::-1]
    # print(arr1)
    # print(arr2)

    child = [cross_point]

    k = min(len(arr1),len(arr2))
    for i in range(k):
        if arr1[i] not in child:
            child.append(arr1[i])
        else:
            break
        if arr2[i] not in child:
            child.insert(0,arr2[i])
        else:
            break

    rest = []
    for item in parent1:
        if item not in child:
            rest.append(item)
    k = 0
    
    while len(rest)>0:
        i = randint(0,len(rest)-1)
        
        if k%2 == 0:
            child.insert(0, rest[i])
        else:
            child.append(rest[i])
        rest.pop(i)
        k += 1

    return child

def swap_2_opt(arr, fitness_func):
    best_val = fitness_func(arr)
    # print(f'arr input: {arr}')
    # print(50*'---')
    # print(f'input best value: {best_val}')
    best_swap = None

    for i in range(len(arr)):
        for k in range(i+1,len(arr)):
            if i !=0:
                pre = arr[0:i]
            else:
                pre = []

            sub_arr = arr[i:k+1]
            past = arr[k+1:]
            new_arr = pre + sub_arr[::-1] + past
            # print(new_arr)
            # print(fitness_func(new_arr))
            # print(50*'--')
            # print(f'fitness iteration of new arr: {fitness_func(new_arr)}')
            if fitness_func(new_arr)<best_val:
                # print('Updating best val.')
                best_val = fitness_func(new_arr)
                best_swap = new_arr

    if best_swap:
        # print(f'returnin value: {fitness_func(best_swap)}')
        return best_swap
    else:
        # print(f'returning value: {fitness_func(arr)}')
        return arr



    pass

def GA_with_2_opt(population, evo_limit, fitness_func, sol_arr, best_val, solution, start, time_limit, index_arr):
    # print('Im doint 2-opt type of GA')
    for i in range(evo_limit):
        i_start = time.time()
        if i_start-start>time_limit:
            print(f'End due to time limit.')
            break
        
        population = sorted(population, key=lambda genome: fitness_func(genome))
        # print(f'Population before: {population}')
        # print(f'fitness for population: {[fitness_func(pop) for pop in population]}')

        if fitness_func(population[0])<best_val:
            # print(f'this is better: {fitness_func(population[0])<best_val}')
            solution = population[0]
            best_val = fitness_func(population[0])
            sol_arr.append(fitness_func(population[0]))
            index_arr.append(i)





        parents = selection_parents(population, fitness_func)
        # print(f'parents selected are: {parents}')

        child = gsx_crossover(parents)
        child = mutate(child)
        child = swap_2_opt(child, fitness_func)

        parents = sorted(parents, key=lambda genome: fitness_func(genome))
        # print(f'parents selected values: {[fitness_func(parent) for parent in parents]}')

        if fitness_func(child)<fitness_func(parents[1]):
            # print(f'fitness of child is better than worse parent: {fitness_func(child)}')
            # print(f'Upadting parent. Element number> {population.index(parents[1])}')
            population[population.index(parents[1])] = child
        
        # print(f'Population after: {population}')
        i_end = time.time()
        print(f'One iteration of GA lasts: {i_end - i_start}')
    return solution

def GA_with_2_opt_test(population, evo_limit, fitness_func, sol_arr, best_val, solution, start, time_limit, index_arr, s, x, y):
    # print('Im doint 2-opt type of GA')
    for i in range(evo_limit):
        i_start = time.time()
        if i_start-start>time_limit:
            print(f'End due to time limit.')
            break
        
        population = sorted(population, key=lambda genome: fitness_func(genome))
        # print(f'Population before: {population}')
        # print(f'fitness for population: {[fitness_func(pop) for pop in population]}')

        if fitness_func(population[0])<best_val:
            # print(f'this is better: {fitness_func(population[0])<best_val}')
            solution = population[0]
            best_val = fitness_func(population[0])
            sol_arr.append(fitness_func(population[0]))
            index_arr.append(i)

            s.write(y,x, i)
            s.write(y,x+1,fitness_func(population[0]))
            y = y + 1



        parents = selection_parents(population, fitness_func)
        # print(f'parents selected are: {parents}')

        child = gsx_crossover(parents)
        child = mutate(child)
        child = swap_2_opt(child, fitness_func)

        parents = sorted(parents, key=lambda genome: fitness_func(genome))
        # print(f'parents selected values: {[fitness_func(parent) for parent in parents]}')

        if fitness_func(child)<fitness_func(parents[1]):
            # print(f'fitness of child is better than worse parent: {fitness_func(child)}')
            # print(f'Upadting parent. Element number> {population.index(parents[1])}')
            population[population.index(parents[1])] = child
        
        # print(f'Population after: {population}')
        i_end = time.time()
        # print(f'One iteration of GA lasts: {i_end - i_start}')
    return solution

def GA_with_elitism_multi_parents(population, evo_limit, fitness_func, sol_arr, best_val, solution, start, time_limit, index_arr):


    # print('Im doint elitism type of GA.')
    for i in range(evo_limit):
        i_start = time.time()
        if i_start-start>time_limit:
            print(f'End due to time limit.')
            break

        population = sorted(population, key=lambda genome: fitness_func(genome))

        if fitness_func(population[0])<best_val:
            solution = population[0]
            best_val = fitness_func(population[0])
            sol_arr.append(fitness_func(population[0]))
            index_arr.append(i)



        children = []

        for _ in range(round(len(population)/2)):
            parents = selection_parents(population, fitness_func)

            child = gsx_crossover(parents)
            child = mutate(child)
            children.append(child)

        population = children + population[0:len(population)-len(children)]

        # print(f'next population looks: {population}')
        
        i_end = time.time()
        # print(f'One iteration of GA lasts: {i_end - i_start} for pop size: {len(population)}')

    return solution

def GA_with_elitism_multi_parents_test(population, evo_limit, fitness_func, sol_arr, best_val, solution, start, time_limit, index_arr, s, x, y):


    # print('Im doint elitism type of GA.')
    for i in range(evo_limit):
        i_start = time.time()
        if i_start-start>time_limit:
            print(f'End due to time limit.')
            break

        population = sorted(population, key=lambda genome: fitness_func(genome))

        if fitness_func(population[0])<best_val:
            solution = population[0]
            best_val = fitness_func(population[0])
            sol_arr.append(fitness_func(population[0]))
            index_arr.append(i)

            s.write(y,x, i)
            s.write(y,x+1,fitness_func(population[0]))
            y = y + 1

        children = []

        for _ in range(round(len(population)/2)):
            parents = selection_parents(population, fitness_func)

            child = gsx_crossover(parents)
            child = mutate(child)
            children.append(child)

        population = children + population[0:len(population)-len(children)]

        # print(f'next population looks: {population}')
        
        i_end = time.time()
        # print(f'One iteration of GA lasts: {i_end - i_start} for pop size: {len(population)}')

    return solution

def run_evolution(genome_len, evo_limit, fitness_func, pop_size, time_limit, genetic_type):
    population = init_population(genome_len, pop_count = pop_size)
    solution = None
    sol_arr = []
    index_arr = []
    best_val = math.inf

    start = time.time()

    # solution = GA_with_2_opt(population, evo_limit, fitness_func, sol_arr, best_val, solution)
    if genetic_type == 0:
        solution = GA_with_elitism_multi_parents(population, evo_limit, fitness_func, sol_arr, best_val, solution, start, time_limit, index_arr)
    elif genetic_type == 1:
        solution = GA_with_2_opt(population, evo_limit, fitness_func, sol_arr, best_val, solution, start, time_limit, index_arr)


        
        
    end = time.time()

    best_seq = solution

    time_needed = end - start
    # print(f'best seq try out: {best_seq}')
    for i in range(len(sol_arr)):
        print(f'Iteration value: {sol_arr[i]} at iteraion number:  {index_arr[i]}')
    return best_seq, time_needed

def run_evolution_test(genome_len, evo_limit, fitness_func, pop_size, time_limit, genetic_type, s, x, y):
    population = init_population(genome_len, pop_count = pop_size)
    solution = None
    sol_arr = []
    index_arr = []
    best_val = math.inf

    start = time.time()

    # solution = GA_with_2_opt(population, evo_limit, fitness_func, sol_arr, best_val, solution)
    if genetic_type == 0:
        solution = GA_with_elitism_multi_parents_test(population, evo_limit, fitness_func, sol_arr, best_val, solution, start, time_limit, index_arr, s, x, y)
    elif genetic_type == 1:
        solution = GA_with_2_opt_test(population, evo_limit, fitness_func, sol_arr, best_val, solution, start, time_limit, index_arr, s, x, y)


        
        
    end = time.time()

    best_seq = solution

    time_needed = end - start
    # print(f'best seq try out: {best_seq}')
    # for i in range(len(sol_arr)):
    #     print(f'Iteration value: {sol_arr[i]} at iteraion number:  {index_arr[i]}')
    return best_seq, time_needed

