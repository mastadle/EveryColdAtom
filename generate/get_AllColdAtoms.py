import requests
from bs4 import BeautifulSoup
import json
from time import sleep

from simplekml import coordinates

class GroupClass:
    defaults = {}
    defaults['name'] = ''
    defaults['webpage'] = ''
    defaults['institution'] = ''
    defaults['country'] = ''
    defaults['address'] = ''
    defaults['lat'] = 0
    defaults['long'] = 0
    defaults['exp_theor'] = ''
    defaults['fields'] = ''
    defaults['people'] = ''
    defaults['atom'] = ''
    defaults['comment'] = ''
    # May not need defaults, may be global. Yes! Global!

    def __init__(self):
        self.name = ''
        self.webpage = ''
        self.institution = ''
        self.country = ''
        self.address = ''
        self.lat = 0.0
        self.long = 0.0
        self.exp_theor = ''
        self.fields = ''
        self.people = '' # having people as a list was too problematic.
        self.atom = ''
        self.comment = ''

    def join(self, other, priority='self'):
        """
        Copies the attributes from other to self.
        Skips empty attributes from other.
        Skips attributes defined in both if priority == self.
        Never tested.
        """
        for field in self.__dict__.keys():
            if (other.__dict__[field] != GroupClass.defaults[field]):
                if (priority == 'other' or
                    self.__dict__[field] == GroupClass.defaults[field]):
                    self.__dict__[field] = other.__dict__[field]
            

    def get_from_utoronto(self, url, replace_existing=True):
        """
        Works for subpages on https://ucan.physics.utoronto.ca/Groups
        such as https://ucan.physics.utoronto.ca/
            /Groups/group.2015-04-09.8798812973/view
        """
        r = requests.get(url)

        soup = BeautifulSoup(r.text, 'html.parser')

        thediv = soup.find_all("h1", {"class": "group"})[0].parent
        self.name = ' '.join(thediv.find_all('h1')[0].text.split())
        
        institution = thediv.find_all("span", {"class": "institution"})
        if len(institution) == 0:
            self.institution = GroupClass.defaults['institution']
        else:
            self.institution = institution[0].text.strip().replace(';', ' ')

        country = thediv.find_all("span", {"class": "country"})
        if len(country) == 0:
            self.country = GroupClass.defaults['country']
        else:
            self.country = country[0].text.strip()

        exp_theor = thediv.find_all("span", {"class": "research note"})
        if len(exp_theor) == 0:
            self.exp_theor = GroupClass.defaults['exp_theor']
        else:
            self.exp_theor = exp_theor[0].text.strip()

        fields = thediv.find_all("div", {"class": "description"})
        if len(fields) == 0:
            self.fields = GroupClass.defaults['fields']
        else:
            self.fields = fields[0].text.strip().replace(';', ',,').replace('\n', '        ').replace('\r', '')
            # Replacements are maybe not necessary, but needed for backwards compatibility.

        people = thediv.find_all("span", {"class": "people"})
        if len(people) == 0:
            self.people = GroupClass.defaults['people']
        else:
            self.people = people[0].text.strip().replace(';', ',,').replace('\n', '        ')
            # Replacements are maybe not necessary, but needed for backwards compatibility.

        self.webpage = thediv.find('div', {'class': "group_homepage"}).a['href']
        # Maybe I should be using find instead of find_all the whole time! Too late now.

        self.atom = ''

        if 0:
            print(self.name, self.institution, self.country, self.exp_theor, sep='\t|\t')
            print('\t', self.fields, self.people, sep='\t|\t')
            print(self.webpage)
            print()
        
        return thediv

    def get_from_utoronto_new(self, url, replace_existing=True):
        """
        Works newer URL, such as view-source:https://ucan.physics.utoronto.ca/research-groups/jegliczupanic/
        """
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        thediv = soup.find_all("article")[0]
        
        self.name = ' '.join(thediv.find_all('h1')[0].text.split())

        institution = "-".join(thediv.section.div.div.text.strip(
            ).replace(';', ' ').split("Institution")[1].split('-')[:-1])
        # Splitting by "-" is incorrect. Some names have - in them. Fixed
        self.institution = " ".join(institution.split())

        country = thediv.find_all("span", {"class": "has-tip"})
        if len(country) == 0:
            self.country = GroupClass.defaults['country']
        else:
            self.country = country[0]['title'].strip()

        #exp_theor = thediv.find_all("span", {"class": "research note"})
        #self.exp_theor = thediv.text.split("Research")[-1].split()[0]
        self.exp_theor = thediv.find_all("div", {"class": "callout"})[0].find_all(
            "div")[2].text.split("Research")[1].split()[0].strip()
        # Todo convert to old format Exp, Exp/Theory, Theory, insted of Experimen, Experiment/Theory, Theory
        
        #fields = thediv.find_all("div", {"class": "rich-text"})
        self.fields = GroupClass.defaults['fields']
        self.fields = thediv.text
        if "Permanent Researchers and Staff" in self.fields:
            self.fields = self.fields.split("Permanent Researchers and Staff")[0]
        self.fields = self.fields.split("Research")[1].lstrip()
        fields_newline = self.fields.find('\n')
        self.fields = self.fields[fields_newline:].strip().replace(';', ',,').replace('\n', '        ')
        #    # Replacements are maybe not necessary, but needed for backwards compatibility.


        people = thediv.text.split("Permanent Researchers and Staff")
        if len(people) == 1:
            self.people = GroupClass.defaults['people']
        else:
            self.people = people[1].strip().replace(';', ',,').replace('\n', '        ')
            # Replacements are maybe not necessary, but needed for backwards compatibility.

        self.webpage = thediv.find_all("div", {"class": "callout"})[0].find_all(
            "div")[1].a['href']
        # Maybe I should be using find instead of find_all the whole time! Too late now.

        self.atom = ''

        if 1:
            print(self.name, self.institution, self.country, self.exp_theor, sep='\t|\t')
            print('\t', self.fields, self.people, sep='\t|\t')
            print(self.webpage)
            print()
        
        return thediv

    def csv(self): # Should probably use built-in csv writer.
        """ Export csv line """
        all_vars = [self.name, self.webpage, self.institution,
            self.country, self.address, self.lat, self.long,
            self.exp_theor, self.fields,
            self.people, self.atom, self.comment]
        
        all_vars = list(map(str, all_vars))
        return ';'.join(all_vars) + '\n'

    def csv_header(self):
        """ Export csv header line """
        all_vars = ['name', 'webpage', 'institution',
            'country', 'address', 'lat', 'long',
            'exp_theor', 'fields',
            'people', 'atom', 'comment']
        return ';'.join(all_vars) + '\n'

    def get_from_csv(self, line, sep=';'):
        line = line.strip('\n')
        if len(line.split(sep)) != 12:
            print(line.split(sep))
        try:
            (self.name, self.webpage, self.institution,
                self.country, self.address, self.lat,
                self.long, self.exp_theor, self.fields,
                self.people, self.atom, self.comment) = line.split(sep)
        except Exception as e:
            print(e)
            print("At line", line)
            raise
        self.lat = float(self.lat)
        self.long = float(self.long)

    def get_from_csv2(self, line):
        """ Line is a list from csv module. Doesn't really work. """
        print(len(line))
        (self.name, self.webpage, self.institution,
            self.country, self.address, self.lat,
            self.long, self.exp_theor, self.fields,
            self.people, self.atom, self.comment) = line
        self.lat = float(self.lat)
        self.long = float(self.long)


    def __eq__(self, other):
        """ Never tested. """
        all_vars = [self.name, self.webpage, self.institution,
            self.country, self.address, self.lat, self.long,
            self.exp_theor, self.fields,
            self.people, self.atom, self.comment]
        other_vars = [other.name, other.webpage, other.institution,
            other.country, other.address, other.lat, other.long,
            other.exp_theor, other.fields,
            other.people, self.atom, other.comment]
        for i in range(len(all_vars)):
            if all_vars[i] != other_vars[i]:
                return False
        return True

    def geocode(self, gmaps, verbose=True):
        """ Get location from address using Google Maps API. """
        querry = self.institution + ', ' + self.country
        if verbose: print('Querry:', querry)

        geocode_result = gmaps.geocode(querry)
        if len(geocode_result) == 0:
            print('No results!')
            return
        if verbose:
            print(len(geocode_result))
            print(geocode_result[0]['geometry']['location'])
        self.lat = geocode_result[0]['geometry']['location']['lat']
        self.long = geocode_result[0]['geometry']['location']['lng']        

    def to_marker(self, i):
        """
        Converts self to javascript marker object. Obsolete. Now use json_data()
        """
        ret = ""
        ret += 'var marker{:} = new L.Marker.SVGMarker([{:}, {:}],'.format(
            i, self.lat, self.long)
        ret += ' { iconOptions: { color: "rgb(0,0,100)" }});\n'
        ret += 'marker{:}.desc = \'<a href="{webpage}"><b>{name}</b></a><br />{institution}, {country}\';\n'.format(
            i, name=self.name.replace('\'', '\\\''), webpage=self.webpage.replace('\'', '\\\''),
            institution=self.institution.replace('\'', '\\\''), country=self.country)
        ret += 'mymap.addLayer(marker{:});\n'.format(i)
        ret += 'oms.addMarker(marker{:});\n'.format(i)
        ret += "marker{i}.on('mouseover', function(e)".format(i=i)
        ret += "{" + """
    popup.setContent(marker{i}.desc);
    popup.setLatLng(marker{i}.getLatLng());
    mymap.openPopup(popup);
""".format(i=i)
        ret += "});"
        ret += "    marker{i}.on('mouseout', function(e)".format(i=i)
        ret += """{ mymap.closePopup(); });
"""
        return ret

    def json_data(self, index):
        """ Converts everything into a dict that is exported as json and used to create
        all markers on the map
        """
        ret = dict()
        ret['lat'] = self.lat
        ret['long'] = self.long
        ret['desc'] = '<a href="{webpage}"><b>{name}</b></a><br />{institution}, {country}<br />'.format(
            i, name=self.name.replace('\'', '\\\''), webpage=self.webpage.replace('\'', '\\\''),
            institution=self.institution.replace('\'', '\\\''), country=self.country)
        ret['desc'] += '<b>Research:</b> {:}<br />{:}<br />'.format(self.exp_theor, self.fields.replace(',,', ';'))
        ret['desc'] += '<b>Atoms:</b> {:}<br />'.format(self.atom)
        ret['desc'] += '<b>Permanent researchers and staff:</b> {:}<br />'.format(self.people.replace(',,', ';'))
        ret['desc'] += '<b>Editors note:</b> {:}<br />'.format(self.comment)
        ret['atom'] = self.atom
        ret['exp_theor'] = self.exp_theor
        ret['index'] = index
        return ret

    def html_header_line(self):
        """ Exports the header line in the html table on the webpage. """
        ret = """<div class="tg-wrap tg-wrap-hidden" id="tg-wrap-id"><table id="tg-tg00" class="tg">
<tr>
    <th class="tg-tg01">Group</th>
    <th class="tg-tg02">Institution</th>
    <th class="tg-tg03">Country</th>
    <th class="tg-tg04">Lat</th>
    <th class="tg-tg05">Long</th>
    <th class="tg-tg06">Exp/Theory</th>
    <th class="tg-tg09">Atoms</th>
    <th class="tg-tg07">Description</th>
    <th class="tg-tg08">People</th>
    <th class="tg-tg10">Comment</th>
    <th class="tg-tg11">Index</th>
  </tr>
"""
        return ret

    def html_ending_line(self):
        """ Exports the ending line in the html table on the webpage. """
        ret = """</table></div>"""
        return ret

    
    def html_line(self, index):
        """ Exports a line in the html table on the webpage. """
        ret = ''
        ret = """  <tr>
    <td class="tg-tg{0:02d}"><a href="{webpage}"><b>{name}</b></a></td>
    <td class="tg-tg{1:02d}">{institution}</td>
    <td class="tg-tg{2:02d}">{country}</td>
    <td class="tg-tg{3:02d}">{lat}</td>
    <td class="tg-tg{4:02d}">{long}</td>
    <td class="tg-tg{5:02d}">{exp_theor}</td>
    <td class="tg-tg{8:02d}">{atoms}</td>
    <td class="tg-tg{6:02d}"><div class="makescrollable">{desc}</div></td>
    <td class="tg-tg{7:02d}"><div class="makescrollable">{people}</div></td>
    <td class="tg-tg{9:02d}">{comment}</td>
    <td class="tg-tg{10:02d}">{index}</td>

  </tr>
""".format(*list(range(1,12)),
           name=self.name, webpage=self.webpage,
           institution=self.institution,
           country=self.country,
           lat=self.lat,
           long=self.long,
           exp_theor=self.exp_theor,
           desc=self.fields.replace(',,', ';'),
           atoms=self.atom,
           people=self.people.replace(',,', ';'),
           comment=self.comment,
           index=index)
        return ret

    def compare(self, other, which): # TODO return all differences.
        for w in which:
            if w == 'name':
                if self.name != other.name: return False, 'name'
            if w == 'webpage':
                if self.webpage != other.webpage: return False, 'webpage'
            if w == 'institution':
                if self.institution != other.institution: return False, 'institution'
            if w == 'country':
                if self.country != other.country: return False, 'country'
            if w == 'lat':
                if self.lat != other.lat: return False, 'lat'
            if w == 'long':
                if self.long != other.long: return False, 'long'
            if w == 'exp_theor':
                if self.exp_theor != other.exp_theor: return False, 'exp_theor'
            if w == 'desc':
                if (self.fields == 'y' or self.fields == 't') and other.fields == '':
                    pass
                elif self.fields != other.fields: return False, 'desc/fields'
            if w == 'atoms':
                if self.atoms != other.atoms: return False, 'atoms'
            if w == 'people':
                if self.people != other.people: return False, 'people'
            if w == 'comment':
                if self.comment != other.comment: return False, 'comment'
            if w == 'index':
                if self.index != other.index: return False, 'index'

        return True, 'True'
    
