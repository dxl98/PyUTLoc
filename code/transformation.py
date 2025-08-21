from pygeodesy import gars, wgrs, ups
import mgrs
import utm
import pyproj
from openlocationcode import openlocationcode as olc
import geohash2
import maidenhead
from pyproj import CRS, Transformer
import csv


class DD1toOthers:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return f"{self.lat} {self.lon}"

    @staticmethod
    def batch_convert_from_csv(csv_file_path, conversion_method_name):
        results = []
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                lat = float(row[0])
                lon = float(row[1])
                dd1_coordinates = DD1toOthers(lat, lon)
                conversion_method = getattr(dd1_coordinates, conversion_method_name, None)
                if callable(conversion_method):
                    results.append(conversion_method())
                else:
                    results.append(f"Invalid conversion method: {conversion_method_name}")
        return results

    def dd1_to_dd2(self):
        lat_direction = "N" if self.lat >= 0 else "S"
        lon_direction = "E" if self.lon >= 0 else "W"
        return f"{abs(self.lat)}{lat_direction} {abs(self.lon)}{lon_direction}"

    def dd1_to_dd3(self):
        lat_direction = "N" if self.lat >= 0 else "S"
        lon_direction = "E" if self.lon >= 0 else "W"
        return f"{lat_direction}{abs(self.lat)} {lon_direction}{abs(self.lon)}"

    @staticmethod
    def decimal_degree_to_degree_minute(decimal_degree):
        degree = int(decimal_degree)
        minute = abs(decimal_degree - degree) * 60
        return f"{degree}°{minute:.3f}'"

    def dd1_to_ddm1(self):
        lat_str = self.decimal_degree_to_degree_minute(self.lat)
        lon_str = self.decimal_degree_to_degree_minute(self.lon)
        return f"{lat_str} {lon_str}"

    def dd1_to_ddm2(self):
        lat_dir = 'S' if self.lat < 0 else 'N'
        lon_dir = 'W' if self.lon < 0 else 'E'
        lat_str = self.decimal_degree_to_degree_minute(abs(self.lat))
        lon_str = self.decimal_degree_to_degree_minute(abs(self.lon))
        return f"{lat_str}{lat_dir} {lon_str}{lon_dir}"

    def dd1_to_ddm3(self):
        lat_dir = 'S' if self.lat < 0 else 'N'
        lon_dir = 'W' if self.lon < 0 else 'E'
        lat_str = self.decimal_degree_to_degree_minute(abs(self.lat))
        lon_str = self.decimal_degree_to_degree_minute(abs(self.lon))
        return f"{lat_dir}{lat_str} {lon_dir}{lon_str}"

    @staticmethod
    def decimal_to_dms(decimal):
        degree = int(decimal)
        minute_decimal = abs(decimal - degree) * 60
        minute = int(minute_decimal)
        second = (minute_decimal - minute) * 60
        return degree, minute, round(second, 2)

    def dd1_to_dms1(self):
        lat_degree, lat_minute, lat_second = self.decimal_to_dms(self.lat)
        lon_degree, lon_minute, lon_second = self.decimal_to_dms(self.lon)

        return f"{lat_degree}° {lat_minute}' {lat_second}\" {lon_degree}° {lon_minute}' {lon_second}\""

    def dd1_to_dms2(self):
        lat_degree, lat_minute, lat_second = self.decimal_to_dms(self.lat)
        lon_degree, lon_minute, lon_second = self.decimal_to_dms(self.lon)

        lat_direction = "N" if self.lat >= 0 else "S"
        lon_direction = "E" if self.lon >= 0 else "W"

        return f"{abs(lat_degree)}° {lat_minute}' {lat_second}\"{lat_direction} {abs(lon_degree)}° {lon_minute}' {lon_second}\"{lon_direction}"

    def dd1_to_dms3(self):
        lat_degree, lat_minute, lat_second = self.decimal_to_dms(self.lat)
        lon_degree, lon_minute, lon_second = self.decimal_to_dms(self.lon)

        lat_direction = "N" if self.lat >= 0 else "S"
        lon_direction = "E" if self.lon >= 0 else "W"

        return f"{lat_direction}{abs(lat_degree)}° {lat_minute}' {lat_second}\" {lon_direction}{abs(lon_degree)}° {lon_minute}' {lon_second}\""

    def dd1_to_gars(self):
        lat = self.lat
        lon = self.lon
        gars_coord = gars.encode(lat, lon, precision=2)
        return gars_coord

    def dd1_to_georef(self):
        lat = self.lat
        lon = self.lon
        wgrs_coord = wgrs.encode(lat, lon, precision=6, height=None, radius=None)
        return wgrs_coord

    def dd1_to_mgrs(self):
        lat = self.lat
        lon = self.lon
        m = mgrs.MGRS()
        mgrs_coord = m.toMGRS(lat, lon, MGRSPrecision=5)
        return mgrs_coord

    def dd1_to_usgn(self):
        lat = self.lat
        lon = self.lon
        m = mgrs.MGRS()
        usgn_coord = m.toMGRS(lat, lon, MGRSPrecision=5)
        return usgn_coord

    def dd1_to_utm1(self):
        lat = self.lat
        lon = self.lon
        utm_result = utm.from_latlon(lat, lon)
        zone_number = utm_result[2]
        zone_letter = utm_result[3]
        easting = utm_result[0]
        northing = utm_result[1]
        utm1_coord = f"{zone_number}{zone_letter} {easting:.6g} {northing:.7g}"
        return utm1_coord

    def dd1_to_utm2(self):
        lat = self.lat
        lon = self.lon
        utm_result = utm.from_latlon(lat, lon)
        zone_number = utm_result[2]
        zone_letter = utm_result[3]
        easting = utm_result[0]
        northing = utm_result[1]
        utm2_coord = f"{zone_number}{zone_letter}{easting:.6g}{northing:.7g}"
        return utm2_coord

    def dd1_to_ups(self):
        lat = self.lat
        lon = self.lon
        ups_coord = ups.toUps8(lat, lon)
        return ups_coord

    def dd1_to_plus_codes(self):
        lat = self.lat
        lon = self.lon
        plus_codes_coord = olc.encode(lat, lon)
        return plus_codes_coord

    def dd1_to_geohash(self):
        lat = self.lat
        lon = self.lon
        geohash_coord = geohash2.encode(lat, lon, precision=12)
        return geohash_coord

    def dd1_to_maidenhead(self):
        lat = self.lat
        lon = self.lon
        maidenhead_coord = maidenhead.to_maiden(lat, lon)
        return maidenhead_coord

    def dd1_to_pms1(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "m"
        return f"{georef[0]}{unit} {georef[1]}{unit}"

    def dd1_to_pms2(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "cm"
        return f"{georef[0] * 100}{unit} {georef[1] * 100}{unit}"

    def dd1_to_pms3(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "dm"
        return f"{georef[0] * 10}{unit} {georef[1] * 10}{unit}"

    def dd1_to_pms4(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "ft"
        return f"{georef[0] * 3.28084}{unit} {georef[1] * 3.28084}{unit}"

    def dd1_to_pms5(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "in"
        return f"{georef[0] * 39.3701}{unit} {georef[1] * 39.3701}{unit}"

    def dd1_to_pms6(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "km"
        return f"{georef[0] * 0.001}{unit} {georef[1] * 0.001}{unit}"

    def dd1_to_pms7(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "mi"
        return f"{georef[0] * 0.00062}{unit} {georef[1] * 0.00062}{unit}"

    def dd1_to_pms8(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "mm"
        return f"{georef[0] * 1000}{unit} {georef[1] * 1000}{unit}"

    def dd1_to_pms9(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "nmi"
        return f"{georef[0] * 0.00054}{unit} {georef[1] * 0.00054}{unit}"

    def dd1_to_pms10(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "pt"
        return f"{georef[0] * 35.2778}{unit} {georef[1] * 35.2778}{unit}"

    def dd1_to_pms11(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "usft"
        return f"{georef[0] * 3.28083}{unit} {georef[1] * 3.28083}{unit}"

    def dd1_to_pms12(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "yd"
        return f"{georef[0] * 1.0936}{unit} {georef[1] * 1.0936}{unit}"

    def dd1_to_pmb1(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "m"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0])}{unit} {X_direction} {abs(georef[1])}{unit} {Y_direction}"

    def dd1_to_pmb2(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "cm"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0]) * 100}{unit} {X_direction} {abs(georef[1]) * 100}{unit} {Y_direction}"

    def dd1_to_pmb3(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "dm"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0]) * 10}{unit} {X_direction} {abs(georef[1]) * 10}{unit} {Y_direction}"

    def dd1_to_pmb4(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "ft"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0]) * 3.28084}{unit} {X_direction} {abs(georef[1]) * 3.28084}{unit} {Y_direction}"

    def dd1_to_pmb5(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "in"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0]) * 39.3701}{unit} {X_direction} {abs(georef[1]) * 39.3701}{unit} {Y_direction}"

    def dd1_to_pmb6(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "km"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0]) * 0.001}{unit} {X_direction} {abs(georef[1]) * 0.001}{unit} {Y_direction}"

    def dd1_to_pmb7(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "mi"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0]) * 0.00062}{unit} {X_direction} {abs(georef[1]) * 0.00062}{unit} {Y_direction}"

    def dd1_to_pmb8(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "mm"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0]) * 1000}{unit} {X_direction} {abs(georef[1]) * 1000}{unit} {Y_direction}"

    def dd1_to_pmb9(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "nmi"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0]) * 0.00054}{unit} {X_direction} {abs(georef[1]) * 0.00054}{unit} {Y_direction}"

    def dd1_to_pmb10(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "pt"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0]) * 35.2778}{unit} {X_direction} {abs(georef[1]) * 35.2778}{unit} {Y_direction}"

    def dd1_to_pmb11(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "usft"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0]) * 3.28083}{unit} {X_direction} {abs(georef[1]) * 3.28083}{unit} {Y_direction}"

    def dd1_to_pmb12(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "yd"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{abs(georef[0]) * 1.0936}{unit} {X_direction} {abs(georef[1]) * 1.0936}{unit} {Y_direction}"

    def dd1_to_pme1(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "m"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0])}{unit} {Y_direction} {abs(georef[1])}{unit}"

    def dd1_to_pme2(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "cm"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0] * 100)}{unit} {Y_direction} {abs(georef[1]) * 100}{unit}"

    def dd1_to_pme3(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "dm"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0] * 10)}{unit} {Y_direction} {abs(georef[1]) * 10}{unit}"

    def dd1_to_pme4(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "ft"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0] * 3.28084)}{unit} {Y_direction} {abs(georef[1]) * 3.28084}{unit}"

    def dd1_to_pme5(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "in"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0] * 39.3701)}{unit} {Y_direction} {abs(georef[1]) * 39.3701}{unit}"

    def dd1_to_pme6(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "km"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0] * 0.001)}{unit} {Y_direction} {abs(georef[1]) * 0.001}{unit}"

    def dd1_to_pme7(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "mi"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0] * 0.00062)}{unit} {Y_direction} {abs(georef[1]) * 0.00062}{unit}"

    def dd1_to_pme8(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "mm"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0] * 1000)}{unit} {Y_direction} {abs(georef[1]) * 1000}{unit}"

    def dd1_to_pme9(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "nmi"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0] * 0.00054)}{unit} {Y_direction} {abs(georef[1]) * 0.00054}{unit}"

    def dd1_to_pme10(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "pt"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0] * 35.2778)}{unit} {Y_direction} {abs(georef[1]) * 35.2778}{unit}"

    def dd1_to_pme11(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "usft"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0] * 3.28083)}{unit} {Y_direction} {abs(georef[1]) * 3.28083}{unit}"

    def dd1_to_pme12(self):
        lat = self.lat
        lon = self.lon
        src_crs = CRS.from_epsg(4326)
        dst_crs = CRS.from_string("EPSG:3857")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lon, lat)
        unit = "yd"
        X_direction = "N" if georef[0] >= 0 else "S"
        Y_direction = "E" if georef[1] >= 0 else "W"
        return f"{X_direction} {abs(georef[0] * 1.0936)}{unit} {Y_direction} {abs(georef[1]) * 1.0936}{unit}"


