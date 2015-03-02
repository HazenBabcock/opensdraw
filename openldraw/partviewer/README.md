
### Summary ###
This is a viewer for finding the part and color information that you will need to add a part in a .lcad file. In order for it to work properly you will first need to run misc/make_parts_xml.py against your current ldraw/parts directory to generate your own version of the parts.xml file. 

```
cd openldraw/openldraw/xml
python ../scripts/make_parts_xml.py /path/to/ldraw/parts/
```   

Once this is done you can run the viewer like this:

```python partviewer.py```
