from datetime import date, timedelta

def dateRange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def yearRange(year):
	return dateRange(date(year, 1, 1), date(year + 1, 1, 1))

def weekends(year):
	def satOrSun(day):
		if day.weekday() == 5:
			return 'Saturday'
		elif day.weekday() == 6:
			return 'Sunday'
		else:
			raise Exception('Not the saturday or sunday')

	return ((weekend, satOrSun(weekend)) for weekend in yearRange(2015) if weekend.weekday() == 5 or weekend.weekday() == 6)

for day in weekends(2015):
	print day