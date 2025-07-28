import re, sys
import csv

# How to use the extractor:
# In the same folder, keep a band.txt where you paste the credits from Discogs that you want to extract.
# The extractor needs three csv files with the following columns: artist,band,year,role
# The extractor will add unwanted credits into the unwanted csv file, wanted credits into the wanted csv file
# and the credits that cannot be identified as wanted or unwanted, will go to the others.csv file.
# You should manually check others to find posible instruments that are not being covered in the wanted list.
# You can (and should) add more instruments into the wanted, unwanted roles that you get from the others.csv.

# The program takes the following arguments:
#  -  BAND/ARTISTNAME 
#  -  solo/band 
#  -  YEAR

# You should pass band as argument if you are extracting a band (two or more artists that release music 
# as an entity). Otherwise you pass solo as an argument for a solo artist. 
# That will allow, for example, that Neil Young is credited as Vocals. If you pass band as an 
# argument, Oasis would be added in "unwanted.csv" as Producter.

if sys.argv[2].strip() == "band":
   is_band = True 
elif sys.argv[2].strip() == "solo":
   is_band = False 
else:
   sys.exit("Solo/Band argument was wrong")

wanted = "path to wanted csv"
unwanted = "path to unwanted csv"
other = "path to others csv"


wanted_roles = ["voic","voca","musician","performer","scratch","vocoder","e-bow","programmed",
          "guitar","sitar","banjo","dobro","mandolin","bass","drum","tom tom","table","organ",
          "keyboard","pian","rhodes","mellotron","synth","violin","viola","percussion","handclaps",
          "hihat","pandeiro","cajon","tamb","bata","prod","mixing","mixed","saxophone","accordion",
          "trumpet","flute","trombone","horn","whistle","recorder","harmonica","oboe","cello",
          "strings","conductor","arranged","orchestra","choir","ukulele","harp","harmonium","marimba",
          "vibraphone","cymbal","clarinet","whistl","tuba", "congas", "bongos", "featuring", "feat",
          "reeds","psaltery","concertina","brass","timbales","beatbox","gong","clarinet","bouzouki",
          "conductor"]
unwanted_roles = ["cover", "engineer","photography","design","art","lacquer","written","lyrics",
                  "managment","master","recorded", "a&r","liner notes","sleeve notes","layout", "technician"]

def get_role(text):
   for word in wanted_roles:
      if word in text: return "Wanted"
   for word in unwanted_roles: 
      if word in text: return "Unwanted"
   return "Other"

added = []

with open("band.txt", 'r') as f:
   for line in f:
      if not any(sep in line for sep in [" – ", " - "]):
            continue 
      if line.strip() == "":
         continue
      if " – " in line:
         fields = line.strip().split(" – ")
      elif " - " in line:
         fields = line.strip().split(" - ")
      elif ": " in line:
         fields = line.strip().split(": ")
      artists = re.sub(r'\([^\)]+\)', '', fields[1].strip()).split(', ')
      for artist in artists:
         artist = re.sub(r"(\").*?(\")", r"\g<1>\g<2>", artist.replace('*', ''))
         artist = re.sub(r"[\"].*?[\"]", r"", artist)
         role = get_role(fields[0].lower())
         new_row = [artist.strip().replace('  ', ' '), sys.argv[1].replace('_', ' '), sys.argv[3], fields[0]]

         if (is_band and artist.strip().replace('  ', ' ') == sys.argv[1].replace('_', ' ')):
            with open (unwanted, mode= 'a', newline='') as unwanted:
               writer = csv.writer(unwanted)
               writer.writerow(new_row)
         elif (role == "Wanted"):
            with open (wanted, mode= 'a', newline='') as wanted:
               writer = csv.writer(wanted)
               writer.writerow(new_row)
            added.append(f"{artist.strip().replace('  ', ' ')} as {fields[0]}.")
         elif (role == "Unwanted"):
            with open (unwanted, mode= 'a', newline='') as unwanted:
               writer = csv.writer(unwanted)
               writer.writerow(new_row)
   
         else:
            with open (other, mode= 'a', newline='') as others:
               writer = csv.writer(others)
               writer.writerow(new_row)

print("Artist added:")
for line in added:
   print(line)