class OtherstoDD1:
    def __init__(self, lat=None, lon=None):
        self.lat = lat
        self.lon = lon

    @staticmethod
    def batch_convert_from_csv(csv_file_path, conversion_method_name):
        results = []
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                lat = row[0]
                lon = row[1]

                if '°' in lat:
                    lat_degree, lat_rest = lat.split('°')
                    lat_minute, lat_dir = lat_rest.split("'")
                    lat_degree = float(lat_degree)
                    lat_minute = float(lat_minute) / 60.0
                    if lat_dir == 'S':
                        lat_degree = -lat_degree
                        lat_minute = -lat_minute
                    new_lat = lat_degree + lat_minute
                else:
                    new_lat = 0.0

                if '°' in lon:
                    lon_degree, lon_rest = lon.split('°')
                    lon_minute, lon_dir = lon_rest.split("'")
                    lon_degree = float(lon_degree)
                    lon_minute = float(lon_minute) / 60.0
                    if lon_dir == 'W':
                        lon_degree = -lon_degree
                        lon_minute = -lon_minute
                    new_lon = lon_degree + lon_minute
                else:
                    new_lon = 0.0

                results.append(f"{new_lat:.2f}° {new_lon:.2f}°")

        return results


    def dd2_to_dd1(self):
        lat_value, lat_dir = self.lat[:-2], self.lat[-1]
        lat_value = float(lat_value)
        if lat_dir == 'S':
            lat_value = -lat_value

        lon_value, lon_dir = self.lon[:-2], self.lon[-1]
        lon_value = float(lon_value)
        if lon_dir == 'W':
            lon_value = -lon_value

        return f"{lat_value:.2f}° {lon_value:.2f}°"


    def dd3_to_dd1(self):
        lat_dir, lat_value = self.lat[0], self.lat[1:-1]
        lat_value = float(lat_value)
        if lat_dir == 'S':
            lat_value = -lat_value

        lon_dir, lon_value = self.lon[0], self.lon[1:-1]
        lon_value = float(lon_value)
        if lon_dir == 'W':
            lon_value = -lon_value

        return f"{lat_value:.2f}° {lon_value:.2f}°"


    def ddm1_to_dd1(self):
        lat_degree, lat_minute = self.lat.split('°')
        lat_minute = lat_minute.replace("'", "")
        lat_degree = float(lat_degree)
        lat_minute = float(lat_minute) / 60.0
        if lat_degree < 0:
            lat_minute = -lat_minute
        new_lat = lat_degree + lat_minute

        lon_degree, lon_minute = self.lon.split('°')
        lon_minute = lon_minute.replace("'", "")
        lon_degree = float(lon_degree)
        lon_minute = float(lon_minute) / 60.0
        if lon_degree < 0:
            lon_minute = -lon_minute
        new_lon = lon_degree + lon_minute

        return f"{new_lat:.2f}° {new_lon:.2f}°"


    def ddm2_to_dd1(self):
        lat_degree, lat_rest = self.lat.split('°')
        lat_minute, lat_dir = lat_rest.split("'")
        lat_degree = float(lat_degree)
        lat_minute = float(lat_minute) / 60.0
        if lat_dir == 'S':
            lat_degree = -lat_degree
            lat_minute = -lat_minute
        new_lat = lat_degree + lat_minute

        lon_degree, lon_rest = self.lon.split('°')
        lon_minute, lon_dir = lon_rest.split("'")
        lon_degree = float(lon_degree)
        lon_minute = float(lon_minute) / 60.0
        if lon_dir == 'W':
            lon_degree = -lon_degree
            lon_minute = -lon_minute
        new_lon = lon_degree + lon_minute

        return f"{new_lat:.2f}° {new_lon:.2f}°"

    def ddm3_to_dd1(self):
        lat_dir, lat_degree, lat_minute = self.lat[0], self.lat[1:].split('°')[0], self.lat[1:].split('°')[1].replace(
            "'", "")
        lat_degree = float(lat_degree)
        lat_minute = float(lat_minute) / 60.0
        if lat_dir == 'S':
            lat_degree = -lat_degree
            lat_minute = -lat_minute
        new_lat = lat_degree + lat_minute

        lon_dir, lon_degree, lon_minute = self.lon[0], self.lon[1:].split('°')[0], self.lon[1:].split('°')[1].replace(
            "'", "")
        lon_degree = float(lon_degree)
        lon_minute = float(lon_minute) / 60.0
        if lon_dir == 'W':
            lon_degree = -lon_degree
            lon_minute = -lon_minute
        new_lon = lon_degree + lon_minute

        return f"{new_lat:.2f}° {new_lon:.2f}°"

    def dms1_to_dd1(self):
        lat_degree, lat_rest = self.lat.split('°')
        lat_minute, lat_second = lat_rest.split("'")[0], lat_rest.split('"')[0].split("'")[1]
        lat_degree = float(lat_degree)
        lat_minute = float(lat_minute) / 60.0
        lat_second = float(lat_second) / 3600.0
        if lat_degree < 0:
            lat_minute = -lat_minute
            lat_second = -lat_second
        new_lat = lat_degree + lat_minute + lat_second

        lon_degree, lon_rest = self.lon.split('°')
        lon_minute, lon_second = lon_rest.split("'")[0], lon_rest.split('"')[0].split("'")[1]
        lon_degree = float(lon_degree)
        lon_minute = float(lon_minute) / 60.0
        lon_second = float(lon_second) / 3600.0
        if lon_degree < 0:
            lon_minute = -lon_minute
            lon_second = -lon_second
        new_lon = lon_degree + lon_minute + lon_second

        return f"{new_lat:.2f}° {new_lon:.2f}°"

    def dms2_to_dd1(self):
        lat_degree, lat_rest = self.lat.split('°')
        lat_minute, lat_part = lat_rest.split("'")
        lat_second, lat_dir = lat_part.split('"')
        lat_degree = float(lat_degree)
        lat_minute = float(lat_minute) / 60.0
        lat_second = float(lat_second) / 3600.0
        if lat_dir == 'S':
            lat_degree = -lat_degree
            lat_minute = -lat_minute
            lat_second = -lat_second
        new_lat = lat_degree + lat_minute + lat_second

        lon_degree, lon_rest = self.lon.split('°')
        lon_minute, lon_part = lon_rest.split("'")
        lon_second, lon_dir = lon_part.split('"')
        lon_degree = float(lon_degree)
        lon_minute = float(lon_minute) / 60.0
        lon_second = float(lon_second) / 3600.0
        if lon_dir == 'W':
            lon_degree = -lon_degree
            lon_minute = -lon_minute
            lon_second = -lon_second
        new_lon = lon_degree + lon_minute + lon_second

        return f"{new_lat:.2f}° {new_lon:.2f}°"

    def dms3_to_dd1(self):
        lat_dir, lat_degree, lat_rest = self.lat[0], self.lat[1:].split('°')[0], self.lat[1:].split('°')[1]
        lat_minute, lat_second = lat_rest.split("'")[0], lat_rest.split('"')[0].split("'")[1]
        lat_degree = float(lat_degree)
        lat_minute = float(lat_minute) / 60.0
        lat_second = float(lat_second) / 3600.0
        if lat_dir == 'S':
            lat_degree = -lat_degree
            lat_minute = -lat_minute
            lat_second = -lat_second
        new_lat = lat_degree + lat_minute + lat_second

        lon_dir, lon_degree, lon_rest = self.lon[0], self.lon[1:].split('°')[0], self.lon[1:].split('°')[1]
        lon_minute, lon_second = lon_rest.split("'")[0], lon_rest.split('"')[0].split("'")[1]
        lon_degree = float(lon_degree)
        lon_minute = float(lon_minute) / 60.0
        lon_second = float(lon_second) / 3600.0
        if lon_dir == 'W':
            lon_degree = -lon_degree
            lon_minute = -lon_minute
            lon_second = -lon_second
        new_lon = lon_degree + lon_minute + lon_second

        return f"{new_lat:.2f}° {new_lon:.2f}°"

    def pms1_to_dd1(self):
        lat_value = self.lat[:-1]
        lat = float(lat_value)

        lon_value = self.lon[:-1]
        lon = float(lon_value)

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pms2_to_dd1(self):
        lat_value = self.lat[:-2]
        lat = float(lat_value) / 100

        lon_value = self.lon[:-2]
        lon = float(lon_value) / 100

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pms3_to_dd1(self):
        lat_value = self.lat[:-2]
        lat = float(lat_value) / 10

        lon_value = self.lon[:-2]
        lon = float(lon_value) / 10

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pms4_to_dd1(self):
        lat_value = self.lat[:-2]
        lat = float(lat_value) / 3.28084

        lon_value = self.lon[:-2]
        lon = float(lon_value) / 3.28084

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pms5_to_dd1(self):
        lat_value = self.lat[:-2]
        lat = float(lat_value) / 39.3701

        lon_value = self.lon[:-2]
        lon = float(lon_value) / 39.3701

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pms6_to_dd1(self):
        lat_value = self.lat[:-2]
        lat = float(lat_value) / 0.001

        lon_value = self.lon[:-2]
        lon = float(lon_value) / 0.001

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pms7_to_dd1(self):
        lat_value = self.lat[:-2]
        lat = float(lat_value) / 0.00062

        lon_value = self.lon[:-2]
        lon = float(lon_value) / 0.00062

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pms8_to_dd1(self):
        lat_value = self.lat[:-2]
        lat = float(lat_value) / 1000

        lon_value = self.lon[:-2]
        lon = float(lon_value) / 1000

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pms9_to_dd1(self):
        lat_value = self.lat[:-3]
        lat = float(lat_value) / 0.00054

        lon_value = self.lon[:-3]
        lon = float(lon_value) / 0.00054

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pms10_to_dd1(self):
        lat_value = self.lat[:-2]
        lat = float(lat_value) / 35.2778

        lon_value = self.lon[:-2]
        lon = float(lon_value) / 35.2778

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pms11_to_dd1(self):
        lat_value = self.lat[:-4]
        lat = float(lat_value) / 3.28083

        lon_value = self.lon[:-4]
        lon = float(lon_value) / 3.28083

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pms12_to_dd1(self):
        lat_value = self.lat[:-2]
        lat = float(lat_value) / 1.0936

        lon_value = self.lon[:-2]
        lon = float(lon_value) / 1.0936

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb1_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-1]
        lat = float(lat_value)
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-1]
        lon = float(lon_value)
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb2_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 100
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 100
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb3_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 10
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 10
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb4_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 3.28084
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 3.28084
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb5_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 39.3701
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 39.3701
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb6_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 0.001
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 0.001
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb7_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 0.00062
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 0.00062
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb8_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 1000
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 1000
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb9_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-3]
        lat = float(lat_value) / 0.00054
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-3]
        lon = float(lon_value) / 0.00054
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb10_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 35.2778
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 35.2778
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb11_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-4]
        lat = float(lat_value) / 3.28083
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-4]
        lon = float(lon_value) / 3.28083
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pmb12_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[0], lat_list[1]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 1.0936
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[0], lon_list[1]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 1.0936
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme1_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-1]
        lat = float(lat_value)
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-1]
        lon = float(lon_value)
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme2_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 100
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 100
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme3_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 10
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 10
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme4_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 3.28084
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 3.28084
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme5_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 39.3701
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 39.3701
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme6_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 0.001
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 0.001
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme7_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 0.00062
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 0.00062
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme8_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 1000
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 1000
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme9_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-3]
        lat = float(lat_value) / 0.00054
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-3]
        lon = float(lon_value) / 0.00054
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme10_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 35.2778
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 35.2778
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme11_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-4]
        lat = float(lat_value) / 3.28083
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-4]
        lon = float(lon_value) / 3.28083
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"

    def pme12_to_dd1(self):
        lat_list = self.lat.split()
        lat_value, lat_dir = lat_list[1], lat_list[0]
        lat_value = lat_value[:-2]
        lat = float(lat_value) / 1.0936
        if lat_dir == 'S':
            lat = -lat

        lon_list = self.lon.split()
        lon_value, lon_dir = lon_list[1], lon_list[0]
        lon_value = lon_value[:-2]
        lon = float(lon_value) / 1.0936
        if lon_dir == 'W':
            lon = -lon

        src_crs = CRS.from_epsg(3857)
        dst_crs = CRS.from_string("EPSG:4326")
        transformer = Transformer.from_crs(src_crs, dst_crs)
        georef = transformer.transform(lat, lon)

        return f"{georef[1]:.2f}° {georef[0]:.2f}°"


