from distutils.core import setup
setup(name='imcodes',
      version='1.0',
      py_modules=['imcodes'],
      description='Imagination.Codes module package to web interface tool',
      author='Michael Oneppo',
			requires=['pyyaml', 'jinja', 'markdown'],
      author_email='moneppo@gmail.com',
      )