import sklearn.neighbors
import numpy as np
import timeit
import time

repetions = 1

def measure(data_type,db_size,embedding_size,neighbor_count,query_sizes):
    report_dict = {}
    knn = sklearn.neighbors.KNeighborsClassifier(n_neighbors=neighbor_count, n_jobs=-1)
    create_index_setup = "X=np.random.rand({1},{2}).astype('{0}');y=np.arange({1})".format(
        data_type,db_size,embedding_size,neighbor_count)
    create_index_run = "knn.fit(X,y)"
    report_dict["Indexing"]= int (1000*timeit.timeit(create_index_run,create_index_setup,globals={"knn":knn,"np":np},number=repetions))
    for query_size in query_sizes:
        query_setup="q=np.random.rand({0},{1}).astype('{2}')".format(query_size, embedding_size, data_type)
        query_run = "dist, ids = knn.kneighbors(q)"
        report_dict["Queries{:5d}".format(query_size)] = int(1000*timeit.timeit(query_run, query_setup, globals={"knn": knn, "np": np},number=repetions))
    return report_dict


data_types = ["float", "double"]
db_sizes = [1000, 10000, 100000, 1000000]
embedding_sizes = [50, 100, 300, 600]
neighbor_count = [1, 5, 50, 500, 1000]
query_sizes = [1, 4, 8, 16, 32, 128]

row_dicts=[]
col_names= "Experiment #","Data Type","Db Size","Embedding Size","Neighbor Count"
counter = 1

t=time.time()

for db_size in db_sizes:
    for data_type in data_types:
        for embedding_size in embedding_sizes:
            for neighbor_count in embedding_sizes:
                columns_dict = measure(data_type,db_size,embedding_size,neighbor_count,query_sizes)
                row_dict = {k: v for k, v in columns_dict.items()}
                row_dict.update({col_names[0]:counter,
                                col_names[1]:data_type,col_names[2]:db_size,
                                 col_names[3]:embedding_size,col_names[4]:neighbor_count})
                row_dicts.append(row_dict)
                counter+=1


column_names = col_names + tuple(sorted(columns_dict.keys()))
header = ("| {:15} " * len(column_names) + " |").format(*column_names)
table = header + "\n"+ "".join(["|" if ch == "|" else "-" for ch in header]) + "\n"
for row_dict in row_dicts:
    table+= ("| {:15} " * len(column_names) + " |").format(*([row_dict[n] for n in column_names]))+"\n"


markdown = """### Indexing Performance

The indexing is based on scikit-learn kdtree implementation.


Experiments in the following section provide an crude upper bound on possible performance.
These experiments don't include IO issues all tests are initialised and run in RAM.

### Scalabillity Experiment Results
{}

Total experiment duration: {:d} msec.
Repetitions per measurement: {:d}.

The experiment can be repeated with the command:

```bash
python3 test/benchmark_indexing.py  > ./docs/performance.md
``` 

""".format(table, int(1000*(time.time()-t)), repetions)

print(markdown)

