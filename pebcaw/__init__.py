#!/usr/bin/env python

"""
################################################################################
#                                                                              #
# PEBCAW                                                                       #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program monitors internet connection security by comparing the observed #
# IP address with a whitelist of VPN and Tor IP addresses.                     #
#                                                                              #
# copyright (C) 2018 Will Breaden Madden, wbm@protonmail.ch                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################

usage:
    program [options]

options:
    -h, --help                  display help message
    --version                   display version and exit
    --interval=INT              observation interval (s) [default: 300]
    --warn_SIGINT_country       warn if IP in SIGINT country
    --display                   display IP details continuously
    --restart_regularly         restart program regularly
    --countries_whitelist=TEXT  comma-separated whitelist of two-letter country codes (e.g. CH)
"""

import docopt
import os
import requests
import shutil
import subprocess
import sys
import textwrap
import time

import shijian

name        = 'PEBCAW'
__version__ = '2020-02-18T0012Z'

def main():
    options             = docopt.docopt(__doc__, version=__version__)
    interval            = int(options['--interval'])
    warn_SIGINT_country =     options['--warn_SIGINT_country']
    display             =     options['--display']
    restart_regularly   =     options['--restart_regularly']
    countries_whitelist =     options['--countries_whitelist']
    if countries_whitelist:
        countries_whitelist = countries_whitelist.split(',')
    message             = name + ' ' + __version__ + ' monitoring internet connection security'
    print('\n' + message + '\n^c to stop\n')
    notify(text=message)
    clock_restart = shijian.Clock(name='restart')
    while True:
        try:
            data_IP      = requests.get('http://ipinfo.io/json').json()
            IP           = data_IP['ip']
            organisation = data_IP['org']
            coordinates  = data_IP['loc']
            city         = data_IP['city']
            country      = data_IP['country']
            region       = data_IP['region']
            if not countries_whitelist:
                if IP not in whitelist_IPs + whitelist_Tor:
                    notify(
                        text    = 'WARNING: IP not identified as AirVPN or Tor',
                        subtext = 'IP: ' + IP
                    )
                if warn_SIGINT_country and country in countries_SIGINT:
                    notify(
                        text    = 'WARNING: IP in SIGINT country',
                        subtext = 'IP: ' + IP
                    )
            else:
                if country not in countries_whitelist:
                    notify(text=f'WARNING: country {country} not in whitelist {countries_whitelist}')
            if display:
                text = textwrap.dedent(
                    """
                    IP:           {IP}
                    organisation: {organisation}
                    coordinates:  {coordinates}
                    city:         {city}
                    country:      {country}
                    region:       {region}
                    """.format(
                        IP           = IP           if IP           else 'unknown',
                        organisation = organisation if organisation else 'unknown',
                        coordinates  = coordinates  if coordinates  else 'unknown',
                        city         = city         if city         else 'unknown',
                        country      = country      if country      else 'unknown',
                        region       = region       if region       else 'unknown'
                    )
                )
                print(chr(27) + '[2J')
                print(text)
        except:
            notify(text='WARNING: error observing IP, unable to identify as secure')
        if restart_regularly and clock_restart.time() >= 500:
            print('regular restart procedure engaged')
            restart()
        time.sleep(interval)

def notify(
    text    = None,
    subtext = None,
    icon    = None
    ):
    try:
        if text and shutil.which('notify-send'):
            command = 'notify-send \"{text}\"'
            if subtext:
                command = command + ' \"{subtext}\"'
            if icon and os.path.isfile(os.path.expandvars(icon)):
                command = command + ' --icon={icon}'
            command = command + ' --urgency=critical'
            command = command.format(
                text    = text,
                subtext = subtext,
                icon    = icon
            )
            engage_command(command)
    except:
        pass

def engage_command(
    command    = None,
    background = True,
    timeout    = None
    ):
    if background:
        subprocess.Popen(
            [command],
            shell      = True,
            executable = '/bin/bash'
        )
        return None
    elif not background:
        process = subprocess.Popen(
            [command],
            shell      = True,
            executable = '/bin/bash',
            stdout     = subprocess.PIPE
        )
        try:
            process.wait(timeout=timeout)
            output, errors = process.communicate(timeout=timeout)
            return output
        except:
            process.kill()
            return False
    else:
        return None

def restart():
    import __main__
    os.execv(__main__.__file__, sys.argv)

