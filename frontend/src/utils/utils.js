let hasOwnProperty = Object.prototype.hasOwnProperty

const camelParser = (noCamel) => {

  const firstLetterUpper = (str) => {
    return str.charAt(0).toUpperCase() + str.slice(1)
  }

  return noCamel.split('_').map((e, i) => i > 0 ? firstLetterUpper(e) : e).join('')
}

function isEmpty(obj) {
  if (obj == null) return true
  if (obj.length > 0) return false
  if (obj.length === 0) return true
  if (typeof obj !== 'object') return true
  for (var key in obj) {
    if (hasOwnProperty.call(obj, key)) return false
  }

  return true
}

let toolkit_info = {
  '描述性统计': '描述性统计是用来概括、表述事物整体状况以及事物间关联、类属关系的统计方法。通过统计处理可以简洁地用几个统计值来表示一组数据地集中性和离散型(波动性大小)。',
  '降维': '降维，通过单幅图像数据的高维化，将单幅图像转化为高维空间中的数据集合，对其进行非线性降维。寻求其高维数据流形本征结构的一维表示向量，将其作为图像数据的特征表达向量。',
  '特征选取': '特征选择( Feature Selection )也称特征子集选择( Feature Subset Selection , FSS )，或属性选择( Attribute Selection )。是指从已有的M个特征(Feature)中选择N个特征使得系统的特定指标最优化，是从原始特征中选择出一些最有效特征以降低数据集维度的过程,是提高学习算法性能的一个重要手段,也是模式识别中关键的数据预处理步骤。',
  '聚类': '将物理或抽象对象的集合分成由类似的对象组成的多个类的过程被称为聚类。由聚类所生成的簇是一组数据对象的集合，这些对象与同一个簇中的对象彼此相似，与其他簇中的对象相异。“物以类聚，人以群分”，在自然科学和社会科学中，存在着大量的分类问题。聚类分析又称群分析，它是研究（样品或指标）分类问题的一种统计分析方法。',
  '数值转换': '数值转换是将数据从一种表示形式变为另一种表现形式的过程。数据在应用过程中相对比较繁杂，为了能够更好的应用数据，需要对其进行某种特定格式化的排列，数值转换通常包含对数字去量纲化、二值化、标准化等操作。',
}

let default_hyper_parameter = {
  'conf': {
    'layers': [
      {
        'name': 'Dense',
        'args': {
          'units': {
            'distribute': 'choice',
            'value': [
              32,
              64,
            ],
          },
          'activation': {
            'distribute': 'choice',
            'value': [
              'linear',
              'relu',
            ],
          },
          'input_shape': [
            4,
          ],
        },
        'index': 0,
      },
      {
        'name': 'Dropout',
        'args': {
          'rate': {
            'distribute': 'uniform',
            'value': '0, 0.5',
          },
        },
        'index': 1,
      },
      {
        'name': 'Dense',
        'args': {
          'units': 2,
          'activation': 'softmax',
        },
        'index': 2,
      },
    ],
    'compile': {
      'args': {
        'loss': {
          'distribute': 'choice',
          'value': [
            'categorical_crossentropy',
            'squared_hinge',
          ],
        },
        'optimizer': {
          'name': 'SGD',
          'range': [
            {
              'distribute': {
                'name': 'distribute_choice',
                'type': {
                  'des': 'distribute choice for hyperparameters tuning',
                  'key': 'choice',
                  'range': [
                    {
                      'default': '0, 1',
                      'eg': '0, 1',
                      'name': 'uniform',
                      'type': {
                        'des': 'Uniform distribution, Returns a value uniformly between low and high.',
                        'key': 'join_low_high',
                      },
                    },
                    {
                      'default': null,
                      'eg': [
                        256,
                        512,
                        1024,
                      ],
                      'name': 'choice',
                      'type': {
                        'des': 'Choice distribution, Returns one of the options, which should be a list or tuple.',
                        'key': 'multiple',
                      },
                    },
                  ],
                },
              },
              'name': 'lr',
              'type': {
                'des': 'the learning rate of NN optimizers',
                'key': 'float',
              },
            },
            {
              'distribute': {
                'name': 'distribute_choice',
                'type': {
                  'des': 'distribute choice for hyperparameters tuning',
                  'key': 'choice',
                  'range': [
                    {
                      'default': '0, 1',
                      'eg': '0, 1',
                      'name': 'uniform',
                      'type': {
                        'des': 'Uniform distribution, Returns a value uniformly between low and high.',
                        'key': 'join_low_high',
                      },
                    },
                    {
                      'default': null,
                      'eg': [
                        256,
                        512,
                        1024,
                      ],
                      'name': 'choice',
                      'type': {
                        'des': 'Choice distribution, Returns one of the options, which should be a list or tuple.',
                        'key': 'multiple',
                      },
                    },
                  ],
                },
              },
              'name': 'momentum',
              'type': {
                'des': 'the learning rate of NN optimizers',
                'key': 'float',
              },
            },
          ],
          'args': {
            'lr': 0.01,
          },
        },
        'metrics': [
          'acc',
        ],
      },
    },
    'fit': {
      'data_fields': [
        [
          'alm',
          'erl',
          'gvh',
          'mcg',
        ],
        [
          'mit',
          'nuc',
        ],
      ],
      'args': {
        'batch_size': 128,
        'epochs': 10,
      },
    },
    'evaluate': {
      'args': {
        'batch_size': 128,
      },
    },
  },
  'project_id': '59959ea9429782d5377ac133',
  'staging_data_set_id': '5995a0bc429782d65508f3ea',
  'schema': 'seq',
  'divide_row': 1000,
}

