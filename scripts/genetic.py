from random import random, choices, shuffle, randint, randrange
import time
import math

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
    return choices(
        population=population,
        weights= [ (1/fitness_func(gene)) for gene in population],
        k = 2
    )



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

    pass

def run_evolution(genome_len, evo_limit, fitness_func, pop_size):
    population = init_population(genome_len, pop_count = pop_size)
    solution = None
    sol_arr = []
    best_val = math.inf

    start = time.time()
    # print(f'start of evolution')
    for _ in range(evo_limit):
        i_start = time.time()
        population = sorted(population, key=lambda genome: fitness_func(genome))
        # print(f'Population before: {population}')

        if fitness_func(population[0])<best_val:
            # print(f'this is better: {fitness_func(population[0])<best_val}')
            solution = population[0]
            best_val = fitness_func(population[0])
            sol_arr.append(fitness_func(population[0]))

        parents = selection_parents(population, fitness_func)
        # print(f'parents selected are: {parents}')

        child = gsx_crossover(parents)
        child = mutate(child)

        parents = sorted(parents, key=lambda genome: fitness_func(genome))

        if fitness_func(child)<fitness_func(parents[1]):
            # print(f'Upadting parent. Element number> {population.index(parents[1])}')
            population[population.index(parents[1])] = child
        
        # print(f'Population after: {population}')
        i_end = time.time()
        print(f'One iteration of GA lasts: {i_end - i_start}')

        
        
    end = time.time()

    best_seq = solution

    time_needed = end - start
    # print(f'best seq try out: {best_seq}')
    for item in sol_arr:
        print(f'Iteration value: {item}')
    return best_seq, time_needed