def gars_to_dd1(gars_coords):
    dd1 = gars.decode3(gars_coords, center=True)
    return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"


def georef_to_dd1(georef_coords):
    dd1 = wgrs.decode3(georef_coords, center=True)
    return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"


def mgrs_to_dd1(mgrs_coords):
    m = mgrs.MGRS()
    dd1 = m.toLatLon(mgrs_coords)
    return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"


def usgn_to_dd1(usgn_coords):
    m = mgrs.MGRS()
    dd1 = m.toLatLon(usgn_coords)
    return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"


def utm1_to_dd1(utm1_coords):
    utm1 = utm1_coords.split()
    ZONE, EASTING, NORTHING = utm1[0], utm1[1], utm1[2]
    ZONE_NUMBER, ZONE_LETTER = ZONE[0:2], ZONE[-1]
    EASTING, NORTHING = float(EASTING), float(NORTHING)
    ZONE_NUMBER = int(ZONE_NUMBER)
    dd1 = utm.to_latlon(EASTING, NORTHING, ZONE_NUMBER, ZONE_LETTER)
    return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"


def utm2_to_dd1(utm2_coords):
    EASTING, NORTHING, ZONE_NUMBER, ZONE_LETTER = utm2_coords[3:9], utm2_coords[9:], utm2_coords[0:2], utm2_coords[2],
    EASTING, NORTHING = float(EASTING), float(NORTHING)
    ZONE_NUMBER = int(ZONE_NUMBER)
    dd1 = utm.to_latlon(EASTING, NORTHING, ZONE_NUMBER, ZONE_LETTER)
    return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"


