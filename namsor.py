#!/usr/bin/python3
# Using NamSor's API to collect the nationality, ethnicity, and gender of job applicants at Northeastern
#
# Copyright: (c) Yakov Bart
#            (c) Marty Vo
#
# Maintainers: y.bart@northeastern.edu
#              vo.ma@northeastern.edu

import json
import csv
import country_converter
from country_converter.country_converter import CountryConverter

ETHNICITY_FILES = ["ethnicity_staff_intake/ethnicity_1_500.json",
                   "ethnicity_staff_intake/ethnicity_501_1000.json",
                   "ethnicity_staff_intake/ethnicity_1001_1500.json",
                   "ethnicity_staff_intake/ethnicity_1501_2000.json",
                   "ethnicity_staff_intake/ethnicity_2001_2500.json",
                   "ethnicity_staff_intake/ethnicity_2501_3000.json",
                   "ethnicity_staff_intake/ethnicity_3001_3500.json",
                   "ethnicity_staff_intake/ethnicity_3501_3689.json"]

NATIONALITY_FILES = ["nationality_staff_intake/nationality_1_500.json",
                     "nationality_staff_intake/nationality_501_1000.json",
                     "nationality_staff_intake/nationality_1001_1500.json",
                     "nationality_staff_intake/nationality_1501_2000.json",
                     "nationality_staff_intake/nationality_2001_2500.json",
                     "nationality_staff_intake/nationality_2501_3000.json",
                     "nationality_staff_intake/nationality_3001_3500.json",
                     "nationality_staff_intake/nationality_3501_3689.json"]

GENDER_FILES = ["genders_staff_intake/genders_1_500.json",
                "genders_staff_intake/genders_501_1000.json",
                "genders_staff_intake/genders_1001_2000.json",
                "genders_staff_intake/genders_2001_3000.json",
                "genders_staff_intake/genders_3001_3689.json"]

INDEX = 0

# Template used for obtaining the gender of individuals through NamSor API
# Data is sent in a POST request and responses are returned in JSON form
request_template = {
  "personalNames": [
    {
      "id": "string",
      "firstName": "string",
      "lastName": "string",
    }
  ]
}

# As data is parsed, add the classifications to the list
classifications = []

# Placeholder for formatting data from CSV
personalInfo = []

# Parsing the given CSV name list of first and last names
def parse_csv():
  with open("staff_intake.csv", mode='r', encoding='utf-8') as csv_file:
      csv_reader = csv.reader(csv_file)

      id = 0
      for line in csv_reader:
          if id == 0:
              id += 1
          else:
              personalInfo.append({"id": str(id), "firstName": line[1], "lastName": line[2]})
              id += 1
              

      # print(personalInfo)

      request_template["personalNames"] = personalInfo
        
      print(json.dumps(request_template))

      # Note that the parsed .txt file may contain some byte encoding issues. 
      # Resolve these errors by going through the output file and searching for byte strings.
      f = open("request_template.json", "w")
      f.write(json.dumps(request_template))
      f.close()


# Combining the ethnicity JSON files
def combine_ethnicity_files():
  for file in ETHNICITY_FILES:
      with open(file) as f:
        ethnicity_file = json.load(f)
        data = ethnicity_file["personalNames"]
        for person in data: 
          classifications.append({"id": person["id"],
                                  "firstName": person["firstName"],
                                  "lastName": person["lastName"],
                                  "ethnicity": person["raceEthnicity"],
                                  "ethnicityAccuracy": person["probabilityCalibrated"],
                                  "altEthnicity": person["raceEthnicityAlt"],
                                  "ethnicityAltAccuracy": person["probabilityAltCalibrated"]})

# Combining the nationality JSON files
def combine_nationality_files():
  global INDEX
  # Instantiate the country converter object for better performance
  converter = CountryConverter()
  for file in NATIONALITY_FILES:
      with open(file) as f:
        nationality_file = json.load(f)
        data = nationality_file["personalNames"]
        for person in data: 
          current = classifications[INDEX]
          current["countryOrigin"] = person["countryOrigin"]
          current["countryFullName"] = converter.convert(names=person["countryOrigin"], to='name_short')
          current["countryOriginAccuracy"] = person["probabilityCalibrated"]
          current["countryOriginAlt"] = person["countryOriginAlt"]
          current["countryFullNameAlt"] = converter.convert(names=person["countryOriginAlt"], to='name_short')
          current["countryOriginAltAccuracy"] = person["probabilityAltCalibrated"]
          INDEX += 1
  INDEX = 0

# Combining the gender JSON files
def combine_gender_files():
  global INDEX
  for file in GENDER_FILES:
      with open(file) as f:
        gender_file = json.load(f)
        data = gender_file["personalNames"]
        for person in data: 
          current = classifications[INDEX]
          current["gender"] = person["likelyGender"]
          current["genderAccuracy"] = person["probabilityCalibrated"]
          INDEX += 1
  INDEX = 0
  
# Combine all classifications and write to singular JSON file
def write_json():
  f = open("staff_intake_classifications.json", "w")
  class_list = {"classifications": classifications}
  f.write(json.dumps(class_list, indent=2, sort_keys=False))
  f.close()

# Write classification data into CSV file
def write_csv():
  with open('staff_intake_classifications.json') as json_file:
    data = json.load(json_file)
    classifications = data["classifications"]

    csv_file = open('staff_intake_classifications.csv', 'w', newline='')
    csv_writer = csv.writer(csv_file)

    count = 0

    for person in classifications:
      if count == 0:
        header = person.keys()
        csv_writer.writerow(header)
        count += 1
      
      csv_writer.writerow(person.values())
    
    csv_file.close()


###### Script ######

# print("Parsing name list CSV...")
# parse_csv()

print("Combining ethnicity classifications...")
combine_ethnicity_files()

print("Combining nationality classifications...")
combine_nationality_files()

print("Combining gender classifications...")
combine_gender_files()

print("Writing to JSON file")
write_json()

print("Writing to CSV file")
write_csv()

print("Finished")