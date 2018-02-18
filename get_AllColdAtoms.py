import requests
from bs4 import BeautifulSoup
import json

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
            self.institution = institution[0].text.strip()

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
            self.fields = fields[0].text.strip().replace(';', ',,').replace('\n', '        ')
            # to je res bolj description, ne tolk seznam fieldov.

        people = thediv.find_all("span", {"class": "people"})
        if len(people) == 0:
            self.people = GroupClass.defaults['people']
        else:
            self.people = people[0].text.strip().replace(';', ',,').replace('\n', '        ')

        self.webpage = thediv.find('div', {'class': "group_homepage"}).a['href']
        # maybe I should use find instead of find_all the whole time!

        self.atom = ''

        if 0:
            print(self.name, self.institution, self.country, self.exp_theor, sep='\t|\t')
            print('\t', self.fields, self.people, sep='\t|\t')
            print(self.webpage)
            print()
        
        return thediv

    def csv(self): # should probably use built-in csv writer.
        all_vars = [self.name, self.webpage, self.institution,
            self.country, self.address, self.lat, self.long,
            self.exp_theor, self.fields,
            self.people, self.atom, self.comment]
        
        all_vars = list(map(str, all_vars))
        return ';'.join(all_vars) + '\n'

    def csv_header(self):
        all_vars = ['name', 'webpage', 'institution',
            'country', 'address', 'lat', 'long',
            'exp_theor', 'fields',
            'people', 'atom', 'comment']
        return ';'.join(all_vars) + '\n'

    def get_from_csv(self, line, sep=';'):
        line = line.strip('\n')
        #print(line.split(sep))
        (self.name, self.webpage, self.institution,
            self.country, self.address, self.lat,
            self.long, self.exp_theor, self.fields,
            self.people, self.atom, self.comment) = line.split(sep)
        self.lat = float(self.lat)
        self.long = float(self.long)

    def get_from_csv2(self, line):
        print(len(line))
        (self.name, self.webpage, self.institution,
            self.country, self.address, self.lat,
            self.long, self.exp_theor, self.fields,
            self.people, self.atom, self.comment) = line
        self.lat = float(self.lat)
        self.long = float(self.long)


    def __eq__(self, other):
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
        Converts self to javascript marker object
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

    def json_data(self):
        ret = dict()
        ret['lat'] = self.lat
        ret['long'] = self.long
        ret['desc'] = '<a href="{webpage}"><b>{name}</b></a><br />{institution}, {country}<br />'.format(
            i, name=self.name.replace('\'', '\\\''), webpage=self.webpage.replace('\'', '\\\''),
            institution=self.institution.replace('\'', '\\\''), country=self.country)
        ret['desc'] += '<b>Research:</b> {:}<br />{:}<br />'.format(self.exp_theor, self.fields)
        ret['desc'] += '<b>Permanent researchers and staff:</b> {:}<br />'.format(self.people)
        ret['desc'] += '<b>Editors note:</b> {:}<br />'.format(self.comment)
        ret['atom'] = self.atom
        ret['exp_theor'] = self.exp_theor
        return ret

    def html_header_line(self):
        ret = """<div class="tg-wrap"><table id="tg-tg00" class="tg">
<tr>
    <th class="tg-tg01">Group</th>
    <th class="tg-tg02">Institution</th>
    <th class="tg-tg03">Country</th>
    <th class="tg-tg04">Lat</th>
    <th class="tg-tg05">Long</th>
    <th class="tg-tg06">Exp/Theory</th>
    <th class="tg-tg07">Description</th>
    <th class="tg-tg08">People</th>
    <th class="tg-tg09">Atoms</th>
    <th class="tg-tg10">Comment</th>
  </tr>
"""
        return ret

    def html_ending_line(self):
        ret = """</table></div>"""
        return ret

    
    def html_line(self):
        ret = ''
        ret = """  <tr>
    <td class="tg-tg{0:02d}"><a href="{webpage}"><b>{name}</b></a></td>
    <td class="tg-tg{1:02d}">{institution}</td>
    <td class="tg-tg{2:02d}">{country}</td>
    <td class="tg-tg{3:02d}">{lat}</td>
    <td class="tg-tg{4:02d}">{long}</td>
    <td class="tg-tg{5:02d}">{exp_theor}</td>
    <td class="tg-tg{6:02d}"><div class="makescrollable">{desc}</div></td>
    <td class="tg-tg{7:02d}"><div class="makescrollable">{people}</div></td>
    <td class="tg-tg{8:02d}">{atoms}</td>
    <td class="tg-tg{9:02d}">{comment}</td>

  </tr>
""".format(*list(range(1,13)),
           name=self.name, webpage=self.webpage,
           institution=self.institution,
           country=self.country,
           lat=self.lat,
           long=self.long,
           exp_theor=self.exp_theor,
           desc=self.fields,
           atoms=self.atom,
           people=self.people,
           comment=self.comment)
        return ret
           
        

