from multiprocessing import Process, Lock

def f(l, i):
    l.acquire()
    print 'hello world', i
    l.release()

if __name__ == '__main__':
    lock = Lock()


    proc = [Process(target=f, args=(lock, num)) for num in range(500)]
    for p in proc:
		p.start()
    for p in proc:
		p.join()    
