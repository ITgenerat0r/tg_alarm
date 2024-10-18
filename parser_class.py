

class Parser():
	def __init__(self, log=False):
		self.__logs = log
		self.__version = "1.0"

		self.__months = {"января" : 1, "февраля" : 2, "марта" : 3, "апреля" : 4, "мая" : 5, "июня" : 6, "июля" : 7, "августа" : 8, "сентября" : 9, "октября" : 10, "ноября" : 11, "декабря" : 12}
		
		self.__cache_filename = "client_cache"
		self.__last_warning = self.__load_last_warning()

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

	def __save_last_warning(self, warning):
		if warning:
			self.__last_warning = warning
			try:
				f = open(self.__cache_filename, "w+")
				f.write(warning)
				f.close()
			except Exception as e:
				self.__prt(f"Can't save last warining in file '{self.__cache_filename}'.\n Error: {e}")

	def __load_last_warning(self):
		try:
			f = open(self.__cache_filename, "r")
			self.__last_warning = f.read()
			f.close()
			return self.__last_warning
		except Exception as e:
			self.__prt(f"Can't load last warining from file '{self.__cache_filename}'.\n Error: {e}")
			self.__last_warning = ""
			return ""


	def parse_file(self, filename, enc="1251"):
		# res = []
		res = ""
		f = open(filename, 'r', encoding=enc)
		key = True
		for line in f:
			line = line.strip()
			# print(f"line: {line}")
			if self.__last_warning == "" or self.__last_warning == line:
				key = False
				self.__save_last_warning(line)
				continue
			if key or line == "":
				continue
			# print("check")
			self.__last_warning = line
			if line.find("Предупреждение:") >= 0:
				res += line + "\n"
				# print("add")
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
		# print(f"res: {res}")
		return res.strip()


	def parse_item(self, item):
		b_ind = item.find('value="')
		if b_ind >= 0:
			m_ind = item.find('" name="')
			if m_ind > 0:
				e_ind = item.find('"/>')
				if e_ind > 0:
					value = item[b_ind+7:m_ind]
					key = item[m_ind+8:e_ind]
					item = item[e_ind+3:]
					# print(f"key: {key}")
					# print(f"value: {value}")
					# print(f"item: {item}")
					return (key, value, item)
		return ("", "", "")

	def parse_config(self, filename, enc="UTF-16-le"):
		data = {}
		f = open(filename, 'r', encoding=enc)
		for line in f:
			# print(line)
			(k, v, item) = self.parse_item(line)
			if k:
				data[k] = v
			while item != "":
				(k, v, item) = self.parse_item(item)
				if k:
					data[k] = v
		f.close()
		return data

	def translate_config(self, udata):
		alphabet = {'well': "Скважина", 'cluster': "Куст", 'field': "Месторождение", 'id' : "uuid"}
		org_alph = {'customer': "Клиент", 'master': "Мастер", 'operators': "Операторы", 'organization': "Организация", 'party': "Номер партии", 'partyhead': "Нач. партии", 'tz': "Часовой пояс"}
		data = {}
		for k in udata:
			if k in alphabet:
				data[alphabet[k]] = udata[k]
		return data












# p = Parser()
# # print(p.is_bigger("9:12:13", "8:12:14"))
# dt = p.parse_config('../wellinfo.config')
# result = p.translate_config(dt)
# # print(result)
# for i in result:
# 	print(f"{i}: {result[i]}")