def diff(newfile, oldfile, sep1, sep2):
    # tab '	'
    data1 = []
    data2 = []
    with open(newfile, 'r', encoding="utf8") as f:
        f.readline() 
        for i, line in enumerate(f):
            a = GroupClass()
            a.get_from_csv(line, sep=sep1)
            data1.append(a)
    print("New file processed")
    with open(oldfile, 'r', encoding="utf8") as f:
        f.readline()
        for i, line in enumerate(f):
            a = GroupClass()
            a.get_from_csv(line, sep=sep2)
            data2.append(a)
    print(len(data1), len(data2), "<- len data1 len data2")
    groups1 = set([i.name for i in data1])
    groups2 = set([i.name for i in data2])
    print("Added groups", sorted(groups1-groups2))
    print("Removed groups", sorted(groups2-groups1))

    for i in range(min(len(data1), len(data2))):
        if data1[i].name != data2[i].name:
            print("Group name mismatch", data1[i].name, data2[i].name)
            continue
        #else: In Sept 2021, the order changer on UCAN. This was used to fix it.
        #    print("Group name match", data1[i].name, data2[i].name)
        #    continue
        cmp_val, cmp_details = data1[i].compare(data2[i], [
            'name',
            'webpage',
            'country', # USA is different
            'institution',
            #'desc', # a lot of desc seem to have diffapeard from webpage.
            'people', # a lot of people seem to have diffapeard from webpage.
            #'exp_theor',
            ])
        if cmp_val:
            pass
        else:
            print("Diff in", cmp_details)
            if cmp_details == 'desc/fields':
                print("New", data1[i].name, data1[i].fields)
                print("Old", data2[i].name, data2[i].fields)
            elif cmp_details == 'people':
                print("New", data1[i].name, data2[i].people)
                print("Old", data2[i].name, data2[i].people)
            else:
                print("New", data1[i].csv())
                print("Old", data2[i].csv())
            #print("New", data1[i].name, data1[i].country)
            #print("Old", data2[i].name, data2[i].country)
            print('----------')
            #sleep(1)
            # Compare all of them to catch new mistakes!!!
            # TODO Finish comparing.
    return data1, data2

