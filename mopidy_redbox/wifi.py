#!/usr/bin/python
import os
import subprocess

def install(ap_name, ap_passwd):
    os.popen("sudo apt install dnsmasq hostapd")

    os.popen('sudo systemctl stop dnsmasq')
    os.popen('sudo systemctl stop hostapd')

    os.popen('sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.source')
    os.popen('sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig')

    os.popen('sudo touch /etc/dnsmasq.conf')
    os.popen('sudo echo "interface=wlan0      # Use the require wireless interface - usually wlan0" >> /etc/dnsmasq.conf')
    os.popen('sudo echo"dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h" >> /etc/dnsmasq.conf')
    os.popen('sudo systemctl reload dnsmasq')


    with open('/etc/hostapd/hostapd.conf', "w") as hostapd:
        hostapd.write("""\
interface=wlan0
driver=nl80211
ssid={}
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP""".format(ap_name, ap_passwd))

    os.popen('sudo echo "DAEMON_CONF="/etc/hostapd/hostapd.conf" >> /etc/default/hostapd')


def scan_networks(interface="wlan0"):
    print "Scanning available networks"
    command = """sudo iwlist {} scan | grep -ioE 'SSID:"(.*)"'""".format(interface)
    result = os.popen(command)
    result = list(result)
    ssid_list = []

    if "Device or resource busy" not in result:
        ssid_list = [item.lstrip('SSID:').strip('"\n') for item in result]

    return [i for i in set(ssid_list) if i != ""]



def turn_on_ap():
    print "Starting AP"
    os.popen("sudo systemctl stop dhcpcd")

    os.popen("sudo cp /etc/dhcpcd.conf.source /etc/dhcpcd.conf")
    os.popen('sudo echo "interface wlan0" >> /etc/dhcpcd.conf')
    os.popen('sudo echo "    static ip_address=192.168.4.1/24" >> /etc/dhcpcd.conf')
    os.popen('sudo echo "    nohook wpa_supplicant" >> /etc/dhcpcd.conf')
    os.popen("sudo systemctl start dhcpcd")
    
    os.popen("sudo systemctl start dnsmasq")
    os.popen("sudo systemctl start hostapd")




def turn_off_ap():
    print "Stoping AP"
    os.popen("sudo systemctl stop hostapd")
    os.popen("sudo systemctl stop dnsmasq")

    os.popen("ip addr flush dev wlan0")
    os.popen("ip link set dev wlan0 up")


    # dhcpcd  -n "$wifidev"
    os.popen("sudo systemctl stop dhcpcd")
    os.popen("sudo cp /etc/dhcpcd.conf.source /etc/dhcpcd.conf")
    # edit file dhcpcd remove wlan0 stuff
    os.popen("sudo systemctl start dhcpcd")





def is_connected_to_internet():
    print "Checking Internet Connection"
    cmd = "ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3` > /dev/null && echo ok || echo error"
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True)
    output, err = process.communicate()
    print output
    
    return output == "ok"



if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        if sys.argv[1] == "on":
            turn_on_ap()

        else:
            turn_off_ap()

    else:
        if not is_connected_to_internet():
            print scan_networks()

            turn_on_ap()

