# OpenStreetMap Data Case Study

This is a Udacity project for the module "Data Wrangling" of the "Data Science for Business" course. The goal of this project is to clean the OpenStreetMap data for Rio de Janeiro, RJ, Brazil.

## Map Area

Rio de Janeiro, RJ, Brazil 

https://www.openstreetmap.org/relation/2697338

https://overpass-api.de/api/map?bbox=-43.7997,-23.1157,-43.0959,-22.7129

Sample of the data (k=100): https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/sample_rj_map.osm

I chose this area because this is the city I currently live in. It would be nice to have the opportunity to contribute to its improvement. 

## Problems Encountered in the Map

I noticed four main problems with the data, which I will discuss in the following order. Just keep in mind that names are in Portuguese, and thus the street names are called "Rua XXX", translating "Street XXX", and not " XXX Street" (the street types come first).

### 1. Over-abbreviated / Inconsistent street names 

Some Examples:

```Av``` and ```Av.``` meaning ```Avenida```

```Pça``` , ```Pça``` and ```Praca``` meaning ```Praça```

```R.```, ```Ruo``` and ```Rue``` meaning ```Rua```

 
### 2. Different key tags with the same meaning for postal codes

Some examples:

```CEP_LD``` vs ```cep:par``` vs ```zip:right```

```CEP_LE``` vs ```cep:impar```  vs ```zip:left```

```addr:zipcode``` vs ```addr:postcode```

### 3. Inconsistent postal codes

Example:

```22410-000``` vs ```22410000```

### 4. Inconsistent contact phones

```+55-21-9999-9999``` vs ```(21) 9999-9999``` vs ```9999-9999```, etc.

## Solving the problems

### 1. Over-abbreviated / Inconsistent street names 

```python
def update_name(name, mapping):
    #Corrects the not expected Street types
    #Args: 
        #name: street name
        #mapping: a mapping dict with the problem types and the write ones
    #Returns: better_name: The street name corrected
    m = street_type_re.search(name)
    better_name = name
    if m:
        better_street_type = mapping[m.group()]
        better_name = street_type_re.sub(better_street_type, name)
    return better_name
```

https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/Update_Street_Types.py

### 2. Different key tags with the same meaning for Postcodes

```python

def update_tags(tag, mapping):
    postal_tag = tag.attrib['k']
    if tag.attrib['k'] in mapping:
        postal_tag = mapping[tag.attrib['k']]     
    return postal_tag  

```
https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/Similar_Tags.py

### 3. Inconsistent postal codes

```python    
def update_postal(spell):
    #Updates postal codes from the format XXXXXXXX to XXXXX-XXX
    #Args: spell: the attrib "v" from address:postcode
    #Returns: better_zip: zip code in the XXXXX-XXX format
    if len(spell) == 8:
        better_zip = spell[0:5] + "-" + spell[5:8]                        
    return better_zip
```
https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/Clean_Postal_Codes.py

### 4. Inconsistent contact phones

```python
def update_phone(spell):
    #Updates phones to the format 
    #phone=+<country code> <area code> <local number>
    #following the ITU-T E.123 and the DIN 5008 pattern
    #Args: spell: the attrib "v" from <phone>
    #Returns: better_number: numbers in the right format
    better_number = str()
    spell = clean_phone(spell)
    if len(spell) == 12:
        #Updates complet phones to the right format
        better_number = '+' + spell[0:2] + ' ' + spell[2:4] + ' ' + spell[4:8] + '-' + spell[8:12]
    elif len(spell) == 13:
        #Updates complet cell phones to the right format
        better_number = '+' + spell[0:2] + ' ' + spell[2:4] + ' ' + spell[4:9] + '-' + spell[9:12] 
    elif len(spell) == 11 and spell[0] == '0':
        spell = spell[1:11] #remove 0 from code area
    elif len(spell) == 10 and spell[0:2] == '21': 
        #Updates phones with no country code to the right format
        better_number = '+55' + ' ' + spell[0:2] + ' ' + spell[2:6] + '-' + spell[6:10]
    elif len(spell) == 11 and spell[0:2] == '21': 
        #Updates cell phones with no country code to the right format
        better_number = '+55' + ' ' + spell[0:2] + ' ' + spell[2:7] + '-' + spell[7:11]
    elif len(spell) == 8:
        #Updates phones with no country code and no area code to the right format
        better_number = '+55 21 ' + spell[0:4] + '-' + spell[4:8]
    elif len(spell) == 9 and spell[0] == '9':
        #Updates cell phones with no country code and no area code to the right format
        better_number = '+55 21 ' + spell[0:5] + '-' + spell[5:9]
    elif spell[0:4] == '0800':
        better_number = spell[0:4] + '-' + spell[4:7] + '-' +  spell[7:11]
    elif ";" in spell: #Takes 'v' with more than one number
        if len(spell) == 25: #Complete two numbers
            better_number = '+' + spell[0:2] + ' ' + spell[2:4] + ' ' + spell[4:8] + '-' + spell[8:12] + ' ; ' + spell[13:15] + ' ' + spell[15:17] + ' ' + spell[17:21] + '-' + spell[21:25]
    else:
        print(spell, len(spell))
    return better_number
```