def geocode_one(name):
    import googlemaps
    with open('gmapsAPIkey.txt', 'r') as f:
        gmapsAPIkey = f.read().strip()
    gmaps = googlemaps.Client(key=gmapsAPIkey)

    querry = name
    print('Querry:', querry)

    geocode_result = gmaps.geocode(querry)
    if len(geocode_result) == 0:
        print('No results!')
        return
    if 1:
        print(len(geocode_result))
        print(geocode_result[0]['geometry']['location'])
    lat = geocode_result[0]['geometry']['location']['lat']
    long = geocode_result[0]['geometry']['location']['lng']
    return lat, long

        

######################################################################
"""
I'll have a base database. And manual corrections.
And automatic change detection, which I'll manually
add to production. Hopefully.
"""
######################################################################

if 0: # OBSOLETE load all from ucan OBSOLETE
    # obsolete because of the webpage change.
    print("Obsolete!!!")
    base_url = 'https://ucan.physics.utoronto.ca/Groups'
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    thetable = soup.find_all("table", {"class": "listing"})
    if len(thetable) != 1:
        print('The len of the table != 1', len(thetable))
    thetable = thetable[0].tbody

    a = GroupClass()

    count = 0
    with open('ucan_utoronto_database_test20180330.csv', 'w', encoding="utf-8") as f:
        # you must open the file in notepad++ and "Convert to UTF-8" so that special characters really work.
        f.write(a.csv_header())
        for row in thetable.children:
            if (str(row).strip() == ''): continue
            print(count, row.td.a['href'])
            count += 1
            a = GroupClass() # pretty sure this needs to be reinitialized.
            b = a.get_from_utoronto(row.td.a['href'])
            f.write(a.csv())

    url = 'https://ucan.physics.utoronto.ca/Groups/group.2005-07-11.4942545460/view'
    #b = a.get_from_utoronto(url)

