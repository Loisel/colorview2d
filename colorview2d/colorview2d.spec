# -*- mode: python -*-

block_cipher = None


a = Analysis(['colorview2d.py'],
             pathex=['/home/al/colorview2d/colorview2d'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             excludes=['zmq'],
             cipher=block_cipher)

a.datas += [('default.config','default.config','DATA')]
a.datas += [('demo.dat','demo.dat','DATA')]

pyz = PYZ(a.pure,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='colorview2d',
          debug=False,
          strip=None,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='colorview2d')
