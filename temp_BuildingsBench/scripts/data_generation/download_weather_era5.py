from pathlib import Path
import pandas as pd
import os
import xarray as xr
from urllib.request import urlopen
import cdsapi
import pandas as pd
from typing import List

# Longitude and latitude limits of some locations used in BuildingsBench
AREA_LONLAT = {
    # 'edinburg': [55.96, -3.19, 55.95, -3.18],
    'edinburg': [55.97, -3.30, 55.90, -3.11],
    # 'massachusetts': [42.41, -71.39, 42.4, -71.38],
    'massachusetts': [42.41, -72.53, 42.34, -72.50],
    'portugal': [42, -9.5, 37, -6],
    # 'lisbon': [38.74, -9.15, 38.73, -9.14],
    'lisbon': [38.78, -9.19, 38.71, -9.11],
    # 'london': [51.51, -0.12, 51.5,-0.11],
    'london': [51.66, -0.43, 51.34, 0.17],
    # 'sceaux': [48.78, 2.29, 48.77, 2.3],
    'sceaux': [48.78, 2.28, 48.77, 2.3],
    # 'waterloo': [43.47, -80.52, 43.46, -80.51],
    'waterloo': [43.5, -80.58, 43.45, -80.50],
    'ucf': [28.61, -81.21, 28.6, -80.20],
    'asu': [33.42, -111.94, 33.41, -111.93],
    'uc-b': [37.88, -122.26, 37.87, -122.25],
    'dc': [38.89, -77.01, 38.88, -77.00]
}

def get_hourly_weather_pandas(
        start_date: str, 
        end_date: str, 
        area: List, 
        variable: List[str] = ['2m_temperature'], 
        download_path: str = None, 
        columns_name: List[str] = None) -> pd.DataFrame:
    """Download weather data from ERA5 CDS API given a date range as pandas dataframe

    Args:
        start_date (str): start date in 'YYYY-MM-DD'
        end_date (str): end date in 'YYYY-MM-DD'
        area (list): specify area by longitude and latitude limits [lat_n long_w lat_s long_e]
        variable (list[str], optional): ERA5 variables to watch. Defaults to ['2m_temperature'].
        download_path (str, optional): if not None, save raw data to this path. Defaults to None.
        columns_name (list[str], optional): specify columns' names for the returned pandas dataframe. Defaults to ['temperature'].

    Returns:
        pandas.DataFrame: Storing weather data indexed by timestamp
    """    
    
    # start the client
    cds = cdsapi.Client()
    # dataset you want to read
    dataset = 'reanalysis-era5-single-levels'
    
    params = {
        'product_type': 'reanalysis',
        'format': 'netcdf',
        'variable': variable,
        'time': [
            '00:00', '01:00', '02:00',
            '03:00', '04:00', '05:00',
            '06:00', '07:00', '08:00',
            '09:00', '10:00', '11:00',
            '12:00', '13:00', '14:00',
            '15:00', '16:00', '17:00',
            '18:00', '19:00', '20:00',
            '21:00', '22:00', '23:00',
        ],
        'date': f'{start_date}/{end_date}',
        'area': area
    }
    # retrieves the path to the file
    fl = cds.retrieve(dataset, params)
    
    if download_path is not None:
        fn = '_'.join(start_date + end_date + variable) + '_raw.nc'
        fl.download(download_path + '/' + fn)
        print(f"Saved raw file: {download_path + '/' + fn}")
            
    # load into memory
    with urlopen(fl.location) as f:
        ds = xr.open_dataset(f.read())
    
    # average values across latitude and longitude
    mean_ds = ds.mean(dim=['latitude', 'longitude'])
    
    # to pandas dataframe
    df = mean_ds.to_pandas()
    df.columns = columns_name if columns_name is not None else variable
    
    return df


def calc_relative_humidity(temp, dewpoint):
    # https://earthscience.stackexchange.com/questions/16570/how-to-calculate-relative-humidity-from-temperature-dew-point-and-pressure
    import math
    b = 17.625
    c = 243.04
    return 100 * math.exp((c * b * (dewpoint - temp)) / ((c + temp) * (c + dewpoint)))

def main():
    real_building_prefix = Path(os.environ.get('BUILDINGS_BENCH', ''))
    real_building_ds = [('LCL', 'london', '2011-01-01', '2014-12-31', 0), ('IDEAL', 'edinburg', '2017-01-01', '2018-12-31', 0), 
                      ('Sceaux', 'sceaux', '2006-12-31', '2011-01-01', 1), ('Borealis', 'waterloo', '2010-12-31', '2013-01-01', -5),
                      ('Electricity', 'lisbon', '2011-01-01', '2014-12-31', 0), ('SMART', 'massachusetts', '2013-12-31', '2017-01-01', -5),
                      ('Panther', 'ucf', '2015-12-31', '2018-01-01', -5), ('Fox', 'asu', '2015-12-31', '2018-01-01', -7), 
                      ('Bear', 'uc-b', '2015-12-31', '2018-01-01', -8), ('Rat', 'dc', '2015-12-31', '2018-01-01', -5)] 
    
    BDG = {'Panther', 'Fox', 'Bear', 'Rat'}
 
    for ds in real_building_ds:
        print('Downloading', ds[0])

        if ds[0] in BDG:
            output_dir = real_building_prefix / 'BDG-2'
        else:
            output_dir = real_building_prefix / ds[0]

        weather = get_hourly_weather_pandas(ds[2], ds[3], AREA_LONLAT[ds[1]], variable=['2m_temperature','2m_dewpoint_temperature'])

        weather['2m_temperature'] = weather['2m_temperature'].apply(lambda x: x-273.15)
        weather['2m_dewpoint_temperature'] = weather['2m_dewpoint_temperature'].apply(lambda x: x-273.15)

        weather['humidity'] = weather.apply(lambda x: calc_relative_humidity(x['2m_temperature'], x['2m_dewpoint_temperature']), axis=1)
        weather.drop(columns=['2m_dewpoint_temperature'], inplace=True)
        weather.rename(columns={'2m_temperature' : 'temperature'}, inplace=True)

        weather.index.rename('timestamp', inplace=True)
        weather.index = weather.index + pd.to_timedelta(f'{ds[4]}h')

        if ds[0] in BDG:
            weather.to_csv(output_dir / f'weather_{ds[0]}_era5.csv')
        else:
            weather.to_csv(output_dir / 'weather_era5.csv')


   
if __name__ == '__main__':
    main()
