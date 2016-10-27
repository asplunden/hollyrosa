# -*- coding: utf-8 -*-
"""
Copyright 2010 - 2016 Martin Eliasson

This file is part of Hollyrosa

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

"""

import logging,  datetime

import transaction
from tg import config

from hollyrosa.config.environment import load_environment
from hollyrosa import model

__all__ = ['setup_app']

log = logging.getLogger(__name__)


def make_booking_day(date):
    """
    This year, all booking days will look exactly the same, so what matters is 
    """
    
    #...make a day and tie it to the only DaySchema
    booking_day = model.BookingDay()
    booking_day.date = date
    booking_day.day_schema_id = 1
    model.DBSession.add(booking_day)
    
def makeActivityGroup(name):
    ag = model.ActivityGroup()
    ag.title = name
    ag.description = name
    model.DBSession.add(ag)
    return ag
    
def makeActivity(name,  activity_group,  capacity,  bg_color=None,  guides_per_day=0,  guides_per_slot=0,  default_booking_state=0):
    a = model.Activity()
    a.title = name
    a.description = name
    a.activity_group = activity_group
    a.guides_per_slot = guides_per_slot
    a.guides_per_day = guides_per_day
    a.capacity = capacity
    a.default_booking_state = default_booking_state
    
    
    if bg_color != None:
        a.bg_color = bg_color
    
    return a
    
def makeSlotRows(n,  activity):
    """make n slot rows with activity"""
    result = []
    for x in range(n):
        slot_row_o = model.SlotRow()
        slot_row_o.slot_row_schema = 'N/A'
        slot_row_o.activity = activity
        result.append(slot_row_o)
    return  result


