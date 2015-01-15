# -*- mode: python -*-
a = Analysis(['colorview2d.py'],
             pathex=['C:\\Users\\LocalAdmin\\Desktop\\colorview2d\\colorview2d'],
             hiddenimports=['scipy.special._ufuncs_cxx','scipy.integrate',
				'scipy.integrate.quadrature','scipy.integrate.odepack','scipy.integrate._odepack',
				'scipy.integrate.quadpack','scipy.integrate._quadpack','scipy.integrate._ode',
				'scipy.integrate.vode','scipy.integrate._dop','scipy.integrate.lsoda'],
             hookspath=None,
             runtime_hooks=None)
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
