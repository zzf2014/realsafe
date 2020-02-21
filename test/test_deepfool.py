import tensorflow as tf
import numpy as np
from os.path import expanduser
from keras.datasets.cifar10 import load_data

from realsafe import DeepFool
from realsafe.model.cifar10 import ResNet56

batch_size = 100

session = tf.Session()
model = ResNet56()
model.load(session, model_path=expanduser('~/.realsafe/cifar10/resnet56.ckpt'))

_, (xs_test, ys_test) = load_data()
xs_test = (xs_test / 255.0) * (model.x_max - model.x_min) + model.x_min
ys_test = ys_test.reshape(len(ys_test))

xs_ph = tf.placeholder(model.x_dtype, shape=(batch_size, *model.x_shape))
lgs, lbs = model.logits_and_labels(xs_ph)

xs = xs_test[0:batch_size]
ys = ys_test[0:batch_size]

attack = DeepFool(
    model=model,
    batch_size=batch_size,
    goal='ut',
    distance_metric='l_2',
    session=session
)
attack.config(
    overshot=0.02,
    iteration=50,
)

xs_adv = attack.batch_attack(xs, ys=ys)
lbs_pred = session.run(lbs, feed_dict={xs_ph: xs})
lbs_adv = session.run(lbs, feed_dict={xs_ph: xs_adv})

print(
    np.equal(ys, lbs_pred).astype(np.float).mean(),
    np.equal(ys, lbs_adv).astype(np.float).mean()
)

attack = DeepFool(
    model=model,
    batch_size=batch_size,
    goal='ut',
    distance_metric='l_inf',
    session=session
)
attack.config(
    overshot=0.02,
    iteration=50,
)

xs_adv = attack.batch_attack(xs, ys=ys)
lbs_pred = session.run(lbs, feed_dict={xs_ph: xs})
lbs_adv = session.run(lbs, feed_dict={xs_ph: xs_adv})

print(
    np.equal(ys, lbs_pred).astype(np.float).mean(),
    np.equal(ys, lbs_adv).astype(np.float).mean()
)