# Specific Notes on How to Use Hollyrosa

## Multi-language support
The language choice in Hollyrosa require some background.

It has been quite common with international staff in program, therefore, the UI in Hollyrosa
is primarily English.

Most groups are Swedish and some Swedish leaders are not comfortable with English, therefore are
the pages listing bookings that we print and send to the groups in Swedish and so are the title and
descriptions of the activities.

To be able to give international groups an English version of the program listing we send to them,
there is now a way to set the language of a visiting group.

The three supported languages are
 * Swedish ( se-SV )
 * English ( us-EN )
 * German ( de-DE )

 The default language is Swedish.

 The general rule is: if a groups has not language specified, the default is assumed.

## Adding languages to specific activities
By default, the language of any activity is Swedish but the title and the description of an
activity may be specified in a different language.

It is important that we don't add lots of language versions to activities and then don't update them,
therefore it is currently only possible to add language versions by directly editing in the database.

An activity can have one or more language versions. When the activity view is shown, the language can
be changed. When editing an activity, it is the currently selected language that is edited.

Activities can have a note, this is the note shown in the list of bookings for activities like Trapper.

Adding language versions of these notes can be done, but currently only by directly editing the database.

## Adding specific activity note to an activity
The notes system for groups have been reused, the way to add a note is to:
 * go to any visiting group
 * add a note (but don't save!)
 * change the target_id in the URL to be a target_id of an activity
 * save

 
