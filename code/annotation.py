import re
import csv


def get_coordinate_type(coordinate):
    patterns = {
        r'^([-+]?\d+(?:\.\d+)?)[°]?\s*([-+]?\d+(?:\.\d+)?)[°]?$': 'DD1',
        r'^([-+]?\d+(?:\.\d+)?)[°]?\s*([NSEW])\s*([-+]?\d+(?:\.\d+)?)[°]?\s*([NSEW])$': 'DD2',
        r'^([NSEW])\s*([-+]?\d+(?:\.\d+)?)[°]?\s*([NSEW])\s*([-+]?\d+(?:\.\d+)?)[°]?$': 'DD3',
        r'^([-+]?\d+(?:\.\d+)?)°?\s*(\d+(?:\.\d+)?)\'?\s*\s*([-+]?\d+(?:\.\d+)?)°?\s*(\d+(?:\.\d+)?)\'?\s*?$': 'DDM1',
        r'^(\d+(?:\.\d+)?)°?\s*(\d+(?:\.\d+)?)\'?\s*([NSEW])\s*([-+]?\d+(?:\.\d+)?)°?\s*(\d+(?:\.\d+)?)\'?\s*([NSEW])$': 'DDM2',
        r'^([NSEW])\s*([-+]?\d+(?:\.\d+)?)°?\s*(\d+(?:\.\d+)?)\'?\s*([NSEW])\s*(\d+(?:\.\d+)?)°?\s*(\d+(?:\.\d+)?)\'?$': 'DDM3',
        r'^([+-]?\d{1,3}°\s?\d{1,2}\'\s?\d{1,2}(?:\.\d{1,2})?")\s+([+-]?\d{1,3}°\s?\d{1,2}\'\s?\d{1,2}(?:\.\d{1,2})?")$': 'DMS1',
        r"(\d{1,3})°\s?(\d{1,2})'\s?(\d{1,2}(\.\d{1,2})?)\"\s?(<N|S|E|W>)": 'DMS2',
        r'^([NSEW])\s?(\d{1,3}°\s?\d{1,2}\'\s?\d{1,2}(?:\.\d{1,2})?")\s+([NSEW])\s?(\d{1,3}°\s?\d{1,2}\'\s?\d{1,2}(?:\.\d{1,2})?")$': 'DMS3',
        r'([0-6][0-9][0-9][A-HJ-NP-TV-Z]{2}[1-4]?[1-9]?)': 'GARS',
        r'[A-HJ-NP-TV-Z][A-L][A-Q][A-Q]\d{4}(?:\d{2})?(?:\d{2})?(?:\d{2})?': 'GEOREF',
        r'^([0-9]{1,2}[C-HJ-NP-X]{1}[A-Za-z]{2}[\s0-9]{0,12})$': 'MGRS',
        r'^([0-9]{1,5}[A-Za-z]{2}[A-Za-z]{2}[\s0-9]{0,12})$': 'USGN',
        r'^([-+]?\d+(?:\.\d+)?)\s*([-+]?\d+(?:\.\d+)?)$': 'UTM1',
        r'^(\d+)\s*(\w)$': 'UTM2',
        r'^([-+]?\d+(?:\.\d+)?)\s*([-+]?\d+(?:\.\d+)?)$': 'UPS',
        r'^([0-9a-z]{4,})$': 'Plus Codes',
        r'^([0-9bcdefghjkmnpqrstuvwxyz]{1}[0123456789bcdefghjkmnpqrstuvwxyz]{1,10})$': 'Geohash',
        r'^([A-Ra-r]{2}\d{2}[A-Xa-x]{2}\d{2})$': 'Maidenhead Grid',
        r'^[+-]?\d+(?:,\d+)?\.\d+m [+-]?\d+(?:,\d+)?\.\d+m$': 'PMS1',
        r'^[+-]?\d+(?:,\d+)?\.\d+cm [+-]?\d+(?:,\d+)?\.\d+cm$': 'PMS2',
        r'^[+-]?\d+(?:,\d+)?\.\d+dm [+-]?\d+(?:,\d+)?\.\d+dm$': 'PMS3',
        r'^[+-]?\d+(?:,\d+)?\.\d+ft [+-]?\d+(?:,\d+)?\.\d+ft$': 'PMS4',
        r'^[+-]?\d+(?:,\d+)?\.\d+in [+-]?\d+(?:,\d+)?\.\d+in$': 'PMS5',
        r'^[+-]?\d+(?:,\d+)?\.\d+km [+-]?\d+(?:,\d+)?\.\d+km$': 'PMS6',
        r'^[+-]?\d+(?:,\d+)?\.\d+mi [+-]?\d+(?:,\d+)?\.\d+mi$': 'PMS7',
        r'^[+-]?\d+(?:,\d+)?\.\d+mm [+-]?\d+(?:,\d+)?\.\d+mm$': 'PMS8',
        r'^[+-]?\d+(?:,\d+)?\.\d+nmi [+-]?\d+(?:,\d+)?\.\d+nmi$': 'PMS9',
        r'^[+-]?\d+(?:,\d+)?\.\d+pt [+-]?\d+(?:,\d+)?\.\d+pt$': 'PMS10',
        r'^[+-]?\d+(?:,\d+)?\.\d+ftUS [+-]?\d+(?:,\d+)?\.\d+ftUS$': 'PMS11',
        r'^[+-]?\d+(?:,\d+)?\.\d+yd [+-]?\d+(?:,\d+)?\.\d+yd$': 'PMS12',
        r'^[+-]?\d+(?:,\d+)?\.\d+m [NEWS] [+-]?\d+(?:,\d+)?\.\d+m [NEWS]$': 'PMB1',
        r'^[+-]?\d+(?:,\d+)?\.\d+cm [NEWS] [+-]?\d+(?:,\d+)?\.\d+cm [NEWS]$': 'PMB2',
        r'^[+-]?\d+(?:,\d+)?\.\d+dm [NEWS] [+-]?\d+(?:,\d+)?\.\d+dm [NEWS]$': 'PMB3',
        r'^[+-]?\d+(?:,\d+)?\.\d+ft [NEWS] [+-]?\d+(?:,\d+)?\.\d+ft [NEWS]$': 'PMB4',
        r'^[+-]?\d+(?:,\d+)?\.\d+in [NEWS] [+-]?\d+(?:,\d+)?\.\d+in [NEWS]$': 'PMB5',
        r'^[+-]?\d+(?:,\d+)?\.\d+km [NEWS] [+-]?\d+(?:,\d+)?\.\d+km [NEWS]$': 'PMB6',
        r'^[+-]?\d+(?:,\d+)?\.\d+mi [NEWS] [+-]?\d+(?:,\d+)?\.\d+mi [NEWS]$': 'PMB7',
        r'^[+-]?\d+(?:,\d+)?\.\d+mm [NEWS] [+-]?\d+(?:,\d+)?\.\d+mm [NEWS]$': 'PMB8',
        r'^[+-]?\d+(?:,\d+)?\.\d+nmi [NEWS] [+-]?\d+(?:,\d+)?\.\d+nmi [NEWS]$': 'PMB9',
        r'^[+-]?\d+(?:,\d+)?\.\d+pt [NEWS] [+-]?\d+(?:,\d+)?\.\d+pt [NEWS]$': 'PMB10',
        r'^[+-]?\d+(?:,\d+)?\.\d+ftUS [NEWS] [+-]?\d+(?:,\d+)?\.\d+ftUS [NEWS]$': 'PMB11',
        r'^[+-]?\d+(?:,\d+)?\.\d+yd [NEWS] [+-]?\d+(?:,\d+)?\.\d+yd [NEWS]$': 'PMB12',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+m [NEWS] [+-]?\d+(?:,\d+)?\.\d+m$': 'PME1',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+cm [NEWS] [+-]?\d+(?:,\d+)?\.\d+cm$': 'PME2',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+dm [NEWS] [+-]?\d+(?:,\d+)?\.\d+dm$': 'PME3',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+ft [NEWS] [+-]?\d+(?:,\d+)?\.\d+ft$': 'PME4',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+in [NEWS] [+-]?\d+(?:,\d+)?\.\d+in$': 'PME5',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+km [NEWS] [+-]?\d+(?:,\d+)?\.\d+km$': 'PME6',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+mi [NEWS] [+-]?\d+(?:,\d+)?\.\d+mi$': 'PME7',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+mm [NEWS] [+-]?\d+(?:,\d+)?\.\d+mm$': 'PME8',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+nmi [NEWS] [+-]?\d+(?:,\d+)?\.\d+nmi$': 'PME9',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+pt [NEWS] [+-]?\d+(?:,\d+)?\.\d+pt$': 'PME10',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+ftUS [NEWS] [+-]?\d+(?:,\d+)?\.\d+ftUS$': 'PME11',
        r'^[NEWS] [+-]?\d+(?:,\d+)?\.\d+yd [NEWS] [+-]?\d+(?:,\d+)?\.\d+yd$': 'PME12'
    }

    for pattern, coordinate_type in patterns.items():
        if re.match(pattern, coordinate):
            return coordinate_type

    return coordinate_type


def identify_coordinates_from_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:
                coordinate = ' '.join(row[:2])
                coordinate_type = get_coordinate_type(coordinate)
                if coordinate_type:
                    print(f"Coordinate {coordinate} belongs to type：{coordinate_type}")
                else:
                    print(f"Unable to recognize coordinates {coordinate} type")


# if __name__ == "__main__":
#     coordinate = input("Please enter the coordinate pair：")
#     coordinate_type = get_coordinate_type(coordinate)
#
#     if coordinate_type:
#         print(f"This coordinate belongs to the type：{coordinate_type}")
#     else:
#         print("Unable to identify the coordinate type")
#
#     # file_path = input("Please enter the CSV file path：")
#     # identify_coordinates_from_csv(file_path)