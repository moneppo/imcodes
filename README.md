IMCODES
-------
Python utility for module creation.

Usage
-----
```
chmod +x imcodes.py
./imcodes.py -o <output zip file name> [-f] <zipped module archive>
```
`-f` Indicates that the module isn't an archive but rather a folder. Useful for testing.

Running Modules
---------------
Unzip the module into a directory. An example has been placed in the directory "output". Navigate to the unzipped folder and run:
```
python -m SimpleHTTPServer
```
to view the module.