countries_SIGINT = [
    'AU', 'Australia',
    'BE', 'Belgium',
    'CA', 'Canada',
    'DK', 'Denmark',
    'DE', 'Germany',
    'FR', 'France',
    'GB', 'UK', 'United Kingdom',
    'NL', 'Netherlands',
    'IT', 'Italy',
    'NO', 'Norway',
    'NZ', 'New Zealand',
    'ES', 'Spain',
    'SE', 'Sweden',
    'US', 'USA', 'United States', 'United States of America',
]
IPs_AirVPN_2018_10_11 = [
    '109.202.107.10',
    '213.152.161.69',
    '213.152.161.181',
    '213.152.161.244',
    '213.152.162.99'
]
IPs_AirVPN_2017_02_21 = [
    '185.9.19.106',
    '217.64.127.194',
    '194.187.251.90',
    '194.187.251.114',
    '194.187.251.162',
    '194.187.251.154',
    '184.75.223.210',
    '162.219.176.2',
    '184.75.221.202',
    '199.19.94.12',
    '104.254.90.202',
    '184.75.221.114',
    '184.75.221.170',
    '184.75.221.162',
    '184.75.221.210',
    '184.75.223.234',
    '184.75.214.162',
    '104.254.90.234',
    '199.21.149.44',
    '104.254.90.242',
    '104.254.90.250',
    '199.19.95.187',
    '199.19.94.61',
    '184.75.221.2',
    '184.75.223.218',
    '199.19.94.132',
    '184.75.221.34',
    '104.254.90.186',
    '184.75.221.178',
    '184.75.223.226',
    '184.75.223.194',
    '104.254.90.194',
    '199.19.94.19',
    '184.75.221.42',
    '137.63.71.50',
    '184.75.221.194',
    '184.75.223.202',
    '184.75.221.58',
    '71.19.252.21',
    '71.19.252.113',
    '71.19.252.26',
    '71.19.252.31',
    '71.19.251.247',
    '46.19.137.114',
    '185.156.175.170',
    '185.156.175.34',
    '185.156.175.50',
    '185.156.175.42',
    '91.214.169.68',
    '185.156.175.58',
    '185.156.174.114',
    '185.156.174.26',
    '185.156.174.154',
    '89.238.166.234',
    '185.104.184.42',
    '46.165.208.70',
    '178.162.198.40',
    '178.162.198.103',
    '46.165.208.65',
    '46.165.208.69',
    '178.162.198.102',
    '79.143.191.166',
    '185.183.106.2',
    '185.93.182.170',
    '95.215.62.91',
    '80.84.49.4',
    '217.151.98.162',
    '217.151.98.167',
    '88.150.240.7',
    '185.103.96.132',
    '185.103.96.134',
    '94.229.74.90',
    '185.103.96.133',
    '185.103.96.131',
    '185.103.96.130',
    '89.249.74.212',
    '89.249.74.217',
    '82.145.37.202',
    '84.39.117.56',
    '84.39.116.179',
    '78.129.153.40',
    '103.16.27.90',
    '103.16.27.80',
    '103.16.27.25',
    '103.10.197.186',
    '103.16.27.85',
    '103.16.27.74',
    '46.166.165.124',
    '93.115.29.23',
    '93.115.29.33',
    '159.148.186.16',
    '159.148.186.17',
    '159.148.186.24',
    '159.148.186.31',
    '213.152.161.180',
    '213.152.161.116',
    '109.202.107.9',
    '109.202.107.4',
    '109.202.107.146',
    '213.152.162.78',
    '213.152.161.4',
    '213.152.161.169',
    '109.202.107.14',
    '213.152.162.164',
    '109.202.103.169',
    '109.202.107.19',
    '213.152.161.9',
    '213.152.162.169',
    '213.152.161.68',
    '109.232.227.132',
    '213.152.161.164',
    '213.152.180.4',
    '213.152.162.73',
    '213.152.161.100',
    '213.152.162.93',
    '213.152.161.39',
    '213.152.161.34',
    '213.152.162.108',
    '213.152.161.84',
    '213.152.162.180',
    '213.152.162.103',
    '109.232.227.137',
    '213.152.161.29',
    '213.152.162.68',
    '213.152.162.88',
    '213.152.162.153',
    '213.152.161.24',
    '109.232.227.148',
    '213.152.162.148',
    '213.152.162.83',
    '213.152.161.19',
    '213.152.162.113',
    '213.152.161.14',
    '213.152.161.73',
    '213.152.162.98',
    '213.152.161.137',
    '213.152.161.132',
    '213.152.161.148',
    '91.207.102.162',
    '109.163.230.232',
    '185.57.80.146',
    '62.102.148.149',
    '62.102.148.142',
    '62.102.148.147',
    '62.102.148.145',
    '62.102.148.140',
    '62.102.148.151',
    '62.102.148.150',
    '62.102.148.141',
    '62.102.148.148',
    '62.102.148.137',
    '62.102.148.132',
    '62.102.148.144',
    '62.102.148.143',
    '62.102.148.146',
    '62.102.148.134',
    '62.102.148.139',
    '62.102.148.136',
    '103.254.153.68',
    '91.231.84.39',
    '104.129.24.178',
    '104.129.24.186',
    '104.129.24.154',
    '46.21.154.82',
    '198.98.113.154',
    '173.234.62.154',
    '23.88.99.194',
    '149.255.33.154',
    '23.88.114.50',
    '107.183.238.178',
    '107.183.238.194',
    '23.88.114.42',
    '64.120.63.90',
    '107.183.238.186',
    '69.162.81.226',
    '46.21.151.106',
    '94.100.23.162',
    '198.203.28.42',
    '199.241.146.178',
    '199.241.146.162',
    '199.241.147.34',
    '173.44.55.154',
    '96.47.229.58',
    '173.44.55.178',
    '173.234.159.194',
    '64.120.44.138',
    '104.243.24.235'
]
IPs_Tor_2017_02_21 = [
    '103.10.197.50',
    '103.199.16.58',
    '103.234.220.197',
    '103.236.201.110',
    '103.27.124.82',
    '103.29.70.23',
    '103.3.61.114',
    '103.56.207.84',
    '103.8.79.229',
    '104.167.116.234',
    '104.200.20.46',
    '104.206.237.21',
    '104.206.237.22',
    '104.233.105.168',
    '104.233.83.9',
    '104.236.141.156',
    '105.155.140.249',
    '106.187.37.101',
    '107.181.174.84',
    '107.191.56.192',
    '108.175.11.230',
    '108.51.26.141',
    '108.61.122.88',
    '108.61.197.189',
    '108.85.99.10',
    '109.108.3.87',
    '109.126.9.228',
    '109.128.134.225',
    '109.163.234.2',
    '109.163.234.4',
    '109.163.234.5',
    '109.163.234.7',
    '109.163.234.8',
    '109.163.234.9',
    '109.169.33.163',
    '109.173.57.54',
    '109.190.182.44',
    '109.191.34.208',
    '109.191.40.25',
    '109.191.41.151',
    '109.191.46.192',
    '109.191.50.252',
    '109.191.51.193',
    '109.191.57.65',
    '109.191.58.45',
    '109.191.60.182',
    '109.201.133.100',
    '109.62.243.61',
    '109.63.235.182',
    '111.248.57.152',
    '114.45.114.141',
    '115.186.243.60',
    '115.70.208.17',
    '117.201.240.2',
    '118.163.74.160',
    '118.163.74.161',
    '120.29.217.46',
    '120.56.160.66',
    '120.56.162.117',
    '120.56.166.126',
    '120.56.166.255',
    '120.56.167.48',
    '120.56.170.131',
    '120.56.170.99',
    '120.56.174.51',
    '120.56.175.18',
    '121.127.250.156',
    '121.54.175.50',
    '124.109.1.207',
    '125.212.241.182',
    '128.153.146.125',
    '128.199.195.117',
    '128.199.47.160',
    '128.52.128.105',
    '130.204.161.3',
    '137.74.167.161',
    '137.74.167.224',
    '137.74.167.96',
    '137.74.169.241',
    '138.197.207.243',
    '138.219.43.141',
    '139.162.10.72',
    '139.162.144.133',
    '139.162.16.13',
    '139.162.226.245',
    '139.162.28.23',
    '139.162.28.31',
    '139.162.57.167',
    '14.202.230.49',
    '141.138.141.208',
    '141.170.2.53',
    '141.255.189.161',
    '141.69.205.121',
    '144.217.161.119',
    '144.217.99.46',
    '146.0.79.144',
    '146.0.79.243',
    '146.115.145.143',
    '146.185.163.44',
    '146.185.177.103',
    '149.202.59.131',
    '149.202.63.214',
    '149.202.98.160',
    '149.202.98.161',
    '149.56.204.218',
    '149.56.223.241',
    '149.56.229.16',
    '149.56.229.17',
    '150.107.150.101',
    '150.107.150.102',
    '151.20.250.122',
    '151.45.101.115',
    '151.45.116.177',
    '151.45.218.47',
    '151.45.221.219',
    '151.50.126.219',
    '151.56.187.133',
    '151.80.136.16',
    '151.80.238.152',
    '151.80.38.67',
    '153.127.199.124',
    '154.127.60.154',
    '154.127.60.92',
    '154.127.61.134',
    '154.127.61.249',
    '154.70.153.175',
    '155.133.82.112',
    '155.4.212.181',
    '158.130.0.242',
    '158.193.153.6',
    '158.255.5.117',
    '158.255.5.180',
    '158.255.5.181',
    '158.255.5.206',
    '158.255.5.207',
    '158.69.36.131',
    '162.213.3.221',
    '162.221.201.57',
    '162.243.166.137',
    '162.243.75.204',
    '162.244.26.76',
    '162.247.72.199',
    '162.247.72.200',
    '162.247.72.201',
    '162.247.72.202',
    '162.247.72.213',
    '162.247.72.216',
    '162.247.72.217',
    '162.247.72.27',
    '162.247.72.7',
    '162.247.73.204',
    '162.247.73.206',
    '162.247.73.74',
    '162.248.10.132',
    '162.248.11.176',
    '163.172.134.238',
    '163.172.134.39',
    '163.172.136.101',
    '163.172.142.15',
    '163.172.151.47',
    '163.172.160.182',
    '163.172.170.212',
    '163.172.190.34',
    '163.172.217.50',
    '163.172.221.209',
    '163.172.223.200',
    '163.172.35.247',
    '163.172.35.249',
    '163.172.67.180',
    '164.132.51.91',
    '164.70.1.193',
    '164.77.133.220',
    '165.231.0.242',
    '165.255.184.131',
    '165.255.186.154',
    '165.255.216.245',
    '166.70.15.14',
    '166.70.207.2',
    '167.114.230.104',
    '167.114.34.150',
    '168.1.75.41',
    '168.235.153.203',
    '171.25.193.131',
    '171.25.193.132',
    '171.25.193.20',
    '171.25.193.235',
    '171.25.193.25',
    '171.25.193.77',
    '171.25.193.78',
    '172.111.204.41',
    '172.94.100.173',
    '172.94.14.219',
    '173.14.173.227',
    '173.208.213.114',
    '173.254.216.66',
    '173.255.226.142',
    '173.255.231.125',
    '173.79.162.220',
    '176.10.104.240',
    '176.10.104.243',
    '176.10.107.180',
    '176.10.99.200',
    '176.10.99.201',
    '176.10.99.202',
    '176.10.99.203',
    '176.10.99.204',
    '176.10.99.205',
    '176.10.99.206',
    '176.10.99.207',
    '176.10.99.208',
    '176.10.99.209',
    '176.115.43.201',
    '176.115.51.75',
    '176.115.58.184',
    '176.115.63.186',
    '176.122.118.238',
    '176.126.252.11',
    '176.126.252.12',
    '176.136.25.17',
    '176.145.182.43',
    '176.194.104.70',
    '176.194.140.70',
    '176.194.170.57',
    '176.214.53.133',
    '176.31.180.157',
    '176.31.215.157',
    '176.31.45.3',
    '176.38.163.77',
    '176.58.100.98',
    '176.58.89.182',
    '177.204.185.97',
    '177.205.154.57',
    '177.205.180.61',
    '177.205.29.126',
    '178.17.170.135',
    '178.17.170.164',
    '178.17.170.179',
    '178.17.170.195',
    '178.17.170.27',
    '178.17.171.40',
    '178.17.171.43',
    '178.17.171.93',
    '178.17.174.10',
    '178.17.174.32',
    '178.175.128.50',
    '178.175.131.194',
    '178.18.83.215',
    '178.20.55.16',
    '178.20.55.18',
    '178.200.157.173',
    '178.208.101.221',
    '178.217.187.39',
    '178.238.237.44',
    '178.32.181.97',
    '178.32.181.98',
    '178.32.181.99',
    '178.32.53.94',
    '178.62.17.15',
    '178.62.217.233',
    '178.63.110.151',
    '179.182.149.162',
    '179.43.151.226',
    '18.248.1.85',
    '185.10.68.119',
    '185.10.68.95',
    '185.100.84.108',
    '185.100.84.82',
    '185.100.85.101',
    '185.100.85.147',
    '185.100.85.190',
    '185.100.85.192',
    '185.100.85.220',
    '185.100.85.61',
    '185.100.86.100',
    '185.100.86.128',
    '185.100.86.154',
    '185.100.86.244',
    '185.100.86.69',
    '185.100.86.86',
    '185.100.87.143',
    '185.100.87.186',
    '185.100.87.192',
    '185.100.87.241',
    '185.100.87.82',
    '185.101.156.141',
    '185.103.99.60',
    '185.104.120.2',
    '185.104.120.3',
    '185.104.120.4',
    '185.109.146.62',
    '185.11.180.67',
    '185.112.157.135',
    '185.113.128.79',
    '185.117.215.9',
    '185.117.82.132',
    '185.118.251.20',
    '185.12.45.79',
    '185.120.147.171',
    '185.121.168.254',
    '185.129.62.62',
    '185.135.156.94',
    '185.14.30.238',
    '185.141.164.52',
    '185.143.240.40',
    '185.145.128.149',
    '185.145.129.197',
    '185.146.168.19',
    '185.16.200.176',
    '185.165.168.123',
    '185.165.168.196',
    '185.165.168.206',
    '185.181.101.81',
    '185.188.204.9',
    '185.24.233.74',
    '185.25.50.103',
    '185.25.50.17',
    '185.25.51.33',
    '185.25.51.42',
    '185.29.8.132',
    '185.29.8.211',
    '185.30.238.77',
    '185.31.161.102',
    '185.31.172.234',
    '185.34.33.2',
    '185.38.14.171',
    '185.38.14.215',
    '185.47.63.74',
    '185.61.149.193',
    '185.65.200.93',
    '185.65.205.10',
    '185.66.200.10',
    '185.7.152.104',
    '185.72.244.24',
    '185.73.44.54',
    '185.82.216.233',
    '185.87.185.45',
    '186.149.249.18',
    '186.206.214.154',
    '187.104.60.81',
    '188.126.81.155',
    '188.143.29.177',
    '188.165.106.249',
    '188.213.165.101',
    '188.235.17.15',
    '188.65.144.2',
    '189.84.21.44',
    '190.10.8.50',
    '190.114.246.77',
    '190.210.182.173',
    '190.210.98.90',
    '190.216.2.136',
    '191.250.139.165',
    '191.250.250.141',
    '191.32.200.66',
    '191.34.17.115',
    '191.34.196.192',
    '191.34.5.116',
    '192.160.102.164',
    '192.160.102.166',
    '192.166.218.63',
    '192.195.80.10',
    '192.241.160.32',
    '192.34.80.176',
    '192.36.27.4',
    '192.36.27.6',
    '192.36.27.7',
    '192.42.116.16',
    '192.81.131.49',
    '192.99.54.79',
    '193.107.85.56',
    '193.107.85.57',
    '193.107.85.62',
    '193.110.157.151',
    '193.15.16.4',
    '193.150.121.78',
    '193.169.135.133',
    '193.171.202.150',
    '193.90.12.86',
    '193.90.12.87',
    '193.90.12.88',
    '193.90.12.89',
    '193.90.12.90',
    '194.15.115.35',
    '194.218.3.79',
    '195.123.210.95',
    '195.154.122.54',
    '195.154.161.35',
    '195.154.161.47',
    '195.154.91.194',
    '195.178.166.72',
    '195.228.45.176',
    '195.254.135.76',
    '196.65.22.208',
    '197.231.221.211',
    '198.100.148.112',
    '198.100.159.72',
    '198.143.136.228',
    '198.167.223.33',
    '198.167.223.38',
    '198.199.111.159',
    '198.211.122.191',
    '198.50.138.50',
    '198.50.159.155',
    '198.50.200.134',
    '198.50.200.135',
    '198.50.245.82',
    '198.58.100.240',
    '198.58.107.53',
    '198.73.50.71',
    '198.96.155.3',
    '199.127.226.150',
    '199.249.223.60',
    '199.249.223.61',
    '199.249.223.62',
    '199.249.223.63',
    '199.249.223.64',
    '199.249.223.65',
    '199.249.223.66',
    '199.249.223.67',
    '199.249.223.68',
    '199.249.223.69',
    '199.249.223.71',
    '199.249.223.72',
    '199.249.223.73',
    '199.249.223.74',
    '199.249.223.75',
    '199.249.223.76',
    '199.249.223.77',
    '199.249.223.78',
    '199.249.223.79',
    '199.249.223.81',
    '199.254.238.44',
    '199.68.196.123',
    '199.68.196.124',
    '199.68.196.125',
    '199.68.196.126',
    '199.87.154.255',
    '201.68.215.52',
    '203.217.173.146',
    '204.11.50.131',
    '204.17.56.42',
    '204.194.29.4',
    '204.27.60.147',
    '204.8.156.142',
    '204.85.191.30',
    '205.168.84.133',
    '205.185.115.60',
    '206.248.184.127',
    '207.154.218.90',
    '207.244.70.35',
    '208.113.166.5',
    '209.123.234.23',
    '209.133.66.214',
    '209.159.137.156',
    '209.222.77.220',
    '209.249.157.69',
    '209.249.180.198',
    '209.66.119.150',
    '210.3.102.152',
    '211.125.222.82',
    '212.159.91.21',
    '212.16.104.33',
    '212.19.17.213',
    '212.21.66.6',
    '212.26.245.34',
    '212.47.242.127',
    '212.47.243.140',
    '212.47.246.21',
    '212.47.253.223',
    '212.81.199.159',
    '212.83.40.238',
    '212.83.40.239',
    '212.92.214.246',
    '212.92.219.15',
    '213.108.105.71',
    '213.161.5.12',
    '213.183.56.93',
    '213.252.244.105',
    '213.32.55.247',
    '213.5.68.196',
    '213.5.68.197',
    '213.5.68.198',
    '213.5.68.199',
    '213.5.68.200',
    '213.5.68.202',
    '213.5.68.203',
    '213.5.68.207',
    '213.61.149.100',
    '213.95.21.54',
    '216.218.134.12',
    '216.218.222.10',
    '216.218.222.12',
    '216.218.222.13',
    '216.230.148.77',
    '216.239.90.19',
    '217.115.10.131',
    '217.115.10.132',
    '217.13.197.5',
    '217.170.201.106',
    '217.211.89.66',
    '217.240.65.160',
    '217.25.160.139',
    '217.25.163.186',
    '217.25.168.7',
    '217.25.171.78',
    '217.25.173.151',
    '217.70.191.13',
    '219.104.92.216',
    '220.129.65.88',
    '223.26.48.248',
    '23.92.27.23',
    '23.92.28.23',
    '24.207.212.154',
    '31.16.244.16',
    '31.16.89.170',
    '31.172.137.19',
    '31.185.104.19',
    '31.185.104.20',
    '31.185.104.21',
    '31.185.27.1',
    '31.19.158.111',
    '31.24.148.37',
    '31.31.74.69',
    '31.34.241.90',
    '31.40.42.31',
    '31.41.219.228',
    '37.123.133.148',
    '37.130.227.133',
    '37.139.8.104',
    '37.187.129.166',
    '37.187.155.239',
    '37.187.7.74',
    '37.218.240.101',
    '37.218.240.21',
    '37.218.240.50',
    '37.218.240.68',
    '37.218.240.80',
    '37.220.35.202',
    '37.220.36.240',
    '37.48.120.196',
    '37.48.120.9',
    '37.59.112.7',
    '37.59.254.9',
    '4.31.64.70',
    '41.182.25.20',
    '41.182.26.202',
    '41.182.27.245',
    '41.182.27.54',
    '41.182.28.154',
    '41.182.29.239',
    '41.182.29.90',
    '41.185.28.214',
    '41.206.188.206',
    '41.208.213.46',
    '41.223.53.141',
    '41.231.53.101',
    '45.33.23.23',
    '45.33.48.204',
    '45.35.72.85',
    '45.62.210.151',
    '45.62.212.227',
    '45.62.246.91',
    '45.62.247.18',
    '45.62.249.18',
    '45.79.207.176',
    '46.101.127.145',
    '46.101.139.248',
    '46.105.100.149',
    '46.148.26.108',
    '46.16.234.131',
    '46.165.223.217',
    '46.165.230.5',
    '46.166.148.142',
    '46.166.148.143',
    '46.166.148.144',
    '46.166.148.145',
    '46.166.148.152',
    '46.166.148.153',
    '46.166.148.154',
    '46.166.148.155',
    '46.166.148.176',
    '46.166.148.177',
    '46.166.173.101',
    '46.182.106.190',
    '46.182.18.214',
    '46.182.19.219',
    '46.183.216.205',
    '46.183.218.199',
    '46.183.221.137',
    '46.183.221.231',
    '46.188.56.132',
    '46.188.56.158',
    '46.188.56.222',
    '46.188.56.65',
    '46.194.144.63',
    '46.194.15.93',
    '46.233.0.70',
    '46.235.227.70',
    '46.246.49.132',
    '46.246.49.159',
    '46.246.49.203',
    '46.246.49.239',
    '46.28.107.82',
    '46.28.68.158',
    '46.29.248.238',
    '46.38.48.12',
    '46.38.56.213',
    '46.4.55.177',
    '46.41.150.74',
    '46.5.40.210',
    '46.72.119.133',
    '46.72.120.15',
    '46.72.120.76',
    '46.72.74.228',
    '46.73.64.90',
    '46.73.69.84',
    '49.135.84.252',
    '5.10.42.187',
    '5.10.46.175',
    '5.135.158.101',
    '5.146.144.232',
    '5.148.165.13',
    '5.189.146.133',
    '5.189.153.91',
    '5.189.188.111',
    '5.196.1.129',
    '5.196.121.161',
    '5.196.66.162',
    '5.199.130.188',
    '5.2.75.199',
    '5.2.75.25',
    '5.228.5.57',
    '5.249.145.164',
    '5.249.149.204',
    '5.34.180.217',
    '5.39.217.14',
    '5.56.32.60',
    '50.247.195.124',
    '50.76.159.218',
    '51.15.1.125',
    '51.15.135.103',
    '51.15.39.2',
    '51.15.40.233',
    '51.15.43.202',
    '51.15.43.205',
    '51.15.44.142',
    '51.15.46.142',
    '51.15.53.118',
    '51.15.53.83',
    '51.15.57.125',
    '51.15.58.152',
    '51.15.60.93',
    '51.15.63.229',
    '51.254.23.203',
    '51.254.48.93',
    '51.255.202.66',
    '51.255.33.0',
    '52.183.40.243',
    '52.184.157.234',
    '59.127.163.155',
    '59.177.65.181',
    '59.177.67.32',
    '59.177.67.67',
    '59.177.70.210',
    '60.248.162.179',
    '61.230.116.135',
    '61.230.167.161',
    '61.231.0.7',
    '61.231.1.40',
    '62.102.148.67',
    '62.12.115.107',
    '62.133.130.105',
    '62.141.35.91',
    '62.141.55.117',
    '62.149.12.153',
    '62.205.133.251',
    '62.210.105.116',
    '62.210.129.246',
    '62.210.245.138',
    '62.210.245.158',
    '62.210.246.163',
    '62.210.254.127',
    '62.210.254.201',
    '62.210.37.82',
    '62.210.69.79',
    '62.210.81.52',
    '62.212.73.141',
    '62.80.200.190',
    '63.223.69.103',
    '63.224.55.73',
    '64.113.32.29',
    '64.124.32.84',
    '64.137.173.118',
    '64.137.178.3',
    '64.137.178.47',
    '64.137.180.197',
    '64.137.184.36',
    '64.137.189.77',
    '64.137.197.197',
    '64.137.198.31',
    '64.137.200.96',
    '64.137.201.90',
    '64.137.208.3',
    '64.137.212.84',
    '64.137.230.99',
    '64.137.231.56',
    '64.137.243.67',
    '64.137.244.96',
    '64.137.245.56',
    '64.137.255.130',
    '64.27.17.140',
    '65.129.152.59',
    '65.129.196.25',
    '65.181.123.254',
    '65.19.167.130',
    '65.19.167.131',
    '65.19.167.132',
    '66.155.4.213',
    '66.180.193.219',
    '66.220.3.179',
    '67.205.146.164',
    '67.215.255.140',
    '68.109.18.141',
    '68.149.248.101',
    '69.162.107.5',
    '69.162.139.9',
    '69.164.207.234',
    '70.164.255.174',
    '71.135.32.197',
    '71.135.32.210',
    '71.135.34.109',
    '71.135.37.238',
    '71.135.38.32',
    '71.135.41.197',
    '71.135.42.238',
    '71.135.42.35',
    '71.135.43.246',
    '71.135.44.147',
    '71.46.220.68',
    '72.12.207.14',
    '72.14.179.10',
    '72.52.75.27',
    '73.225.150.124',
    '74.50.54.69',
    '75.72.74.123',
    '76.85.200.64',
    '77.109.139.87',
    '77.151.20.214',
    '77.153.10.26',
    '77.247.181.163',
    '77.247.181.165',
    '77.27.126.221',
    '77.51.20.37',
    '77.51.67.108',
    '77.81.107.138',
    '77.81.240.41',
    '77.85.191.52',
    '78.107.237.16',
    '78.109.23.1',
    '78.21.52.58',
    '78.31.164.41',
    '78.41.115.145',
    '79.124.59.194',
    '79.134.234.247',
    '79.137.79.31',
    '79.137.81.168',
    '79.137.87.212',
    '79.137.87.213',
    '79.169.34.95',
    '79.172.193.32',
    '79.224.78.208',
    '79.224.79.76',
    '79.224.84.5',
    '79.224.86.115',
    '79.252.221.140',
    '80.15.98.127',
    '80.162.43.72',
    '80.169.241.76',
    '80.240.139.111',
    '80.241.60.207',
    '80.244.81.191',
    '80.67.172.162',
    '80.73.242.142',
    '80.79.23.7',
    '80.85.84.23',
    '81.159.69.44',
    '81.237.215.148',
    '81.240.100.250',
    '81.240.107.196',
    '81.240.108.26',
    '81.240.109.163',
    '81.245.42.66',
    '81.37.224.42',
    '81.89.0.195',
    '81.89.0.196',
    '81.89.0.197',
    '81.89.0.198',
    '81.89.0.199',
    '81.89.0.200',
    '81.89.0.201',
    '81.89.0.202',
    '81.89.0.203',
    '81.89.0.204',
    '82.130.13.154',
    '82.165.142.79',
    '82.196.124.194',
    '82.211.19.143',
    '82.221.128.217',
    '82.221.139.190',
    '82.221.139.25',
    '82.245.109.199',
    '82.247.198.227',
    '82.248.102.124',
    '82.248.35.147',
    '82.249.133.149',
    '82.249.215.231',
    '82.249.217.153',
    '82.250.100.27',
    '82.250.193.133',
    '82.250.3.236',
    '82.250.47.151',
    '82.250.56.13',
    '82.250.88.227',
    '82.71.211.13',
    '83.220.179.175',
    '84.188.74.141',
    '84.19.180.135',
    '84.19.189.242',
    '84.190.176.47',
    '84.190.186.203',
    '84.194.71.213',
    '84.200.50.18',
    '84.200.56.34',
    '84.200.56.36',
    '84.200.82.163',
    '84.3.0.53',
    '84.48.199.78',
    '84.63.49.188',
    '85.131.152.221',
    '85.143.210.233',
    '85.143.219.211',
    '85.195.107.250',
    '85.248.227.163',
    '85.248.227.164',
    '85.248.227.165',
    '85.90.244.23',
    '85.93.218.204',
    '86.134.82.29',
    '86.134.82.98',
    '86.145.75.75',
    '86.145.75.77',
    '86.146.208.28',
    '86.146.213.69',
    '86.148.218.108',
    '86.148.223.142',
    '86.148.223.73',
    '86.148.223.87',
    '86.166.89.22',
    '86.176.199.64',
    '86.180.57.130',
    '86.180.57.180',
    '86.180.57.223',
    '86.246.1.139',
    '86.59.165.99',
    '86.7.140.31',
    '87.118.114.145',
    '87.118.115.176',
    '87.118.116.12',
    '87.118.116.90',
    '87.118.122.201',
    '87.118.122.254',
    '87.118.122.30',
    '87.118.122.50',
    '87.118.122.51',
    '87.118.84.181',
    '87.118.92.43',
    '87.118.94.2',
    '87.180.224.236',
    '87.180.226.238',
    '87.180.227.110',
    '87.180.228.102',
    '87.236.194.113',
    '87.236.194.114',
    '87.236.194.115',
    '87.236.194.116',
    '87.81.148.61',
    '87.98.152.151',
    '87.98.178.61',
    '87.98.250.244',
    '88.188.1.80',
    '88.198.125.96',
    '88.198.56.140',
    '88.76.20.229',
    '88.76.71.212',
    '88.77.203.253',
    '88.77.212.119',
    '88.80.7.5',
    '89.109.226.75',
    '89.140.119.143',
    '89.144.12.15',
    '89.163.224.109',
    '89.187.142.208',
    '89.187.144.122',
    '89.221.210.122',
    '89.223.27.241',
    '89.227.106.165',
    '89.227.126.49',
    '89.227.89.236',
    '89.227.98.31',
    '89.234.157.254',
    '89.236.34.117',
    '89.248.166.157',
    '89.252.2.140',
    '89.31.57.5',
    '89.31.96.168',
    '89.32.127.178',
    '89.34.237.101',
    '89.34.237.192',
    '89.38.208.57',
    '89.45.226.28',
    '89.94.1.179',
    '90.120.135.168',
    '91.107.104.238',
    '91.121.119.122',
    '91.121.77.37',
    '91.134.232.48',
    '91.134.232.49',
    '91.138.20.41',
    '91.146.121.3',
    '91.197.234.102',
    '91.203.5.146',
    '91.213.8.235',
    '91.213.8.236',
    '91.213.8.84',
    '91.219.236.174',
    '91.219.236.218',
    '91.219.236.232',
    '91.219.237.229',
    '91.219.237.244',
    '91.219.237.69',
    '91.220.220.5',
    '91.232.225.43',
    '91.233.106.121',
    '91.64.164.129',
    '92.111.156.14',
    '92.222.103.232',
    '92.222.6.12',
    '92.222.69.25',
    '92.222.74.226',
    '92.222.84.136',
    '92.249.149.95',
    '92.61.66.163',
    '93.115.95.201',
    '93.115.95.202',
    '93.115.95.204',
    '93.115.95.205',
    '93.115.95.206',
    '93.115.95.207',
    '93.115.95.216',
    '93.158.216.52',
    '93.174.93.133',
    '93.184.66.227',
    '93.189.90.244',
    '93.64.207.55',
    '93.65.213.31',
    '93.89.101.27',
    '93.95.100.164',
    '93.95.100.203',
    '93.95.228.80',
    '94.102.60.85',
    '94.142.242.84',
    '94.198.100.17',
    '94.229.144.89',
    '94.229.151.227',
    '94.229.155.254',
    '94.23.173.249',
    '94.23.201.80',
    '94.231.170.190',
    '94.242.246.23',
    '94.242.246.24',
    '94.242.57.161',
    '94.242.57.2',
    '94.26.140.150',
    '94.34.93.176',
    '95.128.43.164',
    '95.130.11.147',
    '95.130.11.170',
    '95.130.12.31',
    '95.140.42.183',
    '95.142.161.63',
    '95.165.148.12',
    '95.181.253.77',
    '95.211.230.94',
    '95.215.44.194',
    '95.215.47.4',
    '95.221.16.179',
    '95.73.225.2',
    '95.79.82.143',
    '95.85.10.71',
    '95.85.61.51',
    '96.35.130.133',
    '96.66.15.147',
    '97.74.237.196',
    '99.122.154.250'
]
whitelist_IPs = IPs_AirVPN_2018_10_11 + IPs_AirVPN_2017_02_21
whitelist_Tor = IPs_Tor_2017_02_21

if __name__ == '__main__':
    main()
