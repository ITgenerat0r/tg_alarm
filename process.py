import multiprocessing

# def thread(func, args):
# 	try:
# 		th = multiprocessing.Process(target=func, args=args)
# 		th.start()
# 		multiprocessing.main_thread()
# 		# th.join()
# 	except Exception as e:
# 		print("Error in thread")
# 		print(e)
	
# def stop(name=""):
# 	print("Threads:")
# 	for t in multiprocessing.enumerate():
# 		print("  ", t.getName())
# 		if t.getName() == str(name):
# 			print("Stopping...")
# 			t.do_run = False
# 			t.join()

# def show():
# 	print("Threads:")
# 	for t in multiprocessing.enumerate():
# 		print("  ", t.getName())
# 	print()



class Process():
	"""docstring for Threads"""
	def __init__(self):
		self.__processes = []
		self.__rlock = multiprocessing.RLock()
		self.__p_conn, self.__c_conn = multiprocessing.Pipe()

	def getConn(self):
		return self.__c_conn

	def getRecv(self):
		return self.__p_conn.recv()

	def rlock(self):
		return self.__rlock

	def run(self, func, args):
		# if __name__ == '__main__':
		pr = multiprocessing.Process(target=func, args=args)
		self.__processes.append(pr)
		pr.start()
		
	def show(self):
		print("Threads:")
		for p in multiprocessing.enumerate():
			print("  ", p.getName())
		print()

	def stop(self, name=""):
		print("Threads:")
		for p in multiprocessing.enumerate():
			print("  ", p.getName())
			if p.getName() == str(name):
				print("Stopping...")
				p.do_run = False
				p.join()

	def stopAll(self):
		for p in self.__processes:
			print(p.getName())
			p.do_run = False
			p.join()