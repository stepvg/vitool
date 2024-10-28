# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns


def nulls(df, ax=None):
	if len(df):
		sns.heatmap(df.isnull(), yticklabels=False, cmap='viridis', ax=ax)


def violinplot(df, ax=None):
	sns.violinplot(data=df, density_norm='width', inner='quartile', orient='h', ax=ax)


def correlogram(df, cmap=None, title_fontsize=20, ticks_fontsize=10, ax=None):
	if cmap is None:
		cmap = LinearSegmentedColormap.from_list('LbBlRdLy', ['lightblue', 'b', 'r','lightyellow'], 256)
	sns.heatmap(df.corr(), xticklabels=df.columns, yticklabels=df.columns, cmap=cmap, annot=True, center=0, vmin=-1, vmax=1, ax=ax)
	if ax is None:
		ax = plt.gca()
	ax.set_title('Correlogram', fontsize=title_fontsize)
	ax.tick_params(labelsize=ticks_fontsize)


def history(history, figsize=(12, 4), facecolor='lightgray', grid=True):
	"""
	Graph of the loss function of the training and validation sets.
	Graphs of the metric functions of the training and validation sets.
	"""
	figure, axes = plt.subplots(nrows=1, ncols=2, figsize=figsize)
	figure.set_facecolor(facecolor)
	for name in history.history.keys():
		id = int('loss' not in name)
		axes[id].legend()
		axes[id].grid(grid)
		axes[id].plot(history.history[name], label=name)
	plt.tight_layout()
	plt.show()


def class_balance(class_sizes, class_names=None, title='Количество', color=['blue', 'magenta'], ax=None):
	"""
	Horizontal bar chart.
	The length of the bars is specified in `class_sizes`.
	The labels of the bars are specified in `class_names`.
	"""
	if ax is None:
		ax = plt.gca()
	class_count = range(len(class_sizes))
	if class_names is None:
		class_names = class_count
	ax.barh(class_count, class_sizes, color=color, tick_label=class_names)
	ax.set_title(title)


def images(images, key=None, transpose=False, tile_shape=None, figsize=(16, 9)):
	try:
		n = tile_shape.__len__()
	except AttributeError:
		column_count = 0
		raw_count = tile_shape if tile_shape else 0
	else:
		tile_shape = list(tile_shape)
		if n < 2:
			tile_shape += [0]*(2-n)
		raw_count, column_count = tile_shape
	if transpose:
		ra_count, col_count = column_count, raw_count
	else:
		ra_count, col_count = raw_count, column_count
	if ra_count:
		raws = [e for e, _ in zip(images, range(ra_count))]
	else:
		raws = list(images)
	ra_count = len(raws)
	if not ra_count:
		print('`images` is empty!')
		return
	if key is not None:
		raws = list(map(key, raws))
	try:
		raws[0].shape
	except AttributeError:
		for i in range(ra_count):
			if col_count:
				raws[i] = [e for e, _ in zip(raws[i], range(col_count))]
			else:
				raws[i] = list(raws[i])
		col_count = len(raws[0])
		if col_count == 1:
			raws = [e[0] for e in raws]
		elif ra_count == 1:
			raws = raws[0]
	else:
		col_count = 1
	if transpose:
		figure, axes = plt.subplots(col_count, ra_count)
	else:
		figure, axes = plt.subplots(ra_count, col_count)
	figure.set_size_inches(figsize)
	if ra_count == 1 or col_count == 1:
		if ra_count == 1 and col_count == 1:
			axes.imshow(raws[0])
			axes.axis('off')
		else:
			for i, img in enumerate(raws):
				axes[i].imshow(img)
				axes[i].axis('off')
		plt.show()
		return
	for i in range(ra_count):
		for j in range(col_count):
			if transpose:
				axes[j, i].imshow(raws[i][j])
				axes[j, i].axis('off')
			else:
				axes[i, j].imshow(raws[i][j])
				axes[i, j].axis('off')
	plt.show()
