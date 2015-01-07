Animation Example
=================

How to create animations using OpenLDraw. Useful ideas about how to configure LDView for this purpose can be found `here <http://www.holly-wood.it/ldview-en.html>`_.

Step 1
------

Create the lcad file. ::

  (import locate :local)

  (def axle1 ()
   (block

    ; Axle 4
    (tb 0 0 -0.5 0 90 0 "3705" "Black")

    ; Gear 8 Tooth
    (tb 0 0 0 0 0 0 "3647" "Dark_Gray")
  
    ))

  (def axle2 ()
   (block

    ; Axle 5
    (tb 0 0 0 0 90 0 "32073" "Light_Gray")

    ; Gear 8 Tooth
    (tb 0 0 1 0 0 0 "3647" "Dark_Gray")

    ; Gear 24 Tooth with Single Axle Hole
    (tb 0 0 -1 0 0 0 "3648b" "Dark_Gray")

    ))
  
  (def axle3 ()
   (block
  
    ; Axle 5
    (tb 0 0 0 0 90 0 "32073" "Light_Gray")

    ; Gear 24 Tooth with Single Axle Hole
    (tb 0 0 1 0 0 0 "3648b" "Dark_Gray")

    ))

  (def angle1 (* time-index 5))
  (def angle2 (+ 7.5 (/ angle1 3)))
  (def angle3 (+ 7.5 (/ angle2 3)))

  (translate (0 0 (bw -1))
   (rotate (0 0 angle1)
    (axle1)))

  (translate (0 (bw 2) 0)
   (rotate (0 0 (- angle2))
    (axle2)))

  (translate ((bw 2) (bw 2) 0)
   (rotate (0 0 angle3)
    (axle3)))

.. note::

   *time-index* is the animation variable. It will count up from 0 in increments of 1.

.. note::
   
   This is the gears.lcad file in the examples folder.
   
Step 2
------

Create a directory to save the .dat files in, change to this directory and generate the dat files. ::

  cd openldraw/examples
  mkdir animate
  cd animate
  python ../../lcad_to_ldraw.py ../gears.lcad gears.dat 100

.. note::

   This will make 100 different versions of the gears.dat file (time-index = 0..99).

Step 3
------

Generate the png files in the same directory. ::

  python ../../misc/ldview_render.py ./

.. note::

   Edit the options in ldview_render.py depending on the desired results (point of view, background color, etc..)

Step 4
------

Create a movie. I find `ImageJ <http://fiji.sc/Fiji>`_ be a handy tool for this. You can import the series of .png files as an image sequence (File -> Import -> Image Sequence).
