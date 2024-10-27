# -*- coding: utf-8 -*-

import seaborn as sns


def nulls(df):
	if len(df):
		sns.heatmap(df.isnull(), yticklabels=False, cmap='viridis')
		plt.show()

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