def setup_app(command, conf, vars):
    """Place any commands to setup hollyrosa here"""
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
    
    
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)

    manager = model.User()
    manager.user_name = u'manager'
    manager.display_name = u'Example manager'
    manager.email_address = u'manager@somedomain.com'
    manager.password = u'managepass'

    model.DBSession.add(manager)

    group = model.Group()
    group.group_name = u'managers'
    group.display_name = u'Managers Group'

    group.users.append(manager)

    model.DBSession.add(group)
    
    #...PL group
    group_pl = model.Group()
    group_pl.group_name = u'pl'
    group_pl.display_name = u'Program leaders and sea leaders'

    group_pl.users.append(manager)

    model.DBSession.add(group_pl)
    
    #...staff group
    group_staff = model.Group()
    group_staff.group_name = u'staff'
    group_staff.display_name = u'Staff members'

    group_staff.users.append(manager)

    model.DBSession.add(group_staff)
    

    permission = model.Permission()
    permission.permission_name = u'manage'
    permission.description = u'This permission give an administrative right to the bearer'
    permission.groups.append(group)
    
    #...pl permission
    permission_pl = model.Permission()
    permission_pl.permission_name = u'pl'
    permission_pl.description = u''
    permission_pl.groups.append(group_pl)
    
    #...staff permission
    permission_staff = model.Permission()
    permission_staff.permission_name = u'staff'
    permission_staff.description = u''
    permission_staff.groups.append(group_staff)
    

    model.DBSession.add(permission)

    editor = model.User()
    editor.user_name = u'editor'
    editor.display_name = u'Example editor'
    editor.email_address = u'editor@somedomain.com'
    editor.password = u'editpass'

    model.DBSession.add(editor)
    model.DBSession.flush()
    
    #...now time to add activities and then slot_rows 
    DaySchema = model.DaySchema()
    DaySchema.title = u'schema 2011'
    model.DBSession.add(DaySchema)
    
    ag_trapper = makeActivityGroup(u'Trapper')
    ag_spar = makeActivityGroup(u'Spår')
    ag_orientering  = makeActivityGroup(u'Orientering')
    ag_hantverk  = makeActivityGroup(u'Hantverk')
    ag_lokal = makeActivityGroup(u'Lokaler')
    ag_fladan = makeActivityGroup(u'Fladan')
    ag_vindskydd = makeActivityGroup(u'Vindskydd')
    ag_campfire = makeActivityGroup(u'Lägerbålsplatser')
    ag_mtrl = makeActivityGroup(u'Material och tält')
    ag_idrott = makeActivityGroup(u'Idrott')
    
    a_trapper = makeActivity(u'Trapper',  ag_trapper,  7,  bg_color='#fee', guides_per_slot=1)  
    a_klattring = makeActivity(u'Klättring',  ag_trapper,  0,  bg_color='#fee', guides_per_slot=2)  
    
    a_naturstigen = makeActivity(u'Naturstigen', ag_spar, 1, bg_color='#eef')
    a_bunkerspar = makeActivity(u'Bunkerspår', ag_spar,  1,  bg_color='#fff', default_booking_state=10)
    a_vildmarkspar = makeActivity(u'Vildmarksspåret', ag_spar, 1, bg_color='#eef')
    a_lilla_woodcraft = makeActivity(u'Lilla woodcraft',  ag_spar, 0,  bg_color='#efe', default_booking_state=10) 
    a_woodcraft = makeActivity(u'Woodcraft',  ag_spar,  0,  bg_color='#efe', default_booking_state=10)
    a_mangfald_ryggsack = makeActivity(u'Mångfaldsryggsäck',  ag_spar,  1,  bg_color='#efe')
    a_tradtranan = makeActivity(u'Trädtränan',  ag_spar,  0,  bg_color='#efe', default_booking_state=10)
    a_tracktrack = makeActivity(u'Träck Track',  ag_spar,  0,  bg_color='#efe', default_booking_state=10)
    a_kand_du_knopen = makeActivity(u'Kan du knopen', ag_spar,  0,  bg_color='#efe', default_booking_state=10)
    a_vatten_ryggsack = makeActivity(u'Vattenryggsäck', ag_spar,  1,  bg_color='#efe')
    a_skogs_ryggsack = makeActivity(u'Skogsryggsäck', ag_spar,  1,  bg_color='#efe')
    a_overlevnads_lada = makeActivity(u'Överlevnadslådan', ag_spar,  1,  bg_color='#efe')
    a_overlevnads_lada = makeActivity(u'Vildmarkskameran', ag_spar,  1,  bg_color='#eef')
    a_ovan_molnen = makeActivity(u'Ovan molnen', ag_spar,  0,  bg_color='#efe', default_booking_state=10)
    a_naturlek = makeActivity(u'Naturlek', ag_spar, 0,  bg_color='#efe')
    a_gosegame = makeActivity(u'Gose game', ag_spar,  1,  bg_color='#efe', default_booking_state=10)
    a_sammarbetsglantan = makeActivity(u'Sammarbetsgläntan', ag_spar,  2,  bg_color='#efe')
    
    a_skissorientering = makeActivity(u'Skissorientering', ag_orientering,  0,  bg_color='#efe', default_booking_state=10)
    a_punktorientering = makeActivity(u'Punktorientering', ag_orientering,  0,  bg_color='#efe', default_booking_state=10)
    a_linjeorientering = makeActivity(u'Linjeorientering', ag_orientering,  0,  bg_color='#efe', default_booking_state=10)
    a_stora_orienteringen = makeActivity(u'Stora orienteringen', ag_orientering,  0,  bg_color='#efe', default_booking_state=10)
    a_geo_cache = makeActivity(u'Geocache', ag_orientering,  1,  bg_color='#eef')
    a_fotoorientering = makeActivity(u'Fotoorientering', ag_orientering,  6,  bg_color='#efe', default_booking_state=10)
    a_fotobalja = makeActivity(u'Fotobalja', ag_spar,  2,  bg_color='#efe')

    a_hantverk = makeActivity(u'Hantverk',  ag_hantverk,  0,  bg_color='#fee', guides_per_slot=1) 
    a_knopladan = makeActivity(u'Knoplådan',  ag_hantverk,  0,  bg_color='#efe')  
    a_sjomaningsladan = makeActivity(u'Sjömaningslådan',  ag_hantverk,  0,  bg_color='#efe')  

    #...fladan
    a_lots = makeActivity(u'Lots', ag_fladan,  4, bg_color='#fee', guides_per_slot=1)  
    a_torekov = makeActivity(u'Torekov', ag_fladan, 4,  bg_color='#fee', guides_per_slot=1)  
    a_beata = makeActivity(u'Beata',  ag_fladan,  1, bg_color='#fee', guides_per_slot=2)  
    a_vaderojolle = makeActivity(u'Väderöjolle',  ag_fladan,  3, bg_color='#fee', guides_per_slot=0)  
    a_optimist = makeActivity(u'Optimist',  ag_fladan, 10, bg_color='#ffe')  
    a_canoe = makeActivity(u'Kanot',  ag_fladan, 20, bg_color='#ffe')  
    a_big_canoe = makeActivity(u'Storkanot',  ag_fladan, 1, bg_color='#ffe') 
    a_kust_woodcraft = makeActivity(u'Kust woodcraft', ag_fladan,  1,  bg_color='#efe')
    a_kanot_orientering = makeActivity(u'Kanotorientering', ag_fladan,  1,  bg_color='#efe')
     
    
    
    a_robuster = makeActivity(u'Rodbåt',  ag_fladan, 1, bg_color='#ffe')  
    a_flotte = makeActivity(u'Flottbygge',  ag_fladan, 1, bg_color='#ffe')
    
    #...idrott och rörelse
    a_hinderbana = makeActivity(u'Hinderbana',  ag_idrott, 0, bg_color='#fff')
    a_fotbollsplan_grustaget = makeActivity(u'Fotbollsplan, grustaget',  ag_idrott, 0, bg_color='#fff', default_booking_state=10)
    a_fotbollsplan_karret = makeActivity(u'Fotbollsplan, kärret',  ag_idrott, 0, bg_color='#fff', default_booking_state=10)
    a_volleybollplan_gras = makeActivity(u'Volleboll, gräs',  ag_idrott, 0, bg_color='#fff', default_booking_state=10)
    a_beach_volleyboll = makeActivity(u'Beachvolleyboll',  ag_idrott, 0, bg_color='#fff', default_booking_state=10)
    
    
    a_bastu_lilla = makeActivity(u'Lilla bastun',  ag_lokal, 8,  bg_color="#fff", default_booking_state=10)
    a_bastu_stora = makeActivity(u'Stora bastun',  ag_lokal, 30,  bg_color="#fff", default_booking_state=10)
    
    #...vindskydd och lägerbålsplatser
    a_vsk_lbp_norra = makeActivity(u'Vsk & Lbp Norra',  ag_vindskydd, 0,  bg_color="#fff", default_booking_state=10)
    a_vsk_lbp_slattskar = makeActivity(u'Vsk & Lbp Slåttskär',  ag_vindskydd, 0,  bg_color="#fff", default_booking_state=10)
    a_vsk_lbp_overangen = makeActivity(u'Vsk & Lbp Överängen',  ag_vindskydd, 0,  bg_color="#fff", default_booking_state=10)
    a_vindskydd_trapper = makeActivity(u'Vsk & Lbp Trapper',  ag_vindskydd, 0,  bg_color="#fff", default_booking_state=10)
    a_vinskydd_ljusklubben = makeActivity(u'Vsk & Lbp Ljusklubben',  ag_vindskydd, 0,  bg_color="#fff", default_booking_state=10)
    a_vindskydd_garpen = makeActivity(u'Vsk & Lbp Garpen',  ag_vindskydd, 0,  bg_color="#fff", default_booking_state=10)
    
    a_lbp_betongbryggan = makeActivity(u'Lbp Betongbryggan',  ag_campfire, 0,  bg_color="#fff", default_booking_state=10)
    a_lbp_bastun = makeActivity(u'Lbp Bastun',  ag_campfire, 0,  bg_color="#fff", default_booking_state=10)
    a_lbp_ravtangen = makeActivity(u'Lbp Rävtången',  ag_campfire, 0,  bg_color="#fff", default_booking_state=10)
    a_lbp_ostra_gvb = makeActivity(u'Lbp Östra GVB',  ag_campfire, 0,  bg_color="#fff", default_booking_state=10)
    a_lbp_fladan = makeActivity(u'Lbp Fladan',  ag_campfire, 0,  bg_color="#fff", default_booking_state=10)
    a_lbp_matladan = makeActivity(u'Lbp Matlådan',  ag_campfire, 0,  bg_color="#fff", default_booking_state=10)
    a_lbp_lillgarn = makeActivity(u'Lbp Lillgårn',  ag_campfire, 0,  bg_color="#fff", default_booking_state=10)
    a_lbp_stora = makeActivity(u'Lbp Stora',  ag_campfire, 0,  bg_color="#fff", default_booking_state=10)
    a_lbp_programangen = makeActivity(u'Lbp Programängen',  ag_campfire, 0,  bg_color="#fff", default_booking_state=10)
    a_lbp_naturstigen = makeActivity(u'Lbp Naturstigen',  ag_campfire, 0,  bg_color="#fff", default_booking_state=10)
    a_lbp_sang_o_mysik = makeActivity(u'Lbp Sång och mysik',  ag_campfire, 0,  bg_color="#fff", default_booking_state=10)
    
    #...lokaler
    a_cirkus_runda_salen = makeActivity(u'Cirkus runda salen',  ag_lokal, 0,  bg_color="#fff")
    a_cirkus_konf_rummet = makeActivity(u'Cirkus konf-rummet',  ag_lokal, 0,  bg_color="#fff")
    a_cirkus_grupp_rummet = makeActivity(u'Cirkus grupprummet',  ag_lokal, 0,  bg_color="#fff")
    a_kapellet = makeActivity(u'Kapellet',  ag_lokal, 0,  bg_color="#fff")
    a_eko = makeActivity(u'Ekohuset',  ag_lokal, 0,  bg_color="#fff")
    a_lillgarn_ovre = makeActivity(u'Lillgårn övre', ag_lokal, 0, bg_color="#fff")
    a_ladan = makeActivity(u'Ladan',  ag_lokal, 0,  bg_color="#fff")
    a_bathuset = makeActivity(u'Båthuset',  ag_lokal, 0, bg_color="#fff")
    
    a_magasinet = makeActivity(u'Magasinet', ag_lokal, 0, bg_color="#ffe")
    a_grillkata = makeActivity(u'Grillkåtan',  ag_lokal, 0, bg_color="#fff")
    
    #...material och tält
    a_vindskydd = makeActivity(u'Vindskydd',  ag_mtrl, 0,  bg_color="#fff")
    a_talt_tentipi = makeActivity(u'Tentipi',  ag_mtrl, 10,  bg_color="#fff")
    a_talt_gillwell = makeActivity(u'Gillwelltält',  ag_mtrl, 0,  bg_color="#fff")
    a_kata = makeActivity(u'Jättekåtan',  ag_mtrl, 0,  bg_color="#fff")
    a_alu_lada = makeActivity(u'ALU-låda',  ag_mtrl, 7,  bg_color="#fff")
    a_mtrl = makeActivity(u'Material, övrigt',  ag_mtrl, 0,  bg_color="#fff")
    a_pionjar = makeActivity(u'Pionjärarbeten',  ag_mtrl, 0,  bg_color="#fff")
    a_ljud = makeActivity(u'Ljudutrustning',  ag_mtrl, 0,  bg_color="#fff")
    
    

    #...create three slot_rows with three slot_row_positions in each
    all_slot_rows = list()
    
    for aa in [a_trapper, a_klattring,  a_naturstigen, a_bunkerspar, a_vildmarkspar, a_lilla_woodcraft, a_woodcraft, a_mangfald_ryggsack, a_tradtranan, a_tracktrack, a_kand_du_knopen, a_vatten_ryggsack, a_skogs_ryggsack, a_overlevnads_lada,  a_ovan_molnen, a_naturlek, a_gosegame, a_sammarbetsglantan]:
        all_slot_rows += makeSlotRows(1,  aa)

    
    for aa in [a_skissorientering, a_punktorientering, a_linjeorientering, a_stora_orienteringen, a_geo_cache, a_fotoorientering, a_fotobalja, a_hantverk, a_knopladan, a_sjomaningsladan]:
        all_slot_rows += makeSlotRows(1,  aa)
    
    
    #...fladan
    for aa in [a_lots, a_torekov, a_beata, a_vaderojolle, a_optimist, a_canoe, a_big_canoe,  a_kust_woodcraft, a_kanot_orientering, a_robuster, a_flotte ]:
        all_slot_rows += makeSlotRows(1,  aa)
    
    
    #...idrott och rörelse
    for aa in [a_hinderbana, a_fotbollsplan_grustaget, a_fotbollsplan_karret, a_volleybollplan_gras, a_beach_volleyboll, a_bastu_lilla, a_bastu_stora]:
        all_slot_rows += makeSlotRows(1,  aa)
    
    #...vindskydd och lägerbålsplatser
    for aa in [a_vsk_lbp_norra, a_vsk_lbp_slattskar, a_vsk_lbp_overangen, a_vindskydd_trapper, a_vinskydd_ljusklubben, a_vindskydd_garpen]:
        all_slot_rows += makeSlotRows(1,  aa)
    
    for aa in [a_lbp_betongbryggan, a_lbp_bastun, a_lbp_ravtangen, a_lbp_ostra_gvb, a_lbp_fladan, a_lbp_matladan, a_lbp_lillgarn, a_lbp_stora, a_lbp_programangen, a_lbp_naturstigen, a_lbp_sang_o_mysik]:
        all_slot_rows += makeSlotRows(1,  aa)
    
    #...lokaler
    for aa in [a_cirkus_runda_salen, a_cirkus_konf_rummet, a_cirkus_grupp_rummet, a_kapellet, a_eko, a_lillgarn_ovre, a_ladan, a_bathuset, a_magasinet, a_grillkata]:
        all_slot_rows += makeSlotRows(1,  aa)
    
    #...material och tält
    for aa in [a_vindskydd, a_talt_tentipi, a_talt_gillwell, a_kata, a_alu_lada, a_mtrl, a_pionjar, a_ljud]:
        all_slot_rows += makeSlotRows(1,  aa)
    
    
    

    L1 = [(9, 12), (13, 16), (17, 20),  (21, 23)]
    for tmp_slot_row in all_slot_rows:
        for fromt,  tot in L1:
            SlotRowPosition = model.SlotRowPosition()
            SlotRowPosition.time_from = datetime.time(fromt)
            SlotRowPosition.time_to = datetime.time(tot)
            SlotRowPosition.duration = tot-fromt
            SlotRowPosition.slot_row = tmp_slot_row
    
    if True:
        # period I  2011 starts 11 june to 17 july

        # period II 2011 starts 18 july to 14 august 

        for i in range(30-11+1):
            d = datetime.date(2011, 6, i+11)
            make_booking_day(d)
       
        for i in range(31):
            d = datetime.date(2011, 7, i+1)
            make_booking_day(d)

        for i in range(14):
            d = datetime.date(2011, 8, i+1)
            make_booking_day(d)
       

       
    
    
    n_a_visiting_group = model.VisitingGroup()
    n_a_visiting_group.name = 'N/A'
    n_a_visiting_group.fromdate = datetime.datetime(2010, 01, 01)
    n_a_visiting_group.todate = datetime.datetime(2100, 01, 01)
    
    model.DBSession.add(n_a_visiting_group)
    
    transaction.commit()
    print "Successfully setup"
