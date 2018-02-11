# This module generates html map that has three layers: locations, where films
# were filmed, population of countries and lakes of North America
from math import nan
import pandas as pd
import folium


def read_films_by_year(path, year):
    """
    (str, int) -> pandas.DataFrame
    Read films from file that were filmed in particular year and store their
    name and filming location in tha pandas DataFrame
    """
    films = {'name': [], 'location': []}
    with open(path, 'r', encoding='utf-8', errors='ignore') as filecontent:
        for line in filecontent:
            if line == '==============\n':
                break
        for line in filecontent:
            if '(' + str(year) + ')' in line or '(' + str(year) + '/' in line:
                films['name'].append(line.strip().split('\t')[0])
                location = line.strip().split('\t')[-2].strip() \
                    if line.strip().split('\t')[-1][0] == '(' \
                    else line.strip().split('\t')[-1].strip()
                films['location'].append(location)
    films = pd.DataFrame(films)
    return films


def read_locations(path):
    """
    (str, int) -> dict(str: tuple)
    Read latitude and longitude of all locations, where films where filmed from
    file and store them in the dictionary where names of locations are keys
    and tuple of coordinates as values
    """
    locations = {}
    with open(path, 'r', encoding='utf-8', errors='ignore') as filecontent:
        filecontent.readline()
        for line in filecontent:
            spline = line.strip().split('\t')
            if len(spline) < 3:
                continue
            locations[spline[0]] = (float(spline[1]), float(spline[2]))
    return locations


def find_coordinates(locations, df):
    """
    dict(str: tuple), pd.DataFrame -> pd.DataFrame, int
    Return dataframe where location column is replaced by corresponding
    coordinates columns and number of locations
    """
    df['latitude'] = df.apply(lambda x:
                              locations.get(x.location, (nan, nan))[0],
                              axis=1)
    df['longitude'] = df.apply(lambda x:
                               locations.get(x.location, (nan, nan))[1],
                               axis=1)
    # drop missing values
    df.dropna(how='any', inplace=True)
    loc_num = len(df.groupby(['longitude', 'latitude']))
    del df['location']
    return df, loc_num


def create_map(df, markers_num=100):
    """
    (pd.DataFrame, int) -> None
    Create map with 3 layers: films locations, country population and
    lakes in North America. markers_num parameter shows how many markers will
    be displayed on the map, if that number is available.
    """
    webmap = folium.Map()

    # add films markers to the map
    fg1 = folium.FeatureGroup(name='Films')
    df = pd.DataFrame(df.groupby(['longitude', 'latitude']).
                      apply(lambda x: '</li><li>'.join(x['name'])),
                      columns=['name'])
    df['name'] = '<ul><li>' + df['name'] + '</li></ul>'
    df.reset_index(inplace=True)
    df = df.sample(frac=1).reset_index(drop=True)
    for index, x in df.iterrows():
        if index < markers_num:
            # set width and height for the IFrame
            height = min(20 * len(x['name'].split('<li>')), 200)
            width = 500
            i_frame = folium.IFrame(html=x['name'], width=width, height=height)
            name = folium.Popup(i_frame, parse_html=True)
            fg1.add_child(folium.Marker(location=[x['latitude'],
                                                  x['longitude']],
                                        popup=name, icon=folium.Icon()))
        else:
            break
    webmap.add_child(fg1)

    # add population data to the map
    pop = folium.FeatureGroup(name='Population')
    pop.add_child(folium.GeoJson(data=open('world.json', 'r',
                                 encoding='utf-8-sig').read(),
                                 style_function=lambda x: {'fillColor': 'green'
           if x['properties']['POP2005'] < 10000000
           else 'orange' if 10000000 <= x['properties']['POP2005'] < 50000000
           else 'red'}))
    webmap.add_child(pop)

    # add lakes of North America on the map
    lakes = folium.FeatureGroup(name='Lakes NA')
    lakes.add_child(folium.GeoJson(data=open('lakes_na.geojson', 'r',
                                             encoding='utf-8-sig').read()))
    webmap.add_child(lakes)

    webmap.add_child(folium.LayerControl())
    webmap.save('films_map.html')
    print('Map is ready to use!!!')


def main():
    """
    None -> None
    Handle input and output of the program
    """
    while True:
        try:
            year = int(input('Year: '))
            if year < 0:
                raise ValueError('Year must be a positive integer! Try again')
            # read films from particular year into films dataframe
            films = read_films_by_year('locations.list', year)
            # read coordinates of locations form tsv file
            locations = read_locations('locations.tsv')
            # update films dataframe with coordinates of locations
            films, loc_num = find_coordinates(locations, films)
            print(f'{loc_num} locations were(was) found')
            break
        except ValueError as err_message:
            print(err_message)
            continue

    while True:
        try:
            marker_num = int(input('Markers number: '))
            if marker_num < 0:
                raise ValueError('Markers number must be a positive integer!')
            break
        except ValueError as err_message:
            print(err_message)
            continue

    create_map(films, marker_num)


main()
