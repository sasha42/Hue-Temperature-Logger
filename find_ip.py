import nmap
import os

def find_philips_hue_bridge():
    # Create an Nmap scanner object
    nm = nmap.PortScanner()
    print('Scanning network for Philips Hue bridge...')

    # Scan the local network for devices with the manufacturer name "Philips Lighting BV"
    results = nm.scan(hosts='192.168.1.0/24', arguments='-sn')

    # Get the results of the scan
    data = results['scan']
    print('Found {} devices'.format(len(data)))

    # Iterate over the devices and print the vendor name and IP address
    for device in data:
        try:
            mac_address = list(data[device]['vendor'].keys())[0]
            vendor = data[device]['vendor'][mac_address]
            ip = data[device]['addresses']['ipv4']

            # Check if the vendor is Philips Lighting BV
            if vendor == 'Philips Lighting BV':
                print('Found Philips Hue bridge at IP address {}'.format(ip))

                # Set environment variable for Philips Hue bridge IP address
                os.environ['PHILIPS_HUE_IP'] = ip
                return ip
        except:
            pass

    print('Could not find Philips Hue bridge on the network')
    return None

if __name__ == '__main__':
    find_philips_hue_bridge()