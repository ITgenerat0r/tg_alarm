

class Parser():
	def __init__(self, log=False):
		self.__logs = log
		self.__version = "1.0"

		self.__months = {"января" : 1, "февраля" : 2, "марта" : 3, "апреля" : 4, "мая" : 5, "июня" : 6, "июля" : 7, "августа" : 8, "сентября" : 9, "октября" : 10, "ноября" : 11, "декабря" : 12}
		
		self.__last_warning = ""

		self.__last_day = "1"
		self.__last_month = 1
		self.__last_year = "0"
		self.__last_time = "0:00:00"

	def __prt(self, text):
		if self.__logs:
			print(text)

	def __month_name_to_number(self, name):
		return self.__months[name]

	# True if first bigger
	def __is_bigger(self, first, second):
		if len(first) > len(second):
			return True
		elif len(first) == len(second):
			return first > second
		return False



	def __is_new(self, time):
		data = time.split(' ')
		key = False
		if len(data) > 4:
			day = data[0]
			month = self.__month_name_to_number(data[1])
			year = data[2]
			time = data[4]
			if self.__is_bigger(year, self.__last_year):
				key = True
			elif year == self.__last_year:
				if month > self.__last_month:
					key = True
				elif month == self.__last_month:
					if self.__is_bigger(day, self.__last_day):
						key = True
					elif day == self.__last_day:
						if self.__is_bigger(time, self.__last_time):
							key = True
		if key:
			self.__last_year = year
			self.__last_month = month
			self.__last_day = day
			self.__last_time = time
		return key


	def parse_file(self, filename, enc="1251"):
		# res = []
		res = ""
		f = open(filename, 'r', encoding=enc)
		key = True
		for line in f:
			line = line.strip()
			print(f"line: {line}")
			if self.__last_warning == "" or self.__last_warning == line:
				key = False
				self.__last_warning = line
				continue
			if key or line == "":
				continue
			print("check")
			self.__last_warning = line
			if line.find("Предупреждение:") >= 0:
				res += line + "\n"
				print("add")
				# ind = line.find(" : ")
				# if ind > 0:
				# 	time = line[:ind].strip()
				# 	text = line[ind+3:].strip()
				# 	# print(f"|{time}|{text}|")
				# 	res.append(f"{time} : {text}")
				# else:
				# 	self.__prt("Wrong line!")
		if key:
			self.__last_warning = ""
		f.close()
		print(f"res: {res}")
		return res.strip()












# p = Parser()
# # print(p.is_bigger("9:12:13", "8:12:14"))
# result = p.parse_file('test.txt')
# print(result)

# print('-')
# result = p.parse_file('test.txt')

# print(result)







