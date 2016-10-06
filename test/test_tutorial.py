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
view.add_Smooth(3, 3)
view.add_Derive()
view.config.update({'Cbmin':0.0, 'Cbmax':0.1})
colorview2d.fileloaders.save_gpfile('Nice_smooth_and_derived.dat', view.data)
