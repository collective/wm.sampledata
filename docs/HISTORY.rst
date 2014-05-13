Changelog
#########

dev
===

- errors raised in finally clause did not pop up with debug=True

- added utility function ``createFile`` to create file-content the same way
  as ``createImage`` creates image-content.

0.2.2 (2013-05-08)
==================

- add traceback logging on errors [saily]

- added utility functions (``utils.getImage`` and ``utils.getRandomImage``) to
  download images from lorempixel.com (see wm.sampledata.example for usage)
  [fRiSi]

- more intuitive syntax for blockPortlets (change breaks backward
  compatibility) [fRiSi]

0.2.1 (2012-05-29)
==================

- fix links for running plugins so they work for
  http://host/plonesite/@@sampledata, too. (not just http://host/@@sampledata)
  [fRiSi]

- added utility method `constrainTypes` to set which objects an be added to
  folderish objects [fRiSi]

0.2 (2011-12-02)
================

- ``SampledataView.runPlugin`` returns the result of ``Plugin.generate``. This
  makes it easy to check if the plugin was sucessfully run in unittests.

0.1 (2011-01-31)
================

- Initial release
