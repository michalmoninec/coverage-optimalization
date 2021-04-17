from random import random, choices, shuffle, randint, randrange
import time
import math

def not_valid(a, b):
    if ((len(set(a)) == len(a)) and ((len(set(b)) == len(b)))):
        return False
    else:
        # print(f"Not suitable crossover.")
        return True

def mutation(genom):
    prob = 0.6
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
    parents_output = []

    for i in range(round(len(population)/2)):
        parents = choices(
        population=population,
        weights=[(1/fitness_func(gene)) for gene in population],
        k = 2
        )
        # print(f'selected parents: {parents}')
        parents_output.append(parents)

    return parents_output


def init_population(len_limit, pop_count):
    arr_out = []
    for i in range(pop_count):
        arr = list(range(0, len_limit))
        shuffle(arr)
        arr_out.append(arr)
    return arr_out



def run_evolution(genome_len, evo_limit, fitness_func, pop_size):
    population = init_population(genome_len, pop_count = pop_size)
    solution = None
    sol_arr = []
    best_val = math.inf

    start = time.time()
    # print(f'start of evolution')
    for i in range(evo_limit):
        
        population = sorted(population, key=lambda genome: fitness_func(genome))
        # print(f'sorted population: {population}')

        if fitness_func(population[0])<best_val:
            # print(f'this is better: {fitness_func(population[0])<best_val}')
            solution = population[0]
            best_val = fitness_func(population[0])
            sol_arr.append(fitness_func(population[0]))

        parents = selection_parents(population, fitness_func)
        
        # next_generation = population[0:(len(population)-len(parents))]

        children = [single_point_crossover(parent) for parent in parents]
        # print(f'children before: {children}')
        children_to_mutation = []
        
        for child in children:
            children_to_mutation += [child[0], child[1]]

        children = [mutation(child) for child in children_to_mutation]

        children = sorted(children, key=lambda genome: fitness_func(genome))
        # print(f'children after: {children}')


        population_next = children[0:round(pop_size/2)]
        population_next = population_next + population[0:round(pop_size/2)]
        population = population_next

        

        # population += [genom for genom in next_generation]
        
        
    end = time.time()

    # print(f'sorted population: {population}')
    # print(f'fitness values: {[fitness_func(item) for item in population]}')
    last_generation = [fitness_func(item) for item in population]
    best_index = last_generation.index(min(last_generation))
    # print(f'best value form last generation: {best_last}')
    # print(f'best value from all generations: {min(solutions)}')
    # print(f'time needed: {end - start}')

    # best_seq = population[0]
    best_seq = solution

    time_needed = end - start
    # print(f'best seq try out: {best_seq}')
    return best_seq, time_needed