new_filename = 'ucan_utoronto_database_test20240410.csv'
print("New filename", new_filename)
# update this filename to the last version of the file
if 0: # load all from ucan. RUN THIS FIRST
    do_geocode = True
    if do_geocode:
        import googlemaps
        with open('gmapsAPIkey.txt', 'r') as f:
            gmapsAPIkey = f.read().strip()
        gmaps = googlemaps.Client(key=gmapsAPIkey)
    base_url = 'https://ucan.physics.utoronto.ca/research-groups/'
    base_url1 = 'https://ucan.physics.utoronto.ca'
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    thetable = soup.find_all("table", {"id": "research_groups_table"})
    if len(thetable) != 1:
        print('The len of the table != 1', len(thetable))
    thetable = thetable[0].tbody

    a = GroupClass()

    count = 0
    with open(new_filename, 'w', encoding="utf-8") as f:
        # you must open the file in notepad++ and "Convert to UTF-8" so that special characters really work.
        # Clarify next time!
        f.write(a.csv_header())
        for row in thetable.children:
            if (str(row).strip() == ''): continue
            print(count, row.td.a['href'])
            count += 1
            #if count != 4: continue
            a = GroupClass() # pretty sure this needs to be reinitialized.
            b = a.get_from_utoronto_new(base_url1 + row.td.a['href'])
            if do_geocode:
                a.geocode(gmaps)
            f.write(a.csv())
            #print(1/0)
            # sleep(5)

