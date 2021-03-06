import inspect
import os

from keras import backend as K
from keras.callbacks import LambdaCallback
from keras.layers import Activation, Dropout, Flatten, Dense
from keras.layers import Conv2D, MaxPooling2D
from keras.preprocessing.image import ImageDataGenerator

from server3.lib import Sequential
from server3.lib import graph
from server3.service import logger_service
from server3.service.keras_callbacks import MyModelCheckpoint
from server3.service.saved_model_services import keras_saved_model


def image_classifier(conf, input, **kw):
    # extract conf
    f = conf['fit']['args']
    e = conf['evaluate']['args']
    epochs = f['epochs']
    batch_size = f['batch_size']
    # extract kw
    result_sds = kw.pop('result_sds', None)
    project_id = kw.pop('project_id', None)
    result_dir = kw.pop('result_dir', None)

    # extract input
    train_data_dir = input['train_data_dir']
    validation_data_dir = input['validation_data_dir']
    nb_train_samples = input['nb_train_samples']
    nb_validation_samples = input['nb_validation_samples']

    # dimensions of our images.
    # use 150, 150 as default
    img_width, img_height = 150, 150

    if K.image_data_format() == 'channels_first':
        input_shape = (3, img_width, img_height)
    else:
        input_shape = (img_width, img_height, 3)

    with graph.as_default():
        return model_main(result_sds, project_id, result_dir, train_data_dir,
                          validation_data_dir, nb_train_samples,
                          nb_validation_samples, input_shape,
                          img_width, img_height,
                          epochs, batch_size)


def model_main(result_sds, project_id, result_dir, train_data_dir,
               validation_data_dir, nb_train_samples,
               nb_validation_samples, input_shape,
               img_width, img_height,
               epochs, batch_size):
    print(train_data_dir)
    model = Sequential()
    model.add(Conv2D(32, (3, 3), input_shape=input_shape))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(32, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(64, (3, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])

    # this is the augmentation configuration we will use for training
    train_datagen = ImageDataGenerator(
        rescale=1. / 255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True)

    # this is the augmentation configuration we will use for testing:
    # only rescaling
    test_datagen = ImageDataGenerator(rescale=1. / 255)

    train_generator = train_datagen.flow_from_directory(
        train_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode='binary')

    validation_generator = test_datagen.flow_from_directory(
        validation_data_dir,
        target_size=(img_width, img_height),
        batch_size=batch_size,
        class_mode='binary')

    # callback to save metrics
    batch_print_callback = LambdaCallback(on_epoch_begin=
                                          lambda epoch, logs:
                                          logger_service.log_epoch_begin(
                                              epoch, logs,
                                              result_sds,
                                              project_id),
                                          on_epoch_end=
                                          lambda epoch, logs:
                                          logger_service.log_epoch_end(
                                              epoch, logs,
                                              result_sds,
                                              project_id),
                                          on_batch_end=
                                          lambda batch, logs:
                                          logger_service.log_batch_end(
                                              batch, logs,
                                              result_sds,
                                              project_id)
                                          )

    # checkpoint to save best weight
    best_checkpoint = MyModelCheckpoint(
        os.path.abspath(os.path.join(result_dir, 'best.hdf5')),
        save_weights_only=True,
        verbose=1, save_best_only=True)
    # checkpoint to save latest weight
    general_checkpoint = MyModelCheckpoint(
        os.path.abspath(os.path.join(result_dir, 'latest.hdf5')),
        save_weights_only=True,
        verbose=1)

    history = model.fit_generator(
        train_generator,
        steps_per_epoch=nb_train_samples // batch_size,
        epochs=epochs,
        validation_data=validation_generator,
        validation_steps=nb_validation_samples // batch_size,
        callbacks=[batch_print_callback, best_checkpoint,
                   general_checkpoint],
        verbose=0
    )

    # model.save_weights('first_try.h5')
    config = model.get_config()
    logger_service.log_train_end(result_sds,
                                 model_config=config,
                                 # score=score,
                                 history=history.history)
    keras_saved_model.save_model(result_dir, model)
    return {'history': history.history}


def image_classifier_to_str(conf, head_str, **kw):
    # extract conf
    f = conf['fit']['args']
    e = conf['evaluate']['args']
    epochs = f['epochs']
    batch_size = f['batch_size']
    # extract kw
    result_sds = kw.pop('result_sds', None)
    project_id = kw.pop('project_id', None)

    # dimensions of our images.
    # use 150, 150 as default
    img_width, img_height = 150, 150

    if K.image_data_format() == 'channels_first':
        input_shape = (3, img_width, img_height)
    else:
        input_shape = (img_width, img_height, 3)

    if result_sds is None:
        raise RuntimeError('no result_sds created')

    str_model = 'from keras.models import Sequential\n'
    str_model += 'from keras.callbacks import LambdaCallback\n'
    str_model += 'from keras.preprocessing.image import ImageDataGenerator\n'
    str_model += 'from keras.layers import Conv2D, MaxPooling2D\n'
    str_model += 'from keras.layers import Activation, Dropout, Flatten, Dense\n'
    str_model += 'from keras import backend as K\n'
    str_model += 'from keras.optimizers import SGD\n'
    str_model += 'from server3.lib.models.keras_callbacks import ' \
                 'MongoModelCheckpoint\n'
    str_model += 'from server3.service import logger_service\n'
    str_model += 'from server3.service import job_service\n'
    str_model += 'from server3.business import staging_data_set_business\n'
    str_model += head_str
    str_model += "result_sds = staging_data_set_business.get_by_id('%s')\n" % \
                 result_sds['id']
    str_model += "project_id = '%s'\n" % project_id
    str_model += "epochs = %s\n" % epochs
    str_model += "batch_size = %s\n" % batch_size
    str_model += "img_width = %s\n" % img_width
    str_model += "img_height = %s\n" % img_height
    str_model += "input_shape = (%s, %s, %s)\n" % input_shape
    model_main_str = inspect.getsource(model_main)
    str_model += model_main_str
    str_model += 'print(model_main(result_sds, project_id, train_data_dir, ' \
                 'validation_data_dir, nb_train_samples, ' \
                 'nb_validation_samples, input_shape, ' \
                 'img_width, img_height, ' \
                 'epochs, batch_size))\n'
    print(str_model)
    return str_model


IMAGE_CLASSIFIER = {
    "fit": {
        "args": [
            {
                "name": "batch_size",
                "type": {
                    "key": "int",
                    "des": "Number of samples per gradient update",
                    "range": None
                },
                "default": 32
            },
            {
                "name": "epochs",
                "type": {
                    "key": "int",
                    "des": "Number of epochs to train the model",
                    "range": None
                },
                "default": 10
            },
        ],
    },
    "evaluate": {
        "args": [
            {
                "name": "batch_size",
                "type": {
                    "key": "int",
                    "des": "Number of samples per gradient update",
                    "range": None
                },
                "default": 32
            },
        ]
    }
}
