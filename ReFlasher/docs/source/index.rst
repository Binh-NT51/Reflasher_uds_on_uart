.. reflasher documentation master file, created by
   sphinx-quickstart on Thu Dec 29 16:43:58 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to reflasher's documentation!
=====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

##################
Development Guide
##################
This document guides the reader how to improve or customize the tool by modify the tool itself.

===========
Environment
===========
Refer ReadMe.md document to set up the environment.

Other tools: VsCode

===========
Guide
===========

Modify the GUI
**************
The GUI is designed and implemented by pyQt5 library. 

   * To open the GUI, go to the installation path of pyQt5 in python3 directory and run QtDesigner.

   * Then, open QtDesigner project in `reflasher\libs\designer\Flasher.ui`

      .. image:: /../images/OpenQtDesigner.PNG
         :width: 1000   
         :alt: Open QtDesigner

   * Please refer the document of pyQt5 for how to modify the GUI.

Modify download sequence
*************************
The download sequence is implemented in `reflasher\libs\reflash\Flashing.py`.
The developer can add more services into the download sequence.
Besides that, developer can modify other modules: logger, uarttp, and config.ini.


