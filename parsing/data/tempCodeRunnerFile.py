
from tensorflow.python.framework import dtypes
from tensorflow.python.ops import array_ops
import tensorflow_hub as hub

from datetime import datetime
from tensorflow.compat.v1 import logging
from twitter.deepbird.projects.timelines.configs import all_configs
from twml.trainers import D ataRecordTrainer
from twml.contrib.calibrators.common_calibrators import (
    build_percentile_discretizer_graph,
)
from twml.contrib.calibrators.common_calibrators import calibrate_discretizer_and_export
from .metrics import get_multi_binary_class_metric_fn
from .constants import TARGET_LABEL_IDX, PREDICTED_CLASSES
from .example_weights import add_weight_arguments, make_weights_tensor
from .lolly.data_helpers import get_lolly_logits
from .lolly.tf_model_initializer_builder import TFModelInitializerBuilder
from .lolly.reader import LollyModelReader
from .tf_model.discretizer_builder import TFModelDiscretizerBuilder
from .tf_model.weights_i