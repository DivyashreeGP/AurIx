import pickle
data = request.args.get('x')
obj = pickle.loads(data)