def ups_to_dd1(ups_coords):

    ups = ups_coords.split()
    E, N, hemisphere = ups[1], ups[2], ups[0],
    E, N = float(E), float(N)

    if hemisphere == 'N':
        proj_string = "+proj=stere +lat_0=90 +lat_ts=90 +lon_0=0 +k=0.994 +x_0=2000000 +y_0=2000000 +ellps=WGS84 +units=m +no_defs"
    elif hemisphere == 'S':
        proj_string = "+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=0.994 +x_0=2000000 +y_0=2000000 +ellps=WGS84 +units=m +no_defs"
    else:
        raise ValueError("Hemisphere must be 'N' or 'S'.")

    ups_proj = pyproj.Proj(proj_string)
    wgs84_proj = pyproj.Proj(proj='latlong', datum='WGS84')

    lon, lat = pyproj.transform(ups_proj, wgs84_proj, E, N)

    return f"{lat:.2f}° {lon:.2f}°"


def plus_codes_to_dd1(plus_codes_coord):
    dd1 = olc.decode(plus_codes_coord)
    dd1 = str(dd1)
    dd1 = dd1.strip('[')
    dd1 = dd1.strip(']')
    dd1 = dd1.split(", ")
    dd1[0], dd1[1] = float(dd1[0]), float(dd1[1])
    return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"


