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
		row_count = tile_shape if tile_shape else 0
	else:
		tile_shape = list(tile_shape)
		if n < 2:
			tile_shape += [0]*(2-n)
		row_count, column_count = tile_shape
	if transpose:
		ro_count, col_count = column_count, row_count
	else:
		ro_count, col_count = row_count, column_count
	if ro_count:
		rows = [e for e, _ in zip(images, range(ro_count))]
	else:
		rows = list(images)
	ro_count = len(rows)
	if not ro_count:
		print('`images` is empty!')
		return
	if key is not None:
		rows = list(map(key, rows))
	try:
		rows[0].shape
	except AttributeError:
		for i in range(ro_count):
			if col_count:
				rows[i] = [e for e, _ in zip(rows[i], range(col_count))]
			else:
				rows[i] = list(rows[i])
		col_count = len(rows[0])
		if col_count == 1:
			rows = [e[0] for e in rows]
		elif ro_count == 1:
			rows = rows[0]
	else:
		col_count = 1
	if transpose:
		figure, axes = plt.subplots(col_count, ro_count)
	else:
		figure, axes = plt.subplots(ro_count, col_count)
	figure.set_size_inches(figsize)
	if ro_count == 1 or col_count == 1:
		if ro_count == 1 and col_count == 1:
			axes.imshow(rows[0])
			axes.axis('off')
		else:
			for i, img in enumerate(rows):
				axes[i].imshow(img)
				axes[i].axis('off')
		plt.show()
		return
	for i in range(ro_count):
		for j in range(col_count):
			if transpose:
				axes[j, i].imshow(rows[i][j])
				axes[j, i].axis('off')
			else:
				axes[i, j].imshow(rows[i][j])
				axes[i, j].axis('off')
	plt.show()
