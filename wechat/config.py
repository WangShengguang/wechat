import os

from local_config import LocalConfig

cur_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.dirname(cur_dir)

data_dir = os.path.join(cur_dir, "data")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)


class Config(LocalConfig):
    pass
