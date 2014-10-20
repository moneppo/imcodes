IMCODES
-------
Python utility for module creation.

Usage
-----
```
chmod +x imcodes.py
./imcodes.py <zipped module archive>
```

Running Modules
---------------
You'll need to place the built files from [jsrepl](https://github.com/replit/jsrepl) (placed in the `build` directory) in a `jsrepl` directory at the root of the unzipped resulting module directory. From that, run 
```
python -m SimpleHTTPServer
```
to view the module.