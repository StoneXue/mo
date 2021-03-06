from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import math

import six

from tensorflow.contrib import layers
from tensorflow.contrib.framework.python.ops import \
    variables as contrib_variables
from tensorflow.contrib.layers.python.layers import feature_column
from tensorflow.contrib.learn.python.learn.estimators import head as head_lib
from tensorflow.python.feature_column import feature_column as fc_core
from tensorflow.python.framework import ops
from tensorflow.python.ops import clip_ops
from tensorflow.python.ops import gradients
from tensorflow.python.ops import partitioned_variables
from tensorflow.python.ops import variable_scope
from tensorflow.python.training import training as train
from server3.constants import SPEC

# The default learning rate of 0.2 is a historical artifact of the initial
# implementation, but seems a reasonable choice.
_LEARNING_RATE = 0.2


def _get_optimizer(spec):
    if isinstance(spec, six.string_types):
        return layers.OPTIMIZER_CLS_NAMES[spec](
            learning_rate=_LEARNING_RATE)
    elif callable(spec):
        return spec()
    return spec


# Ensures consistency with LinearComposableModel.
def _get_default_optimizer(feature_columns):
    learning_rate = min(_LEARNING_RATE, 1.0 / math.sqrt(len(feature_columns)))
    return train.FtrlOptimizer(learning_rate=learning_rate)


def linear_regressor_model_fn(features, labels, mode, params, config=None):
    """A model_fn for linear models that use a gradient-based optimizer.
    Args:
      features: `Tensor` or dict of `Tensor` (depends on data passed to `fit`).
      labels: `Tensor` of shape [batch_size, 1] or [batch_size] labels of
        dtype `int32` or `int64` in the range `[0, n_classes)`.
      mode: Defines whether this is training, evaluation or prediction.
        See `ModeKeys`.
      params: A dict of hyperparameters.
        The following hyperparameters are expected:
        * head: A `Head` instance.
        * feature_columns: An iterable containing all the feature columns
        used by
            the model.
        * optimizer: string, `Optimizer` object, or callable that defines the
            optimizer to use for training. If `None`, will use a FTRL
            optimizer.
        * gradient_clip_norm: A float > 0. If provided, gradients are
            clipped to their global norm with this clipping ratio.
        * joint_weights: If True, the weights for all columns will be stored
        in a
          single (possibly partitioned) variable. It's more efficient, but it's
          incompatible with SDCAOptimizer, and requires all feature columns are
          sparse and use the 'sum' combiner.
      config: `RunConfig` object to configure the runtime settings.
    Returns:
      A `ModelFnOps` instance.
    Raises:
      ValueError: If mode is not any of the `ModeKeys`.
    """

    #   head = head_lib.multi_class_head(
    #         params["n_classes"],
    #         weight_column_name=params["weight_column_name"],
    #         enable_centered_bias=params["enable_centered_bias"],
    #         label_keys=params["label_keys"])

    head = head_lib.regression_head(
        weight_column_name=params["weight_column_name"],
        label_dimension=params["label_dimension"],
        enable_centered_bias=params["enable_centered_bias"])

    feature_columns = [layers.real_valued_column(i) for i in features.keys()]
    optimizer = _get_default_optimizer(feature_columns)
    gradient_clip_norm = params.get("gradient_clip_norm", None)
    num_ps_replicas = config.num_ps_replicas if config else 0
    joint_weights = params.get("joint_weights", False)

    if not isinstance(features, dict):
        features = {
            "": features}

    parent_scope = "linear"

    partitioner = partitioned_variables.min_max_variable_partitioner(
        max_partitions=num_ps_replicas,
        min_slice_size=64 << 20)

    with variable_scope.variable_scope(
            parent_scope,
            values=tuple(six.itervalues(features)),
            partitioner=partitioner) as scope:
        if all([isinstance(fc, feature_column._FeatureColumn)
                # pylint: disable=protected-access
                for fc in feature_columns]):
            if joint_weights:
                layer_fn = layers.joint_weighted_sum_from_feature_columns
            else:
                layer_fn = layers.weighted_sum_from_feature_columns
            logits, _, _ = layer_fn(
                columns_to_tensors=features,
                feature_columns=feature_columns,
                num_outputs=head.logits_dimension,
                weight_collections=[parent_scope],
                scope=scope)
        else:
            logits = fc_core.linear_model(
                features=features,
                feature_columns=feature_columns,
                units=head.logits_dimension,
                weight_collections=[parent_scope])

        def _train_op_fn(loss):
            global_step = contrib_variables.get_global_step()
            my_vars = ops.get_collection(parent_scope)
            grads = gradients.gradients(loss, my_vars)
            if gradient_clip_norm:
                grads, _ = clip_ops.clip_by_global_norm(grads,
                                                        gradient_clip_norm)
            return (_get_optimizer(optimizer).apply_gradients(
                zip(grads, my_vars), global_step=global_step))

        return head.create_model_fn_ops(
            features=features,
            mode=mode,
            labels=labels,
            train_op_fn=_train_op_fn,
            logits=logits)


