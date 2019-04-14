Asssess TODO:

Legend:
- To do
+ Done
* Postponed
% Rejected

LANGUAGE
- Item language translations
- Data table header translations
- App language 

GENERAL
+ Unify urls.py methodology
+ Get rid of context preprocessors, 
+ make context function for navigation links in base app 
+ fix navigation links in views
* Create meta data table with meta information from each itemset and data table
* Enable loading of several or all item/data tables from Excel file

DOCUMENTATION
- Separate between public and private class variables with __xx
- Docstrings for function input and output in the big classes/modules (table, models, history, views)

TESTS
- Figure out how to make good tests

HISTORY

LOGGING
- Log error messages when batch uploading from an entire spreadsheet
- Sanity check upload without actually writing data to database

ITEMS
- items.rename(): Update item description table with the renamed item label
- items.delete(): Get names of all tables in choice and data app that have item as ForeignKey
  -> mark "archived" all entries with the deleted item(s)
  -> present count of deleted data lines by app/table

+ Get rid of csv.py, possibly by using a one-dimensional map?
+ Consider versioning of items, to allow choices to be deletable items (delete should close all current records with a deleted item)
  + add versioning columns to item models
  + modify get_column_items() so that only current, but not proposed and archived items are loaded
  + modify views to handle version numbering
    + view itemDelete(): GET is item.delete()
    + view itemUpload(): GET is form, POST is submit upload -> call item.upload(csv_string)
    + view itemCreate(): GET is form, POST is new item name submit
    + view itemRename(): GET is form, POST is item new name submit
  + modify ItemModel
    + delete()
    + create()
      + make sure that new item has unique label compared to current version of all labels
    + upload()
      + make sure that new items are unique among current items, see create()
      + raise warning to user whe uploading existing labels
    + rename()
      + make sure that renamed item is still unique
         + raise warning to user when uploading existing labels 
         + Do not update versioning information on renaming
+ Consider whether it should be allowed to change label names (YES it should)
+ Consider whether label name change should be a versioned change (NOT it should not, need to stick with item__id not to mess up data tables)
+ Consider adding viewing order for items (NO, dont. Better delete items and reload in new order, incl. reload all new data)

MAPS
- Create maps class with CSV import and table printing (or stick with table class with 'map'=True/False)
- Implement functions:
  => load_model()
  => remove_previous_duplicates() <- is this necessary, since we do not use dataframes?
  => load_csv()
  => validate_column_headers()
  => validate_column_data()
  => changed_records()
  => save_ ?
  => commit_rows()
  => revert_proposed()
  => proposed_count()

TABLES
- Figure out whether table class should also include maps with no value
- Possibly new data structure for keys (list of tuples?)

DATA
- Figure out how to load CSV data in row/column format 
- Validation of CSV column and index data
+ Proposed must show correctly diff and view
+ Add revert version as method to table
+ Enable pivoting by user chosen indices for views
+ Enable pivoting by user chosen indices for diffs
- Make sure that dataframes are loaded distinguishing appropriately between indices and series
* Enable filtering of tables in views (perhaps jQuery or other non-django stuff)
* Enable loading of several or all data tables from Excel file

CHOICES
+ Figure out how to best link choices to items, possibly add "choice item" from choices menu ... 
  => Choices options are modelled as items, choices data is modelled as tables
- Consider how to use formsets for choices, or figure out alternative solution (e.g. a page per choice)
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

