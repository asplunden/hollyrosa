## Synopsis

Hollyrosa is a special developed program booking system for a scout centre called Vässarö, located on an island in Sweden. It's tailore made for Vässarö, the culture and the ways we do things. Many centers use or look for activity booking systems, however, scouting simply isn't a set of activities ona patch of grass. I have therfore decided to design and build a *program booking system*, a system that help us make a better scout program for both visiting groups and staff. We believe being a staff member is/could be part of the scout program and this has guided design decisions in this system. 

Some design decisions are just mad becuase the way we do things at Vässarö, For example, all program are free for groups at the island, so the system has no support at this time for billing which otherwise is quite common.

The system is built on Turbogears2 and is a little bit odd in that it uses CouchDB 1.x as backend, it does however alow master-master replication which in our case is a critical requirement.

## Motivation

This project exist to make it possible for more kids and youth to have a great summer and scout experience. It also exists to enable our goal to empower young people, it does so by the single
fact that it makes progeram booking distributed and so our young staff can handle the system and we old program people can just monitor and check that all looks ok.

## Installation

You will need a running couchdb 1 instance. I would recommend that you run couchdb1 in a docker container mapping the data folder to the host machine somewhere.

You can install the system as a Turbogears2 app and in production you may run it using Apache+mod_wsgi. You will also need to use the hollyrosa_viewtool to upload views to your CouchDB database. 

### TinyMCE 4 Source

TinyMCE v4 is not included with this codebase, it must be downloaded separately.

Download from http://download.tiny.cloud/tinymce/community/tinymce_4.9.7.zip and unzip into the public folder.

Another option is to change the links in the TinyMCE4Widget to point to the CDNs for tinymce.

```
cd <path to public>
wget http://download.tiny.cloud/tinymce/community/tinymce_4.9.7.zip
unzip tinymce_4.9.7.zip
rm tinymce_4.9.7.zip
```

## License

Hollyrosa is Copyright 2010-2018 Martin Eliasson

Hollyrosa is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Hollyrosa is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Hollyrosa.  If not, see <http://www.gnu.org/licenses/>.