if 1:
    # Calculate diff
    print("Calculating diff")
    data1, data2 = diff(new_filename,
         'ucan_utoronto_database_production_with_geocode-edited2tabs.csv',
         ';', '	')
    # To update the production file, open both
    # ucan_utoronto_database_production_with_geocode-edited2.xlsx
    # and new_filename in excel, edit the differences in edited2.xlsx.
    # Then copy paste ucan_utoronto_database_production_with_geocode-edited2.xlsx
    # to ucan_utoronto_database_production_with_geocode-edited2tabs.csv
    


if 0: #geocode
    import googlemaps
    with open('gmapsAPIkey.txt', 'r') as f:
        gmapsAPIkey = f.read().strip()
    gmaps = googlemaps.Client(key=gmapsAPIkey)
    # Geocoding an address
    with open('ucan_utoronto_database.csv', 'r') as in_file:
        with open('ucan_utoronto_database_production_with_geocode.csv', 'w') as out_file:
            in_file.readline()
            a = GroupClass()
            out_file.write(a.csv_header())
            for i in in_file:
                a = GroupClass()
                a.get_from_csv(i)
                a.geocode(gmaps)
                out_file.write(a.csv())
            #geocode_result = gmaps.geocode('Durham University')
            #print(len(geocode_result))
            #print(geocode_result[0]['geometry']['location'])

