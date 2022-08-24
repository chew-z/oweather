#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
Yet another weather forecast for your terminal.

usage: python3 oweather.py [-h] [-c CITY] [-w] [-v]

Get weather from OpenWeather.

optional arguments:
  -h, --help            show this help message and exit
  -c CITY, --city CITY  Forecast location (default: Warsaw,PL)
  -w, --weekly          Weekly forecast (default: False)
  -v, --verbose         Some additional useless info like Beaufort scale etc.
                        (default: False)

Get API Key for yourself at https://openweathermap.org/api

Make and alias for your shell:
alias weather='python3 /path/to/oweather.py'

Try --weekly and --verbose commandline switches
'''
import time
import argparse
import logging
import requests
import json
import math
from tabulate import tabulate
import datetime as dt
import ephem
import emoji

weather_uri = "http://api.openweathermap.org/data/2.5/"
openweather_api_key = 'YOUR API KEY'


def icon(conditions):
    cond = conditions.lower()

    if 'overcast' in cond:
        return ':cloud:'

    if 'clouds' in cond:
        return ':sunflower:'

    if 'snow' in cond or 'sleet' in cond or 'hail' in cond:
        return ':snowman:'

    if 'rain' in cond or 'storm' in cond:
        return ':umbrella:'

    if 'clear' in cond or 'sun' in cond:
        return ':sun_with_face:'

    return ':earth_africa:'


def degrees_to_cardinal(d):
    '''
    note: this is approximate...
    '''
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    if d is None:
        return None
    # ix = int((d + 11.25)/22.5)
    ix = int((d + 11.25) / 22.5 - 0.02)
    return dirs[ix % 16]


def wind_kn(ms):
    "Convert wind from metres per second to knots"
    if ms is None:
        return None
    return ms * 3.6 / 1.852


def wind_bft(ms):
    "Convert wind from metres per second to Beaufort scale"
    _bft_threshold = (0.3, 1.5, 3.4, 5.4, 7.9, 10.7, 13.8, 17.1, 20.7, 24.4, 28.4, 32.6)

    if ms is None:
        return None
    for bft in range(len(_bft_threshold)):
        if ms < _bft_threshold[bft]:
            return bft
    return len(_bft_threshold)


def beaufort(b, label):
    _beaufort_sea = (
        'Sea like a mirror',
        'Ripples with the appearance of scales are formed, but without foam crests',
        'Small wavelets, still short, but more pronounced. Crests have a glassy appearance and do '
        'not break',
        'Large wavelets. Crests begin to break. Foam of glassy appearance. Perhaps scattered white '
        'horses',
        'Small waves, becoming larger; fairly frequent white horses',
        'Moderate waves, taking a more pronounced long form; many white horses are formed.'
        'Chance of some spray',
        'Large waves begin to form; the white foam crests are more extensive everywhere. '
        'Probably some spray',
        'Sea heaps up and white foam from breaking waves begins to be blown in streaks along the '
        'direction of the wind',
        'Moderately high waves of greater length; edges of crests begin to break into spindrift. '
        'The foam is blown in well-marked streaks along the direction of the wind',
        'High waves. Dense streaks of foam along the direction of the wind. Crests of waves begin '
        'to topple, tumble and roll over. Spray may affect visibility',
        'Very high waves with long over-hanging crests. The resulting foam, in great patches, '
        'is blown in dense white streaks along the direction of the wind. On the whole the surface '
        'of the sea takes on a white appearance. The tumbling of the sea becomes heavy and '
        'shock-like. Visibility affected',
        'Exceptionally high waves (small and medium-size ships might disappear behind the waves). '
        'The sea is completely covered with long white patches of foam flying along the direction '
        'of the wind. Everywhere the edges of the wave crests are blown into froth. Visibility '
        'affected',
        'The air is filled with foam and spray. Sea completely white with driving spray; '
        'visibility very seriously affected'
    )
    _beaufort_land = (
        'Calm. Smoke rises vertically',
        'Wind motion visible in smoke',
        'Wind felt on exposed skin. Leaves rustle',
        'Leaves and smaller twigs in constant motion',
        'Dust and loose paper raised. Small branches begin to move',
        'Branches of a moderate size move. Small trees begin to sway',
        'Large branches in motion. Whistling heard in overhead wires. Umbrella use becomes '
        'difficult. Empty plastic garbage cans tip over',
        'Whole trees in motion. Effort needed to walk against the wind. Swaying of skyscrapers '
        'may be felt, especially by people on upper floors',
        'Twigs broken from trees. Cars veer on road',
        'Larger branches break off trees, and some small trees blow over. Construction/temporary '
        'signs and barricades blow over. Damage to circus tents and canopies',
        'Trees are broken off or uprooted, saplings bent and deformed, poorly attached asphalt '
        'shingles and shingles in poor condition peel off roofs',
        'Widespread vegetation damage. More damage to most roofing surfaces, asphalt tiles that '
        'have curled up and/or fractured due to age may break away completely',
        'Considerable and widespread damage to vegetation, a few windows broken, structural damage '
        'to mobile homes and poorly constructed sheds and barns. Debris may be hurled about'
    )
    _beaufort_label = (
        'Calm',
        'Light Air',
        'Light Breeze',
        'Gentle Breeze',
        'Moderate Breeze',
        'Fresh Breeze',
        'Strong Breeze',
        'Near Gale',
        'Gale',
        'Severe Gale',
        'Storm',
        'Violent Storm',
        'Hurricane'
    )

    if label == 'sea':
        return _beaufort_sea[b]
    elif label == 'land':
        return _beaufort_land[b]
    else:
        return _beaufort_label[b]


def dew_point(temp, hum):
    """Compute dew point, using formula from
    http://en.wikipedia.org/wiki/Dew_point.

    """
    if temp is None or hum is None:
        return None
    a = 17.27
    b = 237.7
    gamma = ((a * temp) / (b + temp)) + math.log(float(hum) / 100.0)
    return (b * gamma) / (a - gamma) - 273.15


def moon_phase(year=None, month=None, day=None):

    if year is None and month is None and day is None:
        today = dt.datetime.now()
        year, month, day = today.year, today.month, today.day
        date = ephem.Date(dt.date(year, month, day))

    nnm = ephem.next_new_moon(date)
    pnm = ephem.previous_new_moon(date)

    lunation = (date - pnm) / (nnm - pnm)
    p = lunation * 29.530588853

    if p < 1.84566:
        # return 'New moon ' + u"🌑"    # new
        return emoji.emojize('New moon :new_moon:')
    elif p < 5.53699:
        # return 'Waxing crescent moon ' + u"🌒"    # waxing crescent
        return emoji.emojize('Waxing crescent moon :waxing_crescent_moon:')
    elif p < 9.22831:
        # return 'First quarter ' + u"🌓"    # first quarter
        return emoji.emojize('First quarter :first_quarter_moon:')
    elif p < 12.91963:
        # return 'Waxing gibbous moon ' + u"🌔"    # waxing gibbous
        return emoji.emojize('Waxing gibbous moon :waxing_gibbous_moon:') # waxing gibbous
    elif p < 16.61096:
        # return 'Full moon ' + u"🌕"    # full
        return emoji.emojize('Full moon :full_moon:')
    elif p < 20.30228:
        # return 'Waxing gibbbous moon ' + u"🌖"    # waning gibbous
        return emoji.emojize('Waxing gibbbous moon :waning_gibbous_moon:')
    elif p < 23.99361:
        # return 'Last quarter ' + u"🌗"    # last quarter
        return emoji.emojize('Last quarter :last_quarter_moon:')
    elif p < 27.68493:
        # return 'Waning crescent moon ' + u"🌘"    # waning crescent
        return emoji.emojize('Waning crescent moon :waning_crescent_moon:')
    else:
        # return 'New moon ' + u"🌑"    # new
        return emoji.emojize('New moon :new_moon:')


def getArgs(argv=None):
    '''
    Command line arguments...
    '''
    parser = argparse.ArgumentParser(
        description='Get weather from OpenWeather.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-c', '--city', default='Derlacz,PL', help='Forecast location')
    parser.add_argument('-w', '--weekly', default=False, action="store_true", help='Weekly forecast')
    parser.add_argument(
        '-v',
        '--verbose',
        default=False,
        action="store_true",
        help='Some additional useless info like Beaufort scale etc.'
    )
    return parser.parse_args(argv)


def dailyForecast(city):
    '''
    print weather as it is now..
    '''
    request_uri = weather_uri + 'weather?q=' + city + '&appid=' + openweather_api_key
    if verbose:
        print(request_uri)
    response = requests.get(request_uri)
    open_weather_json = json.loads(response.text)

    print("==============================================================")
    print(
        '\x1b[6;30;42m' + 'City:',
        open_weather_json['name'],
        open_weather_json['sys']['country'],
        '[',
        open_weather_json['coord']['lat'],
        " / ",
        open_weather_json['coord']['lon'],
        ']' + '\x1b[0m'
    )
    print(
        '[ Sunrise:',
        time.strftime('%H:%M',
                      time.localtime(open_weather_json['sys']['sunrise'])),
        '/ Sunset:',
        time.strftime('%H:%M',
                      time.localtime(open_weather_json['sys']['sunset'])),
        ']'
    )
    print(moon_phase())
    print('')
    weather = str(open_weather_json['weather'][0]['description'])
    print('Weather:', emoji.emojize(icon(weather), use_aliases=True), weather)
    # , '\x1b[0m')
    print('  Temp:', '{:02.1f}'.format(open_weather_json['main']['temp'] - 273.15) + u"\u00B0" + 'C')
    if verbose:
        print(
            "  High:",
            '{:02.1f}'.format(open_weather_json['main']['temp_max'] - 273.15),
            "C",
            "  Low:",
            '{:02.1f}'.format(open_weather_json['main']['temp_min'] - 273.15),
            "C"
        )
    print('  Humidity [%]:', open_weather_json['main']['humidity'])
    print('  Pressure [hPa]:', '{:02.1f}'.format(open_weather_json['main']['pressure']))
    if 'deg' in open_weather_json['wind']:
        deg = int(open_weather_json['wind']['deg'])
    else:
        deg = None
    speed = float(open_weather_json['wind']['speed'])
    print('  Wind [m/s]:', '{:03.1f}'.format(speed), degrees_to_cardinal(deg))
    if verbose:
        print('  Wind [land]: ' + str(wind_bft(speed)) + 'B', beaufort(int(wind_bft(speed)), 'land'))
        print('  Wind [sea]: ' + str(wind_bft(speed)) + 'B', beaufort(int(wind_bft(speed)), 'sea'))
        print(
            '  Wind: ' + '{:03.1f}'.format(wind_kn(speed)),
            'knots from',
            '{:03.0f}'.format(open_weather_json['wind']['deg']) + u"\u00B0" + '/',
            beaufort(int(wind_bft(speed)),
                     'label')
        )
        print('  Clouds [%]: ', open_weather_json['clouds']['all'])
        print(
            '  Dew point:',
            '{:02.1f}'.format(dew_point(open_weather_json['main']['temp'],
                                        open_weather_json['main']['humidity'])) + u"\u00B0" + 'C'
        )

    print("  Time:", time.strftime('%H:%M (%z)', time.localtime(open_weather_json['dt'])))
    print("==============================================================")


def weeklyForecast(city):
    '''
    print weekly forecast
    '''
    request_uri = weather_uri + 'forecast?q=' + city + '&appid=' + openweather_api_key
    # print (request_uri)
    response = requests.get(request_uri)
    open_weather_json = json.loads(response.text)

    print("==============================================================")
    print(
        '\x1b[6;30;42m' + 'City:',
        open_weather_json['city']['name'],
        open_weather_json['city']['country'],
        '  [',
        open_weather_json['city']['coord']['lat'],
        ' / ',
        open_weather_json['city']['coord']['lon'],
        ' ]' + '\x1b[0m'
    )
    print("")
    print('\x1b[6;30;42m' + 'Weekly forecast:' + '\x1b[0m')
    table = []
    for item in open_weather_json['list']:
        weather = str(item['weather'][0]['description'])
        table.append(
            [
                time.strftime('%a %H:%M',
                              time.localtime(item['dt'])),
                '{:02.1f}'.format(item['main']['temp'] - 273.15),
                '{:02.1f}'.format(item['main']['pressure']),
                item['main']['humidity'],
                '{:03.0f}'.format(item['wind']['speed']) + ' ' + degrees_to_cardinal(int(item['wind']['deg'])),
        # item['weather'][0]['description']])
                emoji.emojize(icon(weather)) + ' ' + weather + '\x1b[0m'
            ]
        )
    headers = ['Date', 'Temp', 'Pressure', 'Humidity', 'Wind', 'Description']
    print(tabulate(table, headers, tablefmt="simple"))
    print("==============================================================")


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        filename='/tmp/weather.log',
        level=logging.DEBUG,
        format=FORMAT,
        datefmt='%a, %d %b %Y %H:%M:%S',
    )
    logging.info('--- oweather.py logging started ---.')

    args = getArgs()
    city = args.city
    weekly = args.weekly
    verbose = args.verbose
    if weekly:
        weeklyForecast(city)
    else:
        dailyForecast(city)
