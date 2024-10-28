# -*- coding: utf-8 -*-

import tensorflow as tf
from tensorflow.keras import layers as lay
from tensorflow.keras import utils as uti


def null_lines(df, axis=0):
	if axis:
		na = np.zeros(len(df.columns), dtype=bool)
		for index, row in df.isnull().iterrows():
			na |= row.values
		df_na = df[df.columns[na]]
	else:
		na = np.zeros(len(df), dtype=bool)
		for nm, column in df.isnull().items():
			na |= column
		df_na = df[na]
	return df_na


def get_image(filepath):
	image = tf.io.read_file(str(filepath))
	image = tf.io.decode_image(image)
	# image = tf.io.decode_jpeg(image)
	return image


@tf.function
def sorensen_dice_coef(y_true, y_pred):
	y_pred = tf.math.argmax(y_pred, axis=-1, output_type=tf.uint16)
	intersection = tf.cast(y_true == y_pred, tf.int32)
	# tf.config.run_functions_eagerly(True)
	# display(intersection[:2,:2,:2].numpy())
	return tf.keras.ops.sum(intersection) / tf.reduce_prod(intersection.shape)


class UNetDescendingCell(tf.keras.Model):
  """ Descending cell"""

	def __init__(self, filters, pooling=2, norm=True, is_first=False):
		super().__init__()
		self.is_first = is_first
		self.batch_norm = norm
		self.mxpool = lay.MaxPooling2D(pooling)
		self.conv2d1 = lay.Conv2D(filters, (3, 3), padding='same', activation='relu')
		self.batch1 = lay.BatchNormalization()
		self.conv2d2 = lay.Conv2D(filters, (3, 3), padding='same', activation='relu')
		self.batch2 = lay.BatchNormalization()

	def call(self, x):
		if not self.is_first:
			x = self.mxpool(x)
		x = self.conv2d1(x)
		if self.batch_norm:
			x = self.batch1(x)
		x = self.conv2d2(x)
		if self.batch_norm:
			x = self.batch2(x)
		return x


class UNetAscendingCell(tf.keras.Model):
  """ Ascending cell"""

	def __init__(self, filters, upscale=2, norm=True, is_last=False):
		super().__init__()
		self.is_last = is_last
		self.batch_norm = norm
		self.conv2d_tra = lay.Conv2DTranspose(32, (upscale, upscale), strides=(upscale, upscale), padding='same', activation='relu')
		self.batch0 = lay.BatchNormalization()
		self.conv2d1 = lay.Conv2D(filters, (3, 3), padding='same', activation='relu')
		self.batch1 = lay.BatchNormalization()
		self.conv2d2 = lay.Conv2D(filters, (3, 3), padding='same', activation='relu')
		self.batch2 = lay.BatchNormalization()

	def call(self, x):
		x = self.conv2d1(x)
		if self.batch_norm:
			x = self.batch1(x)
		x = self.conv2d2(x)
		if self.batch_norm:
			x = self.batch2(x)
		if self.is_last:
			return x
		if self.batch_norm:
			x = self.batch0(x)
		return self.conv2d_tra(x)


class UNetSimple(tf.keras.Model):

	def __init__(self, filters=32, scale=4, norm=False):
		super().__init__()
		self.batch_norm = norm
		self.und1 = UNetDescendingCell(filters, scale, norm, True)
		self.und2 = UNetDescendingCell(filters*2, scale, norm)
		self.und3 = UNetDescendingCell(filters*4, scale, norm)
		self.conv2d_tra = lay.Conv2DTranspose(filters*2, (scale, scale), strides=(scale, scale), padding='same', activation='relu')
		self.batch0 = lay.BatchNormalization()
		self.unu2 = UNetAscendingCell(filters*2, scale, norm)
		self.unu1 = UNetAscendingCell(filters, scale, norm, True)

	def call(self, inputs):
		out1 = self.und1(inputs)
		out2 = self.und2(out1)
		x = self.und3(out2)
		x = self.conv2d_tra(x)
		if self.batch_norm:
			x = self.batch0(x)
		x = lay.concatenate([x, out2])
		x = self.unu2(x)
		x = lay.concatenate([x, out1])
		return self.unu1(x)


class UNet(tf.keras.Model):

	def __init__(self, filters=64, scale=2, norm=True):
		super().__init__()
		self.batch_norm = norm
		self.und1 = UNetDescendingCell(filters, scale, norm, True)
		self.und2 = UNetDescendingCell(filters*2, scale, norm)
		self.und3 = UNetDescendingCell(filters*4, scale, norm)
		self.und4 = UNetDescendingCell(filters*8, scale, norm)
		self.conv2d_tra = lay.Conv2DTranspose(filters*4, (scale, scale), strides=(scale, scale), padding='same', activation='relu')
		self.batch0 = lay.BatchNormalization()
		self.unu3 = UNetAscendingCell(filters*4, scale, norm)
		self.unu2 = UNetAscendingCell(filters*2, scale, norm)
		self.unu1 = UNetAscendingCell(filters, scale, norm, True)

	def call(self, inputs):
		out1 = self.und1(inputs)
		out2 = self.und2(out1)
		out3 = self.und3(out2)
		x = self.und4(out3)
		x = self.conv2d_tra(x)
		if self.batch_norm:
			x = self.batch0(x)
		x = lay.concatenate([x, out3])
		x = self.unu3(x)
		x = lay.concatenate([x, out2])
		x = self.unu2(x)
		x = lay.concatenate([x, out1])
		return self.unu1(x)


def create_unet(input_shape=(None, None, 3), Unet=UNet):
	inputs = tf.keras.Input(shape=input_shape)
	x = Unet(inputs)
	x = lay.Conv2D(7,(3,3), activation='softmax', padding='same')(x)
	model = tf.keras.Model(inputs, x)
	model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
				loss='sparse_categorical_crossentropy',
				metrics=['sparse_categorical_accuracy'])
	model.summary()
	display(uti.plot_model(model, dpi=60, show_shapes=True))
	return model


class Layer(tf.keras.layers.Layer):

	@classmethod
	def from_config(cls, config):
		return cls(**config)

	def get_config(self):
		config = super().get_config()
		config['output_shape'] = self.output_shape

	def __init__(self, output_shape, **kwargs):
		self.output_shape = output_shape
		super().__init__(**kwargs)

	def build(self, input_shape):
		shape = tf.TensorShape((input_shape[1], self.output_shape))
		# Создаем переменную тренируемого веса для этого слоя.
		self.kernel = self.add_weight(name='kernel',
								shape=shape,
								initializer='uniform',
								trainable=True)
		super().build(input_shape)

	def call(self, inputs):
		return tf.matmul(inputs, self.kernel)

	def compute_output_shape(self, input_shape):
		shape = tf.TensorShape(input_shape).as_list()
		shape[-1] = self.output_shape
		return tf.TensorShape(shape)


