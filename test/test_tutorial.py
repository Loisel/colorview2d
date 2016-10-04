# coding: utf-8
import colorview2d
import numpy as np
data = np.random.random((100, 100))
xrange = (0., 0.1)
yrange = (0., 0.2)
data = colorview2d.Data(data, (yrange, xrange))
view = colorview2d.View(data)
view.config['Xlabel'] = 'foo (f)'
view.config['Ylabel'] = 'bar (b)'
view.config['Cblabel'] = 'nicyness (n)'
view.show_plt_fig()
view.config.update({'Font': 'Ubuntu', 'Fontsize': 16})
view.config['Colormap'] = 'Blues'
view.plot_pdf('Nice_unmodified.pdf')
view.save_config('Nice_unmodified.cv2d')
view.add_mod('Smooth', (3, 3))
view.add_mod('Derive')
view.config.update({'Cbmin':0.0, 'Cbmax':0.1})
colorview2d.fileloaders.save_gpfile('Nice_smooth_and_derived.dat', view.data)
import matplotlib.pyplot as plt
fig = plt.figure()
axes = fig.add_subplot(111)
axes.set_xlabel(view.config['Xlabel'])
axes.set_ylabel(view.config['Cblabel'])
linetraces = view.data.extract_xlinetrace_series(0.04, 0.08, 0.005, 0.02, 0.06)
for trace in linetraces[:-1]:
    axes.plot(linetraces[-1], trace)
fig.show()