const pythonCodeOne = 'from grpc.beta import implementations\n' +
  'import tensorflow as tf\n\n' +

  'from tensorflow_serving.apis import predict_pb2\n' +
  'from tensorflow_serving.apis import prediction_service_pb2\n\n' +

  'tf.app.flags.DEFINE_string(\'server\', \'localhost:9000\',\n' +
  '\'PredictionService host:port\')\n' +
  'tf.app.flags.DEFINE_string(\'image\', \'\', \'path to image in JPEG format\')\n\n' +

  'FLAGS = tf.app.flags.FLAGS\n\n' +

  'def main(_):\n' +
  '\thost, port = FLAGS.server.split(\':\')\n' +
  '\tchannel = implementations.insecure_channel(host, int(port))\n' +
  '\tstub = prediction_service_pb2.beta_create_PredictionService_stub(channel)\n\n' +

  '\t# Send request\n' +
  '\twith open(FLAGS.image, \'rb\') as f:\n\n' +

  '\t\t# See prediction_service.proto for gRPC request/response details.\n' +
  '\t\tdata = f.read()\n' +
  '\t\trequetst = predict_pb2.PredictRequest()\n' +
  '\t\trequest.model_spec.name = \'inception\'\n' +
  '\t\trequest.model_spec.signature_name = \'predict_images\'\n' +
  '\t\trequest.inputs[\'images\'].CopyFrom(\n' +
  '\t\ttf.contrib.util.make_tensor_proto(data, shape=[1]))\n' +
  '\t\tresult = stub.Predict(request, 10.0)  # 10 secs timeout\n' +
  '\t\tprint(result)\n\n' +

  'if __name__ == \'__main__\':\n' +
  'tf.app.run()'

const pythonCodeTwo = 'predict_inputs_tensor_info = tf.saved_model.utils.build_tensor_info(jpegs)\n' +
  'prediction_signature = (\n' +
  'tf.saved_model.signature_def_utils.build_signature_def(\n' +
  'inputs={\'images\': predict_inputs_tensor_info},\n' +
  'outputs={\n' +
  '\t\'classes\': classes_output_tensor_info,\n' +
  '\t\'scores\': scores_output_tensor_info\n' +
  '},\n' +
  'method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME\n' +
  '))\n\n' +

  'builder.add_meta_graph_and_variables(\n' +
  'sess, [tf.saved_model.tag_constants.SERVING],\n' +
  'signature_def_map={\n' +
  '\t\'predict_images\': prediction_signature,\n' +
  '\ttf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: classification_signature,\n' +
  '},\n' +
  'legacy_init_op=legacy_init_op)'

export { isEmpty, camelParser, toolkit_info, default_hyper_parameter, pythonCodeOne, pythonCodeTwo }
