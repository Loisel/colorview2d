# coding: utf-8
import colorview2d
data = np.random.random((100, 100))
xrange = (0., np.random.random())
yrange = (0., np.random.random())
datafile = colorview2d.Datafile(data, (yrange, xrange))
cvfig = colorview2d.CvFig(datafile)
cvfig.config['Xlabel'] = 'foo (f)'
cvfig.config['Ylabel'] = 'bar (b)'
cvfig.config['Cblabel'] = 'nicyness (n)'
cvfig.show_plt_fig()
cvfig.config.update({'Font': 'Ubuntu', 'Fontsize': 16})
cvfig.config['Colormap'] = 'Blues'
cvfig.plot_pdf('Nice_unmodified.pdf')
cvfig.save_config('Nice_unmodified.cv2d')
cvfig.add_mod('Smooth', (1, 1))
cvfig.add_mod('Derive')
cvfig.config.update({'Cbmin':0.0, 'Cbmax':0.1})
colorview2d.fileloaders.save_gpfile('Nice_smooth_and_derived.dat', cvfig.datafile)
