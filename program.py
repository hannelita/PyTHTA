from resolver import Resolver

r = Resolver()
r.import_file()
print(r.df.info())
print(r.build())