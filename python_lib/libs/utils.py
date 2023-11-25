
def equals(obj1, obj2, eq=None):
	if obj1 is None or obj2 is None:
		return False

	return obj1 == obj2 or (eq and eq(obj1, obj2))

def intersect(objs1, objs2, eq=None):
	res = []

	for obj1 in objs1:
		for obj2 in objs2:
			if equals(obj1, obj2, eq):
				res.append(obj1)

	return res

def first(objs1, objs2, eq=None):
	if not isinstance(objs1, list):
		objs1 = [objs1]

	if not isinstance(objs2, list):
		objs2 = [objs2]

	return intersect(objs1, objs2, eq)[0]