######################################################################
"""
I'll have a base database. And manual corrections.
And automatic change detection, which I'll manually
add to production. Hopefully.
"""
######################################################################

if 0: # load all        
    base_url = 'https://ucan.physics.utoronto.ca/Groups'
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    thetable = soup.find_all("table", {"class": "listing"})
    if len(thetable) != 1:
        print('The len of the table != 1', len(thetable))
    thetable = thetable[0].tbody

    a = GroupClass()

    count = 0
    with open('ucan_utoronto_database.csv', 'w', encoding="utf-8") as f:
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

# Todo geocode with better names.
# Currently some insitution names are cities.
# Issues: Multiple groups at the same institution.

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

if 0: # convert to javascript
    with open('ucan_utoronto_database_production_with_geocode.csv', 'r') as in_file:
        with open('markers.js', 'w') as out_file:
            in_file.readline()
            for i, line in enumerate(in_file):
                a = GroupClass()
                a.get_from_csv(line)
                out_file.write(a.to_marker(i))

if 0: # convert to json like format
    with open('ucan_utoronto_database_production_with_geocode-edited2tabs.csv',
              'r', encoding="utf8") as in_file:
        with open('json_data.js', 'w', encoding="utf8") as out_file:
            in_file.readline()
            tmp_list = []
            for i, line in enumerate(in_file):
                a = GroupClass()
                a.get_from_csv(line, sep='	')
                tmp_list.append(a.json_data())
                #print(tmp_list[-1])
                #json.dumps(tmp_list[-1])
            json.dump(tmp_list, out_file, ensure_ascii=False)

if 0: # convert to json like format with new csv
    # does not work.
    import csv
    with open('ucan_utoronto_database_production_with_geocode-edited2tabs.csv',
              'r', newline='', encoding="utf8") as in_file:
        with open('json_data.js', 'w') as out_file:
            in_data = csv.reader(in_file)
            #print(in_data[0])
            #in_data.pop(0)
            tmp_list = []
            for i, line in enumerate(in_file):
                print(line)
                a = GroupClass()
                a.get_from_csv2(line)
                tmp_list.append(a.json_data())
                #print(tmp_list[-1])
                #json.dumps(tmp_list[-1])
            json.dump(tmp_list, out_file, ensure_ascii=False)

if 0: # convert to html table.
    with open('ucan_utoronto_database_production_with_geocode-edited2tabs.csv',
              'r', encoding="utf8") as in_file:
        with open('webpage/generated_table_part.html', 'w', encoding="utf8") as out_file:
            in_file.readline()
            tmp_list = ""
            a = GroupClass()
            out_file.write(a.html_header_line())
            for i, line in enumerate(in_file):
                a = GroupClass()
                a.get_from_csv(line, sep='	')
                out_file.write(a.html_line())
                #print(tmp_list[-1])
                #json.dumps(tmp_list[-1])
            #json.dump(tmp_list, out_file, ensure_ascii=False)
            out_file.write(a.html_ending_line())
                        
if 1: #combine htmls
    print('Combining htmls')
    with open('webpage/index.html', 'w', encoding="utf8") as out_file:
        inlist = ['head_part.html', 'header_part.html',
                  'atoms_part.html',
                  'periodic_part.html',
                  'table_before_part.html', 'generated_table_part.html',
                  'footer_part.html']
        for infile in inlist:
            with open('webpage/' + infile, 'r', encoding="utf8") as in_file:
                out_file.write(in_file.read())
    print('Combined htmls')      
            
if 0: # generate checkboxes
    elements = 'H He Li Na K Rb Cs Ca Sr Cr Dy Er Yb Th Ba'.split()
    basestr = """<label><input type='checkbox' onclick='handleClick(this);' name="incheckbox" value="{:}" checked>{:}</label>"""
    for i in elements:
        print(basestr.format(i, i))
    