Asssess TODO:

Legend:
- To do
+ Done
* Postponed

LANGUAGE
- Item language translations
- Data table header translations
- App language 

GENERAL
+ Unify urls.py methodology
+ Get rid of context preprocessors, 
+ make context function for navigation links in base app 
+ fix navigation links in views

DOCUMENTATION
- Separate between public and private class variables with __xx
- Docstrings for function input and output in the big classes/modules (table, models, history, views)

TESTS
- FIgure out how to make tests

TABLES
- Figure out whether table class should also include maps with no value
- Possibly new data structure for keys (list of tuples?)

HISTORY

MAPS
- Create maps class with CSV import and table printing

ITEMS
- Get rid of csv.py, possibly by using a one-dimensional map?
* Add versioning for items
* Enable loading of several or all item tables from Excel file
 
DATA
+ Proposed must show correctly diff and view
+ Add revert version as method to table
+ Enable pivoting by user chosen indices for views
+ Enable pivoting by user chosen indices for diffs 
- Validation of CSV column and index data
* Enable filtering of tables in views (perhaps jQuery or other non-django stuff)
* Enable loading of several or all data tables from Excel file

CHOICES
+ Create choices class with import and table printing
+ Streamline choices and data app to use as much shared functionality as possible, move views to base app

SCENARIOS


RESULTS
- Tables
- Table Pivot 
- Table filtering

- Standard charts
- BarTotal by scenario (in storyline)
- BarBreakdown by scenario (in storyline)
- Line by time and (scenario or item)
