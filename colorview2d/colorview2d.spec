# -*- mode: python -*-
a = Analysis(['__main__.py'],
             pathex=['C:\\Users\\LocalAdmin\\Desktop\\colorview2d\\colorview2d'],
             hiddenimports=['scipy.special._ufuncs_cxx','scipy.integrate',
				'scipy.integrate.quadrature','scipy.integrate.odepack','scipy.integrate._odepack',
				'scipy.integrate.quadpack','scipy.integrate._quadpack','scipy.integrate._ode',
				'scipy.integrate.vode','scipy.integrate._dop','scipy.integrate.lsoda'],
             hookspath=None,
             runtime_hooks=None)
import glob
import os
list_yapsy = glob.glob('Mods/*.yapsy-plugin')
list_py = glob.glob('Mods/*.py')
list_yapsy += list_py
print list_yapsy
for file in list_yapsy:
	a.datas += [(file,file,'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='colorview2d.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True , icon='icon\\icon.ico')