https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/Clean_Phone_Numbers.py

## Overview of the data

 I then parsed the data from .osm format to .csv, using the algorithm https://github.com/danicastroaraujo/OpenStreetMap-DataWrangling/blob/master/preparing_database.py. See file sizes below.
 
### File sizes

rj_map.osm ...........  281 MB

sample_rj_map.osm...... 2.8MB

nodes.csv ............. 132.5 MB

nodes_tags.csv ........ 7.1 MB

ways.csv .............. 13.6 MB

ways_tags.csv ......... 19.1 MB

ways_nodes.cv ......... 37.4 MB  


### Importing csv files to SQLite
 
 ```sql
 .mode csv
 .import /Users/daniellacastro/Downloads/nodes.csv nodes
 .schema nodes
 ```
 
 ```sql
 CREATE TABLE nodes(
  "b'id'" TEXT,
  "b'lat'" TEXT,
  "b'lon'" TEXT,
  "b'user'" TEXT,
  "b'uid'" TEXT,
  "b'version'" TEXT,
  "b'changeset'" TEXT,
  "b'timestamp'" TEXT
);
 ```
 
### Number of Nodes

```sql
 SELECT COUNT(*) from nodes;
```

```sql
  1200106
```


### Number of Ways

```sql
SELECT COUNT(*) from ways;
```

```sql
170480
```


### Numbers of Unique Users

```sql
SELECT COUNT(DISTINCT(e."b'uid'"))
FROM (SELECT "b'uid'" FROM nodes UNION ALL SELECT "b'uid'" FROM WAYS) e;
```

```sql
1691
```

### Number of shoppings

```sql
SELECT COUNT(*)
FROM nodes_tags
WHERE  "b'key'" = "b'shop'";
```

```sql
3204
```

## Additional Data Exploration


### TOP 5 contributing users 

```sql
SELECT e."b'user'", COUNT(*) as x
FROM ( SELECT "b'user'" FROM nodes UNION ALL SELECT "b'user'" FROM ways) e
GROUP by e."b'user'"
ORDER by x DESC
LIMIT 5;
```

```sql
"b'smaprs_import'",183573
"b'ThiagoPv'",172302
"b'Alexandrecw'",144411
"b'AlNo'",125908
"b'Import Rio'",84042
```

### Is there actually only Rio de Janeiro data?

```sql
SELECT "b'value'", COUNT(*)
FROM nodes_tags
WHERE  "b'key'" = "b'city'"
GROUP BY "b'value'"
ORDER by COUNT(*) DESC
LIMIT 5;
```

```sql
"b'Rio de Janeiro'",2398
"b'Niter\xc3\xb3i'",125
"b'S\xc3\xa3o Jo\xc3\xa3o de Meriti'",31
"b'Nova Igua\xc3\xa7u'",26
"b'Duque de Caxias'",25
```

As I expected, there is also data from other cities (located in Rio de Janeiro State): Niteroi, São João do Meriti, Nova Iguaçu e Duque de Caxias, among others.


## Additional Ideas

### Automatic validators

Althought there are volunteers regularly checking OpenStreetMap OSM data, there also should be automatic validators in the OpenStreetMap input tool, to avoid problems such as:

- Different/wrong phone numbers formats: there should be a dictionary with the right format per country.
- Different postcode formats: there also should be a dictionary with the right format per country. Besides, there should be a tool for postcode validating per city, to avoid problems such as I found in Rio de Janeiro data.

Benefits: More accurateness in data, making OpenStreetMaps more reliable. 
Problems: This could lead to fewer data submissions. 

## References

https://forum.openstreetmap.org/viewtopic.php?id=61604

https://forum.openstreetmap.org/viewtopic.php?id=32037

https://arjan-hada.github.io/osm-data-wrangling.html

https://wiki.openstreetmap.org/wiki/OSM_Tasking_Manager/Validating_data

http://luizschiller.com/openstreetmap/

https://github.com/yangju2011/udacity-data-analyst-nanodegree/blob/master/P3-Wrangle-OpenStreetMap-Data/OpenStreetMap%20Project%20Data%20Wrangling%20with%20SQL.pdf
