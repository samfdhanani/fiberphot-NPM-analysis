### Analyzing Neurophotometrics FP3002 data with Python.

All code has been adapted from:

Martianova, E., Aronson, S., Proulx, C.D. Multi-Fiber Photometry to Record Neural Activity in Freely Moving Animal.. J. Vis. Exp. (152), e60278, doi: 10.3791/60278 (2019).
https://github.com/katemartian/Photometry_data_processing

## The Bonsai workflow
All node structures and workflows are from the Neurophotmetrics Bonsai Textbook linked here:
https://static1.squarespace.com/static/60ff345fca665d50e1adc805/t/65366fc82f93fd1b67b65a5b/1698066378544/BonsaiGuide_20231023.pdf

**Outputs**
1. SubjectID.csv
   - the raw data file.
2. SubjectIDStart.csv
   - a file containing the timestamp of when you want to start the session after a period of photobleaching.
3. SubjectIDInjection.csv
   - a file containing two timestamps, one right before you pick up the mouse to administer and injection and the second after the mouse is placed in the open field following the injection.
4. SubjectIDHandle.csv
   - this file contains pairs of timestamps indicating the times before and after manually handling a mouse in the open field. 

## Transforming the data files before plotting and calculating the zdFF scores

