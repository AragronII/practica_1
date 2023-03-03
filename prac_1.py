# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import multiprocessing as mp
import time
import random


#---------------console panel-------------------------
num_producer = 10

Nax = 4

#times_of_produce = [1,2,3,3,3,3,2,1,3,2]

#times_of_produce = [0,1,0,1,0,1,0,1,0,1]

#times_of_produce = [1,2,3,1,0,2,1,0,1,3]

times_of_produce = [random.randint(0, Nax) for _ in range(num_producer)]

max_times_of_produce = max(times_of_produce)

up_limit = 100
#---------------console panel-------------------------


sems = [[mp.BoundedSemaphore(1), mp.Semaphore(0)] for _ in range(num_producer)]

merge_start = mp.BoundedSemaphore(1)

merge_stop = mp.Semaphore(0)

mutex = mp.Lock()

def producer(storage, i, N, N_max):
    for j in range(N_max):
        sems[i][0].acquire()
        print (f"producer {mp.current_process().name} produciendo")
        if j < N:
            produce(storage, i)
        else:
            produce(storage, i, True)
        sems[i][1].release()
        print (f"producer {mp.current_process().name} almacenado {storage[i]}")
        time.sleep(0.1)

def consumer(storage, N):
    for _ in range(N):
        merge_start.acquire()
        for i in range(num_producer):
            sems[i][1].acquire()
            print (f"consumer {mp.current_process().name} desalmacenando")
            data = consume(storage, i)
            #sems[i][0].release()
            print (f"consumer {mp.current_process().name} consumiendo {data}")
            time.sleep(0.3)
        merge_stop.release()

def produce(storage, i, tag = False):
    mutex.acquire()
    down_limit = max(0, storage[i]) # que sea creciente, si no 0
    try:
        if tag == False:
            storage[i] = random.randint(down_limit, up_limit)
        else:
            storage[i] = -1
        time.sleep(0.1)
    finally:
        mutex.release()

def consume(storage, i):
    mutex.acquire()
    try:
        data = storage[i]
        time.sleep(0.1)
    finally:
        mutex.release()
    return data

def ord_insercion(v):
    N = len(v)
    for i in range(N):
        elem = v[i];
        j = i-1;
        while j>0 and elem < v[j]:
            v[j+1] = v[j];
            j -= 1;
        v[j+1] = elem;

def merge(storage, N):
    res = []
    for _ in range(N):
        merge_stop.acquire()
        aux = up_limit
        for i in range(num_producer):
            if aux > storage[i] and storage[i] != -1 and storage[i] != -2:
                aux = storage[i]
        if aux != up_limit:
            res.append(aux)
            print(f"merged {aux}")
        time.sleep(0.1)
        for i in range(num_producer):
            sems[i][0].release()
        merge_start.release()
    ord_insercion(res)
    print(f"merged list{res}")
    

def main():
    storage = mp.Array('i', num_producer)
    N = times_of_produce
    N_max = max_times_of_produce
    for i in range(num_producer):
        storage[i] = -2
    
    proc_produce = [];
    for j in range(num_producer):
        proc_produce.append(mp.Process(target = producer, name = f'prod_{j}', \
                                  args = (storage, j, N[j], N_max)));
    for proc in proc_produce:
        proc.start()
    
    proc_consume = mp.Process(target = consumer, name="cons", args = (storage, N_max))
    proc_merge = mp.Process(target = merge, name = "merge", args = (storage, N_max))
    proc_consume.start()
    proc_merge.start()
    
    for proc in proc_produce:
        proc.join()
    proc_consume.join()
    proc_merge.join()
    
    
    
