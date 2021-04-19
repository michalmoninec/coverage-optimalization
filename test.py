import random 

def gsx_crossover(parent1, parent2):
    # cross_point = parent1[random.randint(0,len(parent1))]
    cross_point = 'B'

    arr1 = parent1[parent1.index(cross_point)+1:]
    arr2 = parent2[0:parent2.index(cross_point)]
    arr2 = arr2[::-1]
    print(arr1)
    print(arr2)

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
        i = random.randint(0,len(rest)-1)
        
        if k%2 == 0:
            child.insert(0, rest[i])
        else:
            child.append(rest[i])
        rest.pop(i)
        k += 1

    return child





# ex1 = ['D','C','I','B','A','H','G','E','F','K','L','M','N','O','J']
ex1 = 'DCIBAHGEFKLMNOJ'
ex2 = 'GFLOMKNEDJICBHA'
print(len(ex1))

gsx_crossover(ex1,ex2)

# a = [1,2,3,5]
# a.insert(0,5)
# print(a)