LinearRegressorSteps = [
    {
        "name": "data_source",
        "display_name": "Select Data Source",
        "args": [
            {
                "name": "input",
                "des": "Please select input data source",
                "type": "select_box",
                "default": None,
                "required": True,
                "len_range": [
                    1,
                    1
                ],
                "values": []
            }
        ]
    },
    {
        "name": "feature_fields",
        "display_name": "Select Feature Fields",
        "args": [
            {
                "name": "fields",
                "des": "",
                "required": True,
                "type": "multiple_choice",
                "len_range": [
                    1,
                    None
                ],
                "values": []
            }
        ]
    },
    {
        "name": "label_fields",
        "display_name": "Select Label Fields",
        "args": [
            {
                "name": "fields",
                "des": "",
                "type": "multiple_choice",
                "required": True,
                "len_range": [
                    1,
                    None
                ],
                "values": []
            }
        ]
    },
    {
        "name": "estimator",
        "display_name": "Estimator Parameters",
        'args': [
            {
                **SPEC.ui_spec['input'],
                "name": "weight_column_name",
                "display_name": "Weight Column Name",
                "value_type": "str",
                "des": "A string defining feature column name "
                       "representing "
                       "weights. It is used to down weight or boost "
                       "examples during training. It will be multiplied "
                       "by "
                       "the loss of the example."
            },
            {
                **SPEC.ui_spec['input'],
                "name": "gradient_clip_norm",
                "display_name": "Gradient Clip Norm",
                "value_type": "float",
                "des": "A float > 0. If provided, gradients are clipped "
                       "to their global norm with this clipping ratio.",
                "range": [0.0, 100],
            },
            {
                **SPEC.ui_spec['input'],
                "name": "_joint_weights",
                "display_name": "Joint weights",
                "value_type": "bool",
                "des": "If True, the weights for all columns will be "
                       "stored in a single (possibly partitioned) "
                       "variable. It's more efficient, but it's "
                       "incompatible with SDCAOptimizer, and requires "
                       "all feature columns are sparse and use"
                       " the 'sum' combiner.",
            },
            {
                **SPEC.ui_spec['input'],
                "name": "enable_centered_bias",
                "display_name": "Enable Centered Bias",
                "value_type": "bool",
                "des": "A bool. If True, estimator will learn a "
                       "centered bias variable for each class. "
                       "Rest of the model structure learns the residual "
                       "after centered bias.",
            },
            {
                **SPEC.ui_spec['input'],
                "name": "label_dimension",
                "display_name": "Label Dimension",
                "des": "Number of regression targets per example. This "
                       "is thesize of the last "
                       "dimension of the labels and logits `Tensor` "
                       "objects(typically, these "
                       "have shape `[batch_size, label_dimension]`)",
                "default": 1,
            }
        ]
    },
    {
        "name": "fit",
        "display_name": "Fit Parameters",
        "args": [
            {
                **SPEC.ui_spec['input'],
                "name": "steps",
                "display_name": "Steps",
                "des": "Number of steps of training",
                "default": 400,
                "required": True
            },
        ],
    },
    {
        "name": "evaluate",
        "display_name": "Evaluate Parameters",
        "args": [
            {
                **SPEC.ui_spec['input'],
                "name": "steps",
                "display_name": "Steps",
                "des": "Number of steps of evaluate",
                "default": 1,
                "required": True
            },
        ]
    }
]

LinearRegressor = {
    'estimator': {
        'args': [
            {
                "name": "weight_column_name",
                "type": {
                    "key": "string",
                    "des": "A string defining feature column name "
                           "representing "
                           "weights. It is used to down weight or boost "
                           "examples during training. It will be multiplied "
                           "by "
                           "the loss of the example."
                },
                "default": None,
                "required": False
            },
            {
                "name": "gradient_clip_norm",
                "type": {
                    "key": "float",
                    "des": "A float > 0. If provided, gradients are clipped "
                           "to their global norm with this clipping ratio.",
                    "range": [0.0, 100]
                },
                "default": None,
                "required": True
            },
            {
                "name": "_joint_weights",
                "type": {
                    "key": "bool",
                    "des": "If True, the weights for all columns will be "
                           "stored in a single (possibly partitioned) "
                           "variable. It's more efficient, but it's "
                           "incompatible with SDCAOptimizer, and requires "
                           "all feature columns are sparse and use"
                           " the 'sum' combiner.",
                    "range": None
                },
                "default": False,
                "required": True
            },
            {
                "name": "enable_centered_bias",
                "type": {
                    "key": "bool",
                    "des": "A bool. If True, estimator will learn a "
                           "centered bias variable for each class. "
                           "Rest of the model structure learns the residual "
                           "after centered bias.",
                    "range": None
                },
                "default": False,
                "required": True
            },
            {
                "name": "label_dimension",
                "type": {
                    "key": "int",
                    "des": "Number of regression targets per example. This "
                           "is thesize of the last "
                           "dimension of the labels and logits `Tensor` "
                           "objects(typically, these "
                           "have shape `[batch_size, label_dimension]`)",
                    "range": None
                },
                "default": 1,
                "required": False
            }
        ]
    },
    'fit': {
        "data_fields": {
            "name": "training_fields",
            "type": {
                "key": "transfer_box",
                "des": "data fields for x and y",
            },
            "default": None,
            "required": True,
            "x_data_type": ["integer", "float"],
            "y_data_type": ["integer", "float"],
            "x_len_range": None,
            "y_len_range": None
        },
        'args': [
            {
                "name": "steps",
                "type": {
                    "key": "int",
                    "des": "steps for training",
                    "range": None
                },
                "default": 30,
                "required": True
            },
        ]
    },
    'evaluate': {
        'args': [
            {
                "name": "steps",
                "type": {
                    "key": "int",
                    "des": "steps for evaluate",
                    "range": None
                },
                "default": 1,
                "required": True
            },
        ]
    }
}