def geohash_to_dd1(geohash_coord):
    dd1 = geohash2.decode(geohash_coord)
    dd1 = list(dd1)
    dd1[0], dd1[1] = float(dd1[0]), float(dd1[1])
    return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"


def maidenhead_to_dd1(maidenhead_coord):
    dd1 = maidenhead.to_location(maidenhead_coord)
    return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"


class SpecialCoordsToDD1:
    def __init__(self, coords_list):
        self.coords_list = coords_list

    def gars_to_dd1(self, gars_coords):
        dd1 = gars.decode3(gars_coords, center=True)
        return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"

    def georef_to_dd1(self, georef_coords):
        dd1 = wgrs.decode3(georef_coords, center=True)
        return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"

    def mgrs_to_dd1(self, mgrs_coords):
        m = mgrs.MGRS()
        dd1 = m.toLatLon(mgrs_coords)
        return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"

    def usgn_to_dd1(self, usgn_coords):
        m = mgrs.MGRS()
        dd1 = m.toLatLon(usgn_coords)
        return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"

    def utm1_to_dd1(self, utm1_coords):
        utm1 = utm1_coords.split()
        ZONE, EASTING, NORTHING = utm1[0], utm1[1], utm1[2]
        ZONE_NUMBER, ZONE_LETTER = ZONE[0:2], ZONE[-1]
        EASTING, NORTHING = float(EASTING), float(NORTHING)
        ZONE_NUMBER = int(ZONE_NUMBER)
        dd1 = utm.to_latlon(EASTING, NORTHING, ZONE_NUMBER, ZONE_LETTER)
        return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"

    def utm2_to_dd1(self, utm2_coords):
        EASTING, NORTHING, ZONE_NUMBER, ZONE_LETTER = utm2_coords[3:9], utm2_coords[9:], utm2_coords[0:2], utm2_coords[
            2],
        EASTING, NORTHING = float(EASTING), float(NORTHING)
        ZONE_NUMBER = int(ZONE_NUMBER)
        dd1 = utm.to_latlon(EASTING, NORTHING, ZONE_NUMBER, ZONE_LETTER)
        return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"

    def ups_to_dd1(self, ups_coords):
        ups = ups_coords.split()
        E, N, hemisphere = ups[1], ups[2], ups[0],
        E, N = float(E), float(N)

        if hemisphere == 'N':
            proj_string = "+proj=stere +lat_0=90 +lat_ts=90 +lon_0=0 +k=0.994 +x_0=2000000 +y_0=2000000 +ellps=WGS84 +units=m +no_defs"
        elif hemisphere == 'S':
            proj_string = "+proj=stere +lat_0=-90 +lat_ts=-90 +lon_0=0 +k=0.994 +x_0=2000000 +y_0=2000000 +ellps=WGS84 +units=m +no_defs"
        else:
            raise ValueError("Hemisphere must be 'N' or 'S'.")

        ups_proj = pyproj.Proj(proj_string)
        wgs84_proj = pyproj.Proj(proj='latlong', datum='WGS84')

        lon, lat = pyproj.transform(ups_proj, wgs84_proj, E, N)

        return f"{lat:.2f}° {lon:.2f}°"

    def plus_codes_to_dd1(self, plus_codes_coord):
        dd1 = olc.decode(plus_codes_coord)
        dd1 = str(dd1)
        dd1 = dd1.strip('[')
        dd1 = dd1.strip(']')
        dd1 = dd1.split(", ")
        dd1[0], dd1[1] = float(dd1[0]), float(dd1[1])
        return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"

    def geohash_to_dd1(self, geohash_coord):
        dd1 = geohash2.decode(geohash_coord)
        dd1 = list(dd1)
        dd1[0], dd1[1] = float(dd1[0]), float(dd1[1])
        return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"

    def maidenhead_to_dd1(self, maidenhead_coord):
        dd1 = maidenhead.to_location(maidenhead_coord)
        return f"{dd1[0]:.2f}° {dd1[1]:.2f}°"

    def batch_convert_from_csv(self, csv_file_path, conversion_method_name):
        results = []
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                coords = row[0]

                conversion_method = getattr(self, conversion_method_name, None)
                if callable(conversion_method):
                    results.append(conversion_method(coords))
                else:
                    results.append(f"Invalid conversion method: {conversion_method_name}")
        return results


