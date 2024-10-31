import multiprocessing

class TwoQueue:
  worker_args = ()
  worker_function = None
  task_queue = multiprocessing.Queue()
  batch_args = ()
  batch_function = None
  result_queue = multiprocessing.Queue()
  num_workers = multiprocessing.cpu_count() - 2
  
  @staticmethod
  def set_num_workers(numworkers=4):
    TwoQueue.num_workers = numworkers
  
  @staticmethod
  def set_worker(worker_func, worker_args=()):
    TwoQueue.worker_func = worker_func
    TwoQueue.worker_args = worker_args
  
  @staticmethod
  def set_batch(batch_func, batch_args=()):
    TwoQueue.batch_function = batch_func
    TwoQueue.batch_args = batch_args
  
  @staticmethod
  def process_data(queue_callback):
    workers = [
        multiprocessing.Process(
            target=TwoQueue.worker_func,
            args=(TwoQueue.task_queue, TwoQueue.result_queue, TwoQueue.worker_args)
        ) for _ in range(TwoQueue.num_workers)
    ]
    batch_process = multiprocessing.Process(target=TwoQueue.batch_function, args=(TwoQueue.result_queue, TwoQueue.batch_args))
    for w in workers:
      w.start()
    batch_process.start()
    queue_callback(TwoQueue.task_queue)
    for _ in range(TwoQueue.num_workers):
      TwoQueue.task_queue.put(None)
    
    for w in workers:
      w.join()
    
    TwoQueue.result_queue.put(None)
    batch_process.join()