if 0: # convert to javascript. Obsolete
    with open('ucan_utoronto_database_production_with_geocode.csv', 'r') as in_file:
        with open('markers.js', 'w') as out_file:
            in_file.readline()
            for i, line in enumerate(in_file):
                a = GroupClass()
                a.get_from_csv(line)
                out_file.write(a.to_marker(i))

if 1: # convert to json like format
    print("Generating json.")
    with open('ucan_utoronto_database_production_with_geocode-edited2tabs.csv',
              'r', encoding="utf8") as in_file:
        with open('../json_data.js', 'w', encoding="utf8") as out_file:
            out_file.write('var data =')
            in_file.readline()
            tmp_list = []
            for i, line in enumerate(in_file):
                a = GroupClass()
                #print(line)
                a.get_from_csv(line, sep='	')#'	')
                tmp_list.append(a.json_data(i))
                #print(tmp_list[-1])
                #json.dumps(tmp_list[-1])
            json.dump(tmp_list, out_file, ensure_ascii=False)

if 1: # convert to html table.
    print('Generating html table')
    with open('ucan_utoronto_database_production_with_geocode-edited2tabs.csv',
              'r', encoding="utf8") as in_file:
        with open('../generated_table_part.html', 'w', encoding="utf8") as out_file:
            in_file.readline()
            tmp_list = ""
            a = GroupClass()
            out_file.write(a.html_header_line())
            for i, line in enumerate(in_file):
                a = GroupClass()
                a.get_from_csv(line, sep='	')#'	')
                out_file.write(a.html_line(i))
                #print(tmp_list[-1])
                #json.dumps(tmp_list[-1])
            #json.dump(tmp_list, out_file, ensure_ascii=False)
            out_file.write(a.html_ending_line())
                        
if 1: #combine htmls
    print('Combining htmls')
    with open('../index.html', 'w', encoding="utf8") as out_file:
        inlist = ['head_part.html', 'header_part.html',
                  'atoms_part.html',
                  'legendfilter.html', 
                  'periodic_part.html',
                  'table_before_part.html', 'generated_table_part.html',
                  'footer_part.html']
        for infile in inlist:
            with open('../' + infile, 'r', encoding="utf8") as in_file:
                out_file.write(in_file.read())
    print('Combined htmls')      
            
if 0: # generate checkboxes
    # Used only once.
    elements = 'H He Li Na K Rb Cs Ca Sr Cr Dy Er Yb Th Ba'.split()
    basestr = """<label><input type='checkbox' onclick='handleClick(this);' name="incheckbox" value="{:}" checked>{:}</label>"""
    for i in elements:
        print(basestr.format(i, i))

