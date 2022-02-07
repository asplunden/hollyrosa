/**
* Copyright 2010-2020 Martin Eliasson
*
* This file is part of Hollyrosa
*
* Hollyrosa is free software: you can redistribute it and/or modify
* it under the terms of the GNU Affero General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* Hollyrosa is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU Affero General Public License for more details.
*
* You should have received a copy of the GNU Affero General Public License
* along with Hollyrosa.  If not, see <http://www.gnu.org/licenses/>.
**/

/* for booking_day.html */
function set_visible_ag_rows(acg_id, v) {
  var elems = dojo.query("[hollyrosa:acgid]");
  dojo.forEach(elems, function(elem) {
    var agc_val = dojo.attr(elem, 'hollyrosa:acgid');
    if (agc_val == acg_id) {
      dojo.style(elem, {display: v});
    }
  } );
}


function navigation_calendar_is_disabled(x) {
  var test_date = dojo.date.locale.format(x, {datePattern: "yyyy-MM-dd", selector: "date"});
  return test_date < "2022-05-01" || test_date > "2022-10-31";
}


// TODO: who is using these functions
function transfer_date(to_ement, date) {
  e.value = date;
}


function transfer_to_booking_request_fromdate() {
  var e = dojo.byId('visiting_group_data_fromdate');
  var value = e.innerHTML;
  transfer_from_date(value);
}


function transfer_to_booking_request_todate() {
  var e = dojo.byId('visiting_group_data_todate');
  var value = e.innerHTML;
  transfer_to_date(value);
}
