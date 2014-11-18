
### Install instructions for emacs. ###

Consult [this](http://www.gnu.org/software/emacs/manual/html_node/emacs/Windows-HOME.html) to find the location of your emacs home directory on Windows.

1. Add a sub-folder to your .emacs.d directory called "lcad-mode"
2. Copy the lcad-mode.el file into this directory.
3. Add the following to your .emacs file:
```
(add-to-list 'load-path "~/.emacs.d/lcad-mode")
(require 'lcad-mode)
```
