
### Summary ###
This is a viewer for finding the part and color information that you will need to add a part in a .lcad file. In order for it to work properly you will first need to make sure that the ldraw_path.xml file (in the opensdraw/xml folder) has the correct path to your LDraw parts directory.

Once this is done you can run the viewer like this:

```python partviewer.py```

The first time you run partviewer will take a while (15-30 minutes) to start as it will generate thumbnails of all the parts.

When it is running it will also generate a file called "ldview_part.mpd" that you can load with a viewer like LDView to view and manipulate the currently selected part in the currently selected color.
