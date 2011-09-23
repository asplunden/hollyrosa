"""
Copyright 2010, 2011 Martin Eliasson

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


import zipfile, shutil,  StringIO
from xml.etree.ElementTree import ElementTree, fromstring, tostring,  Element


class OOorgDoc(object):
    def __init__(self, path,  dont_close=False):
        """
        An OpenOffice spreadsheet is a zip-file where all the contents can be found in the file content.xml
        """
        self.path = path
        z = zipfile.ZipFile(path)
        data = z.read('content.xml')
        if not dont_close:
            z.close()
        else:
            self.z = z
            
        self.content = data
        
    def copyAndSetNewContent(self, new_path, new_content,  dont_close=False):
        try:
            shutil.copy(self.path, new_path)
            z = zipfile.ZipFile(new_path,  'a')
        except TypeError:
            namelist = self.z.namelist()
            z = zipfile.ZipFile(new_path, 'w')
            for n in namelist:
                t = self.z.read(n)
                z.writestr(n,  t)
        
        #...I hope we can make new_path a StringIO buffer so we dont have to use the file system at all
        #   It would be great, because then we could make a zip file of zip files - so we can return an archive of diplomas
        z.writestr('content.xml', new_content)
        if not dont_close:
            z.close()

    def close(self):
        self.z.close()
        
class OOorgSpreadsheet(OOorgDoc):
    def __init__(self, path,  dont_close=False):
        OOorgDoc.__init__(self, path,  dont_close=dont_close)
        
        
    def computeMappedCellContents(self):
        """
        Compute a list with dictionaries, each dictionary mapping first row cell (column names) to cell content in the row it represents.
        
        Returns the computed list, bot also sets it in this instance
        """
        
        cell_contents = []
            
        tree = fromstring(self.content)
        body = tree.findall('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}body')[0]
        spreadsheet = body.find('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}spreadsheet')
        table =  spreadsheet.find('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table')
        
        #...iterate over all rows (in the first of all spreadsheets)
        table_rows = table.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row')
        
        #...figure out column names and corresponding index
        row0 = table_rows[0]
        row0_label_to_index_mapping = {}
        i = 0
        for cell in row0.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell'):
            n= cell.find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p').text
            row0_label_to_index_mapping[n] = i
            i += 1
    
        #...using column index, build dictionaries for each row
        for row in table_rows[1:]:
            cells = row.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell')
            
            row_contents = {}
        
            for cell_column_name,cell_column_index in row0_label_to_index_mapping.items():
                if len(cells) >cell_column_index:
                    p_tag = cells[cell_column_index].find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p')
                    if p_tag != None:
                        row_contents[cell_column_name] = p_tag.text
                else:
                    row_contents[cell_column_name] = ""
                    
                i+=1
            cell_contents.append(row_contents)
        
        self.cell_contents = cell_contents
        return cell_contents
        
    def setCol0NameToRowMap(self,  booking_day_mapping):
        """
        Merge data from hollyrosa into daily schema.
        
        For each row, get col0 name, 
          find col 0 in given mapping 
          for each row in col0 (first three?) set cell 1 2 and 3 (zero based)
          
        """
        
            
        tree = fromstring(self.content)
        body = tree.findall('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}body')[0]
        spreadsheet = body.find('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}spreadsheet')
        table =  spreadsheet.find('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table')
        
        #...iterate over all rows (in the first of all spreadsheets)
        table_rows = table.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row')
        
        #...figure out column names and corresponding index
        for tmp_row in table_rows:
            tmp_cell_index = 0
            data_index = 0
            is_booking_row = False
            
            for tmp_cell in tmp_row.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell'):
                if 0 == tmp_cell_index:
                   tmp_cell_index += 1 
                elif 1== tmp_cell_index:
                    tmp_cell_p = tmp_cell.find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p')
                    if None != tmp_cell_p:
                        #print 'cell 1',  tmp_cell_p.text
                        if booking_day_mapping.has_key(tmp_cell_p.text):
                            tmp_data = booking_day_mapping[tmp_cell_p.text]
                            is_booking_row = True
                    else:
                        #print 'empty cell, continuing'
                        break
                    tmp_cell_index += 1
                    
                else:
                    if is_booking_row:
                        tmp_cell_p = tmp_cell.find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p')
                        if data_index < len(tmp_data):
                            if None == tmp_cell_p:
                                tmp_cell_p = Element('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p')
                                tmp_cell.append(tmp_cell_p)
                             
                            #print 'setting content at data index=',  data_index,  tmp_cell_index
                            tmp_cell_p.text = tmp_data[data_index]
                        
                            #...reset column repeater, it creates big pain otherwise from our template
                            #tmp_cell.attrib['{ns1}number-columns-repeated'] = "1"
                            
                            data_index += 1
                            
                        tmp_cell_index += 1
                
        return tostring(tree)
        
        
    def filterMappedCellContents(self, include_headers):
        """
            Given a list of column headers, takes the cell contents list in this class and returns a copy of it, but only with those headers listed in include_headers
        """
        result = []
        for row in self.cell_contents:
            n = {}
            for k,v in row.items():
                if k in include_headers:
                    n[k] = v
            result.append(n)
        return result
    
    def parseNmn(self, template):
        #cell_contents = []
        result = {}
        
        
        tree = fromstring(self.content)
        body = tree.findall('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}body')[0]
        spreadsheet = body.find('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}spreadsheet')
        
        #print spreadsheet
        #print spreadsheet.getchildren()
        
        tables =  spreadsheet.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table')
        
        for table in tables:
            #...iterate over all rows (in the first of all spreadsheets)
            table_rows = table.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row')
            
            #...figure out column names and corresponding index
            row0 = table_rows[0]
            i = 0
            cells = row0.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell')
            
            if len(cells) <= 1:
                return result
                
            nmn = cells[1].find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p').text
            #print 'Nmn:', nmn    
            tmp_result = []
            result[nmn] = tmp_result
        
            #...using column index, build dictionaries for each row
            for row in table_rows[2:]:
                cells = row.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell')
                
                #print cells[0].find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p').text,
                #print cells[1].find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p').text,
                #print cells[2].find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p').text
                
                tmp_result.append((cells[0].find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p').text, cells[1].find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p').text, cells[2].find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p').text))
            
        return result

    
class OOorgText(OOorgDoc):
    def __init__(self, path,  dont_close=False):
        OOorgDoc.__init__(self, path,  dont_close=dont_close)
        
        
    def diveIntoDoc(self, nmn, terms):
        tree = fromstring(self.content)
        body = tree.findall('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}body')[0]
        text_node = body.find('{urn:oasis:names:tc:opendocument:xmlns:office:1.0}text')
        table_nodes = text_node.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table')
        
        #...we want the table node named "Years"
        
        for tn in table_nodes:
            #print tn
            if tn.attrib['{urn:oasis:names:tc:opendocument:xmlns:table:1.0}style-name'] == 'name':
                name_table_node = tn
        
         
        
        table_rows = name_table_node.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row')
        cells = table_rows[0].findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell')
        cells[0].find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p').text = nmn
        
        for tn in table_nodes:
            if tn.attrib['{urn:oasis:names:tc:opendocument:xmlns:table:1.0}style-name'] == 'years':
                terms_table_node = tn
        
        
        print terms_table_node
        
        #...iterate over the rows
        table_rows = terms_table_node.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-row')
        row_num = 0
        for row in table_rows[1:11]: #...hard coded maximum number of rows=11
            if row_num < len(terms):
                cells = row.findall('{urn:oasis:names:tc:opendocument:xmlns:table:1.0}table-cell')
            
                #abc = ['a','b','c','d']
                i = 0 # use itertools instead
                for cell in cells:
                    cell.find('{urn:oasis:names:tc:opendocument:xmlns:text:1.0}p').text = terms[row_num][i] #abc[i]
                    i+= 1
                row_num += 1
                
        self.new_content = tostring(tree)
        
        
        #...the real cool thing would be if we could parse a ods and given the sheets - one for each pn - we could generate one such odt if it didnt already exist.
        #
        #...a related question is, can we use this for badger? What would it look like? 
            


def make(template,  booking_day_mapping=None):
    if booking_day_mapping==None:
        booking_day_mapping = {}
        booking_day_mapping['Trapper 1'] = ['hej',  'hopp', 'faderullan']
        booking_day_mapping['Trapper 2'] = ['',  'tidig', '']
        booking_day_mapping['Trapper 3'] = ['morgon',  '', '']
        booking_day_mapping['Trapper 4'] = ['',  '', 'sen']

    
    ODS = OOorgSpreadsheet(template,  dont_close=True)
    new_content = ODS.setCol0NameToRowMap(booking_day_mapping)
    
    out_file = StringIO.StringIO()
    ODS.copyAndSetNewContent(out_file, new_content)
    return out_file.getvalue()
    
    
if __name__ == '__main__':
    
    booking_day_mapping = {}
    
    booking_day_mapping['Trapper 1'] = ['hej',  'hopp', 'faderullan']
    booking_day_mapping['Trapper 2'] = ['',  'tidig', '']
    booking_day_mapping['Trapper 3'] = ['morgon',  '', '']
    booking_day_mapping['Trapper 4'] = ['',  '', 'sen']
    
    ODS = OOorgSpreadsheet('/home/marel069/programdayn.ods')
    new_content = ODS.setCol0NameToRowMap(booking_day_mapping)
    #print new_content
    #ODT = OOorgText('diplom_mall.odt')
    #for nmn, terms in nmns.items():
    #    ODT.diveIntoDoc(nmn, terms)
    #    ODT.copyAndSetNewContent(nmn+'.odt', ODT.new_content)
    ODS.copyAndSetNewContent('/home/marel069/new_booking_day.ods', new_content)
    
