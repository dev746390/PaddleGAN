import cv2
import random
import os.path
from .base_dataset import BaseDataset, get_transform
from .image_folder import make_dataset

from .builder import DATASETS


@DATASETS.register()
class UnalignedDataset(BaseDataset):
    """
    """

    def __init__(self, cfg):
        """Initialize this dataset class.

        Args:
            cfg (dict) -- stores all the experiment flags
        """
        BaseDataset.__init__(self, cfg)
        self.dir_A = os.path.join(cfg.dataroot, cfg.phase + 'A')  # create a path '/path/to/data/trainA'
        self.dir_B = os.path.join(cfg.dataroot, cfg.phase + 'B')  # create a path '/path/to/data/trainB'

        self.A_paths = sorted(make_dataset(self.dir_A, cfg.max_dataset_size))   # load images from '/path/to/data/trainA'
        self.B_paths = sorted(make_dataset(self.dir_B, cfg.max_dataset_size))    # load images from '/path/to/data/trainB'
        self.A_size = len(self.A_paths)  # get the size of dataset A
        self.B_size = len(self.B_paths)  # get the size of dataset B
        btoA = self.cfg.direction == 'BtoA'
        input_nc = self.cfg.output_nc if btoA else self.cfg.input_nc       # get the number of channels of input image
        output_nc = self.cfg.input_nc if btoA else self.cfg.output_nc      # get the number of channels of output image
        self.transform_A = get_transform(self.cfg.transform, grayscale=(input_nc == 1))
        self.transform_B = get_transform(self.cfg.transform, grayscale=(output_nc == 1))

        self.reset_paths()

    def reset_paths(self):
        self.path_dict = {}

    def __getitem__(self, index):
        """Return a data point and its metadata information.

        Parameters:
            index (int)      -- a random integer for data indexing

        Returns a dictionary that contains A, B, A_paths and B_paths
            A (tensor)       -- an image in the input domain
            B (tensor)       -- its corresponding image in the target domain
            A_paths (str)    -- image paths
            B_paths (str)    -- image paths
        """
        A_path = self.A_paths[index % self.A_size]  # make sure index is within then range
        if self.cfg.serial_batches:   # make sure index is within then range
            index_B = index % self.B_size
        else:   # randomize the index for domain B to avoid fixed pairs.
            index_B = random.randint(0, self.B_size - 1)
        B_path = self.B_paths[index_B]

        A_img = cv2.imread(A_path)
        B_img = cv2.imread(B_path)
        # apply image transformation
        A = self.transform_A(A_img)
        B = self.transform_B(B_img)

        return A, B

    def __len__(self):
        """Return the total number of images in the dataset.

        As we have two datasets with potentially different number of images,
        we take a maximum of
        """
        return max(self.A_size, self.B_size)
