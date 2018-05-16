# ims.fieldupdater

This project was inspired by Products.KeywordManager and applies some of its ideas to replacing schema field values
on content. Unlike that package, this one is based on schema field and not KeywordIndex. This allows you to change
different kinds of values whether or not they are indexed, but it is also a more expensive process.

## Process
- Select a schema. This is an object_provides value and/or a registered Dexterity behavior
- Select a field
- (DataGridField only - select one of the DictRow keys)
- Select one of the existing values on the site to constitute a match
- Enter a new value to replace the match (if replacing)
- Delete or replace

## The power of zope.schema

One of the nice things about zope.schema is that once we know which field
we are changing, we can look it up in the schema and use it for
- rendering an input widget
- data extraction/parsing
- validation
