# coding: utf-8
import colorview2d
data = np.random.random((100, 100))
xrange = (0., np.random.random())
yrange = (0., np.random.random())
datafile = colorview2d.Datafile(data, (yrange, xrange))
view = colorview2d.View(datafile)
view.config['Xlabel'] = 'foo (f)'
view.config['Ylabel'] = 'bar (b)'
view.config['Cblabel'] = 'nicyness (n)'
view.show_plt_fig()
view.config.update({'Font': 'Ubuntu', 'Fontsize': 16})
view.config['Colormap'] = 'Blues'
view.plot_pdf('Nice_unmodified.pdf')
view.save_config('Nice_unmodified.cv2d')
view.add_mod('Smooth', (1, 1))
view.add_mod('Derive')
view.config.update({'Cbmin':0.0, 'Cbmax':0.1})
colorview2d.fileloaders.save_gpfile('Nice_smooth_and_derived.dat', view.datafile)