if 1:
    import simplekml
    kml = simplekml.Kml(name="Every cold atom")
    with open(new_filename, 'r', encoding="utf-8") as f:
        f.readline()
        atom_folder = kml.newfolder(name="Neutral Atoms")
        atom_group_types=("Experiment", "Experiment/Theory", "Theory")
        style = {}
        subfolders = {}
        for type in atom_group_types:
            style[type] = simplekml.Style()
            style[type].labelstyle.color = simplekml.Color.rgb(33, 59, 109)  # Make the text Qendra blue
            style[type].labelstyle.color = simplekml.Color.rgb(226, 111, 56)  # Make the text Qendra orange
            style[type].labelstyle.scale = 1.5
            style[type].iconstyle.scale = 1.5
            if type == 'Experiment':
                style[type].iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/blu-blank.png'
            elif type == 'Experiment/Theory':
                style[type].iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/purple-blank.png'
            else:
                style[type].iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/orange-blank.png'
            subfolders[type] = atom_folder.newfolder(name=type)
        for i, line in enumerate(f):
            a = GroupClass()
            #print(line)
            a.get_from_csv(line, sep=';')
            pnt = subfolders[a.exp_theor].newpoint(name=a.name,
                    description=a.exp_theor,
                    coords=[(a.long, a.lat)]
                    )
            pnt.style = style[a.exp_theor]

        kml.save(new_filename[0:-4]+".kml")

ion_trap_filename = "IonTrappers.csv"
import csv

if 0:
    import googlemaps
    with open('gmapsAPIkey.txt', 'r') as f:
        gmapsAPIkey = f.read().strip()
    gmaps = googlemaps.Client(key=gmapsAPIkey)

    with open(ion_trap_filename, 'r', encoding="utf-8-sig") as f:
        reader = csv.reader(f, dialect="excel")
        header = next(reader)
        expected_headers = [
                "",
                "Country",
                "State",
                "City",
                "Institution",
                "Group",
                "Head",
                "Ions"
                ]
        print(header)
        for c_idx, c in enumerate(header):
            if (c != expected_headers[c_idx]):
                raise KeyError("Unexpected header: " + c + ", expected " + expected_headers[c_idx])

        ion_trappers = []
        for i, row in enumerate(reader):
            ion_trappers.append({})
            for c_idx, c in enumerate(header):
                ion_trappers[i][c] = row[c_idx]

            print(ion_trappers[i])

            """ Get location from address using Google Maps API. """
            query = ', '.join([ion_trappers[i]["Institution"],ion_trappers[i]["Country"], ion_trappers[i]["City"]])

            geocode_result = gmaps.geocode(query)
            if len(geocode_result) == 0:
                print("No results for "+query)
            ion_trappers[i]["Lat"] = geocode_result[0]['geometry']['location']['lat']
            ion_trappers[i]["Long"] = geocode_result[0]['geometry']['location']['lng']        

        expected_headers.append("Lat")
        expected_headers.append("Long")

        with open(ion_trap_filename[0:-4]+"_geocode.csv", 'w') as out_f:
            writer = csv.writer(out_f, dialect="excel")
            writer.writerow(expected_headers)
            for ion_trapper in ion_trappers:
                writer.writerow(ion_trapper.values())

if 1:
    import simplekml
    kml = simplekml.Kml(name="Trapped Ions")
    with open(ion_trap_filename[:-4]+"_geocode.csv", 'r', encoding="utf-8") as f:
        reader = csv.reader(f, dialect="excel")
        header = next(reader)
        ion_folder = kml.newfolder(name="Trapped Ions")
        style = simplekml.Style()
        style.labelstyle.color = simplekml.Color.rgb(33, 59, 109)  # Make the text Qendra blue
        style.labelstyle.color = simplekml.Color.rgb(226, 111, 56)  # Make the text Qendra orange
        style.labelstyle.scale = 1.5
        style.iconstyle.scale = 1.5
        style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/pink-blank.png'
        sep = ','
        for i, row in enumerate(reader):
            ion_trapper = {}
            for c_idx, c in enumerate(row):
                ion_trapper[header[c_idx]] = c
            pnt = ion_folder.newpoint(name=ion_trapper["Group"],
                    description=ion_trapper["Ions"],
                    coords=[(ion_trapper["Long"], ion_trapper["Lat"])]
                    )
            pnt.style = style

        kml.save(ion_trap_filename[:-4]+".kml")






    
"""
How to convert csv to excel.
Open csv in Notepad++.
Convert to UTF-8

How to convert excel to csv.
Ctrl+a, Ctrl+a (the second time is needed to select also the header row).
Ctrl+c
Ctrl+v in notepad++.
"""
