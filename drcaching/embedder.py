from .util import get_all_subclasses, mkdir_p
import pathlib

class ImageRegionEmbedder(object):
    embedder_type = "EmAbstract"

    @staticmethod
    def _get_embedder_types():
        subclasses = get_all_subclasses(ImageRegionEmbedder)
        res = {c.embedder_type: c for c in subclasses}
        assert len(res) == len(subclasses)
        for cls in subclasses:
            assert cls.embedder_type.isalum() and cls.embedder_type[:2] == "Em"
        return res

    @staticmethod
    def _get_embedder_class_from_filename(filename):
        embedder_types = ImageRegionEmbedder._get_embedder_types()
        return embedder_types[pathlib.Path(filename).parts[-2]]

    @staticmethod
    def load(filename):
        cls = ImageRegionEmbedder._get_embedder_class_from_filename(filename)
        cls.unserialize(filename)

    def __init__(self, embedding_size, filename):
        self.embedding_size = embedding_size
        self.filename = filename

    @staticmethod
    def unserialize(filename):
        raise NotImplementedError

    def __call__(self, img, ltrb):
        raise NotImplementedError()

    def save(self):
        raise NotImplementedError()

    def embed_file_lists(self, input_image_filenames, input_regions_filenames, output_embeddings_filenames):
        raise NotImplementedError()

    def embed_files(self, input_image_filename, input_regions_filename, output_embeddings_filename):
        if isinstance(input_image_filename, (list, tuple)):
            assert isinstance(input_regions_filename, (list, tuple))
            assert isinstance(output_embeddings_filename, (list, tuple))
            input_image_filenames = input_image_filename
            input_regions_filenames = input_regions_filename
            output_embeddings_filenames = output_embeddings_filename
        else:
            assert isinstance(input_regions_filename, (list, tuple))
            assert isinstance(output_embeddings_filename, (list, tuple))
            input_image_filenames = [input_image_filename]
            input_regions_filenames = [input_regions_filename]
            output_embeddings_filenames = [output_embeddings_filename]
        self.embed_file_lists(self, input_image_filenames, input_regions_filenames, output_embeddings_filenames)

    @property
    def embedder_type(self):
        return type(self).embedder_type

    @property
    def embedding_size(self):
        return self._embedding_size

    def get_page_bash_cmd(self,input_image_filename, input_regions_filename, output_embeddings_filename):
        return "python3 -c 'import drcaching; drcaching.ImageRegionEmbedder.load('{3}')"\
               ".embed_files('{0}', '{1}','{2}')".format(input_image_filename, input_regions_filename,
                                                         output_embeddings_filename, self.filename)

    def get_page_makeline(self, input_image_filename, input_regions_filename, output_embeddings_filename):
        cmd = self.get_page_bash_cmd(input_image_filename, input_regions_filename, output_embeddings_filename)
        return "{2}: {0} {1}\n\t{3}".format(input_image_filename, input_regions_filename, output_embeddings_filename,
                                            cmd)

class RandomRegionEmbedder(ImageRegionEmbedder):
    embedder_type = "EmRandom"

    def __init__(self, embeding_size=100, filename="/tmp/embedders/{}/f".format(self.embedder_type)):
        super().__init__(embedding_size=embeding_size, filename=filename)