class LengthConverter:
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def convert(self, target_unit):
        if self.unit == target_unit:
            return self.value

        conversion_factors = {
            'cm': 1,
            'dm': 0.1,
            'ft': 0.0328084,
            'in': 0.393701,
            'km': 0.00001,
            'm': 0.01,
            'mi': 0.0000062137,
            'mm': 10,
            'nmi': 0.0000053996,
            'pt': 0.352778,
            'usft': 0.0328084 / 0.3048006,
            'yd': 0.0109361
        }

        if self.unit in conversion_factors and target_unit in conversion_factors:
            conversion_factor = conversion_factors[self.unit] / conversion_factors[target_unit]
            converted_value = self.value * conversion_factor
            return converted_value
        else:
            return None


# Usage examples
# value = 12345.12
# unit = 'm'
#
# converter = LengthConverter(value, unit)
#
# converted_cm = converter.convert('cm')
# converted_dm = converter.convert('dm')
# converted_ft = converter.convert('ft')
# converted_in = converter.convert('in')
# converted_km = converter.convert('km')
# converted_mi = converter.convert('mi')
# converted_mm = converter.convert('mm')
# converted_nmi = converter.convert('nmi')
# converted_pt = converter.convert('pt')
# converted_usft = converter.convert('usft')
# converted_yd = converter.convert('yd')
#
# print(f"{value}{unit} convert to cm: {converted_cm}cm")
# print(f"{value}{unit} convert to dm: {converted_dm}dm")
# print(f"{value}{unit} convert to ft: {converted_ft}ft")
# print(f"{value}{unit} convert to in: {converted_in}in")
# print(f"{value}{unit} convert to km: {converted_km}km")
# print(f"{value}{unit} convert to mi: {converted_mi}mi")
# print(f"{value}{unit} convert to mm: {converted_mm}mm")
# print(f"{value}{unit} convert to nmi: {converted_nmi}nmi")
# print(f"{value}{unit} convert to pt: {converted_pt}pt")
# print(f"{value}{unit} convert to usft: {converted_usft}usft")
# print(f"{value}{unit} convert to yd: {converted_yd}yd")

