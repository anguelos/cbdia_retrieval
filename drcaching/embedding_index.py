from .embeddings import PageRegionEmbeddings
from .util import tic, toc, log
import collections
import numpy as np
import sklearn.neighbors
import threading

class IndexedRegions(object):
    def __init__(self, embedding_index):
        self.embedding_index = embedding_index

    def __len__(self):
        return len(self.embedding_index)

    def __getitem__(self, item):
        if isinstance(item, int):
            page_num = np.searchsorted(self.embedding_index.locations, item)
            region_num = item - page_num
            return self.embedding_index.embeddings[page_num].regions[region_num]
        elif hasattr(item, "__len__"):
            page_nums = np.searchsorted(self.embedding_index.locations, item)
            region_nums = item - page_nums
            embedings = self.embedding_index.embeddings[page_nums]
            return [embedings[n].regions[region_nums[n]] for n in range(len(embedings))]


class IndexedPageCrops(object):
    def __init__(self, embedding_index):
        self.embedding_index = embedding_index

    def __len__(self):
        return len(self.embedding_index)

    def __getitem__(self, item):
        if isinstance(item, int):
            page_num = np.searchsorted(self.embedding_index.locations, item)
            region_num = item - page_num
            l, r, t, b = self.embedding_index.embeddings[page_num].regions[region_num]
            return self.embedding_index.embeddings[page_num].page.img[l:r, t:b, :]
        elif hasattr(item, "__len__"):
            page_nums = np.searchsorted(self.embedding_index.locations, item)
            region_nums = item - page_nums
            embeddings = self.embedding_index.embeddings[page_nums]
            images = []
            for n in range(len(item)):
                l, r, t, b = embeddings[n].regions[region_nums[n]]
                images.append(embeddings[n].page.img[l:r, t:b, :])
            return images


class IndexedPageAndRegions(object):
    def __init__(self, embedding_index):
        self.embedding_index = embedding_index

    def __len__(self):
        return len(self.embedding_index)

    def __getitem__(self, item):
        if isinstance(item, int):
            page_num = np.searchsorted(self.embedding_index.locations, item)
            region_num = item - page_num
            ltrb = self.embedding_index.embeddings[page_num].regions[region_num]
            page = self.embedding_index.embeddings[page_num].page.img
            return (page,) + ltrb
        elif hasattr(item, "__len__"):
            page_nums = np.searchsorted(self.locations, item)
            region_nums = item - page_nums
            embeddings = self.embedding_index.embeddings[page_nums]
            pages = []
            for n in range(len(item)):
                ltrb = embeddings[n].regions[region_nums[n]]
                pages.append((embeddings[n].page.img,) + ltrb)
            return pages


class IndexedMd5AndRegions(object):
    def __init__(self, embedding_index):
        self.embedding_index = embedding_index

    def __len__(self):
        return len(self.embedding_index)

    def __getitem__(self, item):
        if isinstance(item, int):
            page_num = np.searchsorted(self.embedding_index.locations, item)
            region_num = item - page_num
            ltrb = self.embedding_index.embeddings[page_num].regions[region_num]
            page = self.embedding_index.embeddings[page_num].page.img
            return (page,) + ltrb
        elif hasattr(item, "__len__"):
            page_nums = np.searchsorted(self.locations, item)
            region_nums = item - page_nums
            embeddings = self.embedding_index.embeddings[page_nums]
            results = []
            for n in range(len(item)):
                ltrb = embeddings[n].regions[region_nums[n]]
                results.append((embeddings[n].page.md5,) + ltrb)
            return results


class EmbeddingIndex(object):
    def __init__(self, embedding_list, n_neighbors, dtype):
        self.nb_neighbors = n_neighbors
        self.data_dtype = dtype
        self.embeddings = np.array(embedding_list)
        self.md5_to_embedding = collections.OrderedDict()
        self.cumulative_sizes = np.empty(len(embedding_list), dtype="int64")
        self.sizes = np.array([len(emb) for emb in embedding_list])
        self.total_size = sum(self.sizes)
        self.cumulative_sizes = np.cumsum(self.sizes)
        self.embedded_vectors = np.empty([self.total_size, self.embeddings[0].embedding_length], dtype=dtype)

        shard_begin = 0
        for n, embedding in enumerate(embedding_list):
            self.md52embeddings[embedding.md5] = n
            self.embeddings[n] = embedding
            self.embedded_vectors[shard_begin: shard_begin + len(embedding)] = embedding.embeddings
        self.knn = sklearn.neighbors.KNeighborsClassifier(n_neighbors=n_neighbors)
        self._knn_ready = False
        self._knn_index_thread = None

        self.indexed_regions = IndexedRegions(self)
        self.indexed_page_crops = IndexedPageCrops(self)
        self.indexed_page_and_regions = IndexedPageAndRegions(self)
        self.indexed_md5_and_regions = IndexedMd5AndRegions(self)

    def _update_index(self):
        t = tic()
        log(3, "Updateting Index for {}".format(str(self)))
        self.knn.fit(self.embedded_vectors, np.arange(len(self), dtype="int64"))
        self._knn_ready = True
        log(3, "Updating Index for {} done in {:f} sec.".format(str(self), toc(t)))

    def update_index(self):
        self._knn_index_thread = threading.Thread(target = self._update_index)
        self._knn_index_thread.start()

    def search_by_embeddings(self, queries, nb_neighbors=None):
        t = tic()
        if not self._knn_ready:
            log(5, "Updating Index for {} incomplete search pauses.".format(self))
            self._knn_index_thread.pause()
            log(6, "Updating Index for {} incomplete search resumed.".format(self))
        if nb_neighbors is None:
            nb_neighbors = self.nb_neighbors
        log(9, "")
        return self.knn.kneighbors(queries, n_neighbors=nb_neighbors)