# if __name__ == "__main__":
#     #     dd1 = DD1toOthers(40.7128, -74.0060)
#     #     dd11 = DD1toOthers(-80, 118.43)
#
#     #     print("DD1:", dd1)
#     #     print("DD1_to_DD2:", dd1.dd1_to_dd2())
#     #     print("DD1_to_DD3:", dd1.dd1_to_dd3())
#     #     print("DD1_to_DDM1:", dd1.dd1_to_ddm1())
#     #     print("DD1_to_DDM2:", dd1.dd1_to_ddm2())
#     #     print("DD1_to_DDM3:", dd1.dd1_to_ddm3())
#     #     print("DD1_to_DMS1:", dd1.dd1_to_dms1())
#     #     print("DD1_to_DMS2:", dd1.dd1_to_dms2())
#     #     print("DD1_to_DMS3:", dd1.dd1_to_dms3())
#     #     print("DD1_to_GARS:", dd1.dd1_to_gars())
#     #     print("DD1_to_GEOREF:", dd1.dd1_to_georef())
#     #     print("DD1_to_MGRS:", dd1.dd1_to_mgrs())
#     #     print("DD1_to_USGN:", dd1.dd1_to_usgn())
#     #     print("DD1_to_UTM1:", dd1.dd1_to_utm1())
#     #     print("DD1_to_UTM2:", dd1.dd1_to_utm2())
#     #     print("DD1_to_UPS:", dd11.dd1_to_ups())
#     #     print("DD1_to_Plus Codes:", dd1.dd1_to_plus_codes())
#     #     print("DD1_to_Geohash:", dd1.dd1_to_geohash())
#     #     print("DD1_to_Maidenhead:", dd1.dd1_to_maidenhead())
#     #     print("DD1_to_PMS1:", dd1.dd1_to_pms1())
#     #     print("DD1_to_PMB1:", dd1.dd1_to_pmb1())
#     #     print("DD1_to_PME1:", dd1.dd1_to_pme1())
#     #     print("DD1_to_PMS2:", dd1.dd1_to_pms2())
#     #     print("DD1_to_PMB2:", dd1.dd1_to_pmb2())
#     #     print("DD1_to_PME2:", dd1.dd1_to_pme2())
#     #     print("DD1_to_PMS3:", dd1.dd1_to_pms3())
#     #     print("DD1_to_PMB3:", dd1.dd1_to_pmb3())
#     #     print("DD1_to_PME3:", dd1.dd1_to_pme3())
#     #     print("DD1_to_PMS4:", dd1.dd1_to_pms4())
#     #     print("DD1_to_PMB4:", dd1.dd1_to_pmb4())
#     #     print("DD1_to_PME4:", dd1.dd1_to_pme4())
#     #     print("DD1_to_PMS5:", dd1.dd1_to_pms5())
#     #     print("DD1_to_PMB5:", dd1.dd1_to_pmb5())
#     #     print("DD1_to_PME5:", dd1.dd1_to_pme5())
#     #     print("DD1_to_PMS6:", dd1.dd1_to_pms6())
#     #     print("DD1_to_PMB6:", dd1.dd1_to_pmb6())
#     #     print("DD1_to_PME6:", dd1.dd1_to_pme6())
#     #     print("DD1_to_PMS7:", dd1.dd1_to_pms7())
#     #     print("DD1_to_PMB7:", dd1.dd1_to_pmb7())
#     #     print("DD1_to_PME7:", dd1.dd1_to_pme7())
#     #     print("DD1_to_PMS8:", dd1.dd1_to_pms8())
#     #     print("DD1_to_PMB8:", dd1.dd1_to_pmb8())
#     #     print("DD1_to_PME8:", dd1.dd1_to_pme8())
#     #     print("DD1_to_PMS9:", dd1.dd1_to_pms9())
#     #     print("DD1_to_PMB9:", dd1.dd1_to_pmb9())
#     #     print("DD1_to_PME9:", dd1.dd1_to_pme9())
#     #     print("DD1_to_PMS10:", dd1.dd1_to_pms10())
#     #     print("DD1_to_PMB10:", dd1.dd1_to_pmb10())
#     #     print("DD1_to_PME10:", dd1.dd1_to_pme10())
#     #     print("DD1_to_PMS11:", dd1.dd1_to_pms11())
#     #     print("DD1_to_PMB11:", dd1.dd1_to_pmb11())
#     #     print("DD1_to_PME11:", dd1.dd1_to_pme11())
#     #     print("DD1_to_PMS12:", dd1.dd1_to_pms12())
#     #     print("DD1_to_PMB12:", dd1.dd1_to_pmb12())
#     #     print("DD1_to_PME12:", dd1.dd1_to_pme12())
#
#     #     dd2 = OtherstoDD1("34.12°S", "118.43°E")
#     #     print("DD2_to_DD1:", dd2.dd2_to_dd1())  # Output: -34.12°, 118.43°
#
#     #     dd3 = OtherstoDD1("S34.12°", "E118.43°")
#     #     print("DD3_to_DD1:", dd3.dd3_to_dd1())  # Output: -34.12°, 118.43°
#
#     #     ddm1 = OtherstoDD1("-34°7.404'", "118°25.926'")
#     #     print("DDM1_to_DD1:", ddm1.ddm1_to_dd1())  # Output: -34.12°, 118.43°
#
#     #     ddm2 = OtherstoDD1("34°7.404'S", "118°25.926'E")
#     #     print("DDM2_to_DD1:", ddm2.ddm2_to_dd1())  # Output: -34.12°, 118.43°
#
#     #     ddm3 = OtherstoDD1("S34°7.404'", "E118°25.926'")
#     #     print("DDM3_to_DD1:", ddm3.ddm3_to_dd1())  # Output: -34.12°, 118.43°
#
#     #     dms1 = OtherstoDD1("-34°7'12\"", "118°25'48\"")
#     #     print("DMS1_to_DD1:", dms1.dms1_to_dd1())  # Output: -34.12°, 118.43°
#
#     #     dms2 = OtherstoDD1("34°7'12\"S", "118°25'48\"E")
#     #     print("DMS2_to_DD1:", dms2.dms2_to_dd1())  # Output: -34.12°, 118.43°
#
#     #     dms3 = OtherstoDD1("S34°7'12\"", "E118°25'48\"")
#     #     print("DMS3_to_DD1:", dms3.dms3_to_dd1())  # Output: -34.12°, 118.43°
#
#     #     gars_coords = "597ER26"
#     #     print("GARS_to_DD1:", gars_to_dd1(gars_coords))
#
#     #     georef_coords = "VDPL2580052800"
#     #     print("GEOREF_to_DD1:", gars_to_dd1(gars_coords))
#
#     #     mgrs_coords = "50HPH3187623615"
#     #     print("MGRS_to_DD1:", mgrs_to_dd1(mgrs_coords))
#
#     #     usgn_coords = "50HPH3187623615"
#     #     print("MGRS_to_DD1:", mgrs_to_dd1(mgrs_coords))
#
#     #     utm1_coords = "50H 631877 6223615"
#     #     print("UTM1_to_DD1:", utm1_to_dd1(utm1_coords))
#
#     #     utm2_coords = "50H6318776223615"
#     #     print("UTM2_to_DD1:", utm1_to_dd1(utm1_coords))
#
#     #     ups_coords = "S 2978729 1470141"
#     #     print("UPS_to_DD1:", ups_to_dd1(ups_coords))
#
#     #     plus_codes = "4PQWVCJJ+22"
#     #     print("Plus_Codes_to_DD1:", plus_codes_to_dd1(plus_codes))
#
#     #     geohash_codes = "q9ujyuwhe502"
#     #     print("Geohash_to_DD1:", geohash_to_dd1(geohash_codes))
#
#     #     maidenhead_codes = "OF95fv"
#     #     print("Maidenhead_Grid_to_DD1:", maidenhead_to_dd1(maidenhead_codes))
#
#     #     pms1 = OtherstoDD1("4532128.1647683885m", "-12517968.827857949m")
#     #     print("PMS1_to_DD1:", pms1.pms1_to_dd1())
#
#     #     pms2 = OtherstoDD1("453212816.4768388cm", "-1251796882.785795cm")
#     #     print("PMS2_to_DD1:", pms2.pms2_to_dd1())
#
#     #     pms3 = OtherstoDD1("45321281.64768389dm", "-125179688.27857949dm")
#     #     print("PMS3_to_DD1:", pms3.pms3_to_dd1())
#
#     #     pms4 = OtherstoDD1("14869187.368098719ft", "-41069452.849189475ft")
#     #     print("PMS4_to_DD1:", pms4.pms4_to_dd1())
#
#     #     pms5 = OtherstoDD1("178430339.05974793in", "-492833684.54965025in")
#     #     print("PMS5_to_DD1:", pms5.pms5_to_dd1())
#
#     #     pms6 = OtherstoDD1("4532.128164768388km", "-12517.968827857949km")
#     #     print("PMS6_to_DD1:", pms6.pms6_to_dd1())
#
#     #     pms7 = OtherstoDD1("2809.9194621564006mi", "-7761.140673271928mi")
#     #     print("PMS7_to_DD1:", pms7.pms7_to_dd1())
#
#     #     pms8 = OtherstoDD1("4532128164.768389mm", "-12517968827.857948mm")
#     #     print("PMS8_to_DD1:", pms8.pms8_to_dd1())
#
#     #     pms9 = OtherstoDD1("2447.3492089749298nmi", "-6759.7031670432925nmi")
#     #     print("PMS9_to_DD1:", pms9.pms9_to_dd1())
#
#     #     pms10 = OtherstoDD1("159883510.97106627pt", "-441606400.71540713pt")
#     #     print("PMS10_to_DD1:", pms10.pms10_to_dd1())
#
#     #     pms11 = OtherstoDD1("14869142.046817072usft", "-41069327.66950119usft")
#     #     print("PMS11_to_DD1:", pms11.pms11_to_dd1())
#
#     #     pms12 = OtherstoDD1("4956335.36099071yd", "-13689650.710145451yd")
#     #     print("PMS12_to_DD1:", pms12.pms12_to_dd1())
#
#     #     pmb1 = OtherstoDD1("4532128.1647683885m N", "12517968.827857949m W")
#     #     print("PMB1_to_DD1:", pmb1.pmb1_to_dd1())
#
#     #     pmb2 = OtherstoDD1("453212816.4768388cm N", "1251796882.785795cm W")
#     #     print("PMB2_to_DD1:", pmb2.pmb2_to_dd1())
#
#     #     pmb3 = OtherstoDD1("45321281.64768389dm N", "125179688.27857949dm W")
#     #     print("PMB3_to_DD1:", pmb3.pmb3_to_dd1())
#
#     #     pmb4 = OtherstoDD1("14869187.368098719ft N", "41069452.849189475ft W")
#     #     print("PMB4_to_DD1:", pmb4.pmb4_to_dd1())
#
#     #     pmb5 = OtherstoDD1("178430339.05974793in N", "492833684.54965025in W")
#     #     print("PMB5_to_DD1:", pmb5.pmb5_to_dd1())
#
#     #     pmb6 = OtherstoDD1("4532.128164768388km N", "12517.968827857949km W")
#     #     print("PMB6_to_DD1:", pmb6.pmb6_to_dd1())
#
#     #     pmb7 = OtherstoDD1("2809.9194621564006mi N", "7761.140673271928mi W")
#     #     print("PMB7_to_DD1:", pmb7.pmb7_to_dd1())
#
#     #     pmb8 = OtherstoDD1("4532128164.768389mm N", "12517968827.857948mm W")
#     #     print("PMB8_to_DD1:", pmb8.pmb8_to_dd1())
#
#     #     pmb9 = OtherstoDD1("2447.3492089749298nmi N", "6759.7031670432925nmi W")
#     #     print("PMB9_to_DD1:", pmb9.pmb9_to_dd1())
#
#     #     pmb10 = OtherstoDD1("159883510.97106627pt N", "441606400.71540713pt W")
#     #     print("PMB10_to_DD1:", pmb10.pmb10_to_dd1())
#
#     #     pmb11 = OtherstoDD1("14869142.046817072usft N", "41069327.66950119usft W")
#     #     print("PMB11_to_DD1:", pmb11.pmb11_to_dd1())
#
#     #     pmb12 = OtherstoDD1("4956335.36099071yd N", "13689650.710145451yd W")
#     #     print("PMB12_to_DD1:", pmb12.pmb12_to_dd1())
#
#     #     pme1 = OtherstoDD1("N 4532128.1647683885m", "W 12517968.827857949m")
#     #     print("PME1_to_DD1:", pme1.pme1_to_dd1())
#
#     #     pme2 = OtherstoDD1("N 453212816.4768388cm", "W 1251796882.785795cm")
#     #     print("PME2_to_DD1:", pme2.pme2_to_dd1())
#
#     #     pme3 = OtherstoDD1("N 45321281.64768389dm", "W 125179688.27857949dm")
#     #     print("PME3_to_DD1:", pme3.pme3_to_dd1())
#
#     #     pme4 = OtherstoDD1("N 14869187.368098719ft", "W 41069452.849189475ft")
#     #     print("PME4_to_DD1:", pme4.pme4_to_dd1())
#
#     #     pme5 = OtherstoDD1("N 178430339.05974793in", "W 492833684.54965025in")
#     #     print("PME5_to_DD1:", pme5.pme5_to_dd1())
#
#     #     pme6 = OtherstoDD1("N 4532.128164768388km", "W 12517.968827857949km")
#     #     print("PME6_to_DD1:", pme6.pme6_to_dd1())
#
#     #     pme7 = OtherstoDD1("N 2809.9194621564006mi", "W 7761.140673271928mi")
#     #     print("PME7_to_DD1:", pme7.pme7_to_dd1())
#
#     #     pme8 = OtherstoDD1("N 4532128164.768389mm", "W 12517968827.857948mm")
#     #     print("PME8_to_DD1:", pme8.pme8_to_dd1())
#
#     #     pme9 = OtherstoDD1("N 2447.3492089749298nmi", "W 6759.7031670432925nmi")
#     #     print("PME9_to_DD1:", pme9.pme9_to_dd1())
#
#     #     pme10 = OtherstoDD1("N 159883510.97106627pt", "W 441606400.71540713pt")
#     #     print("PME10_to_DD1:", pme10.pme10_to_dd1())
#
#     #     pme11 = OtherstoDD1("N 14869142.046817072usft", "W 41069327.66950119usft")
#     #     print("PME11_to_DD1:", pme11.pme11_to_dd1())
#
#     #     pme12 = OtherstoDD1("N 4956335.36099071yd", "W 13689650.710145451yd")
#     #     print("PME12_to_DD1:", pme12.pme12_to_dd1())
#
#     #     # Assuming your CSV file has two columns: latitude and longitude
#     #     csv_file_path = 'C:/Users/94871/Desktop/地理坐标计算/2数据/DD1/Equatorial Guinea - Settlements.csv'
#     #     conversion_method_name = 'dd1_to_ddm2'
#
#     #     # Batch conversion from DD1 to DD2
#     #     dd1_results = DD1toOthers.batch_convert_from_csv(csv_file_path, conversion_method_name)
#     #     print("DD1 Results:", dd1_results)
#     #     print(type(dd1_results))
#
#     #     csv_file_path = "output.csv"
#
#     #     with open(csv_file_path, mode='w', newline='') as file:
#     #         writer = csv.writer(file)
#     #         writer.writerows(dd1_results)
#
#     #     print(f"CSV file '{csv_file_path}' created successfully.")
#
#     #     csv_file_path = ''
#     #     conversion_method_name = 'ddm2_to_dd1'
#
#     #     ddm2_results = OtherstoDD1.batch_convert_from_csv(csv_file_path, conversion_method_name)
#     #     print("DDM2 Results:", ddm2_results)
#
#     #     # Assuming your CSV file has two columns: latitude and longitude
#     #     csv_file_path = ''
#     #     conversion_method_name = 'dd1_to_gars'
#
#     #     # Batch conversion from DD1 to DD2
#     #     dd1_results = DD1toOthers.batch_convert_from_csv(csv_file_path, conversion_method_name)
#     #     print("DD1 Results:", dd1_results)
#     #     print(type(dd1_results))
#
#     #     csv_file_path = "output.csv"
#
#     #     with open(csv_file_path, mode='w', newline='') as file:
#     #         writer = csv.writer(file)
#     #         writer.writerows(dd1_results)
#
#     #     print(f"CSV file '{csv_file_path}' created successfully.")
#
#     coords_converter = SpecialCoordsToDD1(None)
#
#     csv_file_path = ''
#     conversion_method_name = 'gars_to_dd1'
#
#     gars_results = coords_converter.batch_convert_from_csv(csv_file_path, conversion_method_name)
#     print("GARS Results:", gars_results)