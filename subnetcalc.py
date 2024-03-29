import argparse
from netaddr import *
from prettytable import PrettyTable

# Gibt die Subnetz-Bits im Binärformat zurück
def get_subnet_bin(args):
    if(args.prefix):
        subnet = IPAddress("0.0.0.0")
        subnet_bin = subnet.bits().replace(".", "")
        subnet_bin_prefixed = subnet_bin.replace("0", "1", args.prefix)
        return subnet_bin_prefixed
    elif(args.mask):
        subnet = IPAddress(args.mask)
        subnet_binary = subnet.bin[2:]
        return subnet_binary
    
# Gibt eine Liste von Binärzahlen zurück, die die benötigten Bits für die Subnetze darstellen
def get_needed_bits(args):
    needed_bits = get_subnet_bit_count(args)
    bit_list = []
    count = 0
    for x in range(args.amount):
        bit_list.append(str(bin(count)[2:].zfill(needed_bits)))
        count += 1    
    return bit_list

# Gibt die Anzahl der benötigten Bits für die Subnetze zurück
def get_subnet_bit_count(args):
    needed_bits = 0
    pow_sum = 0
    while args.amount > pow_sum:
        needed_bits = needed_bits + 1
        pow_sum = pow(2,needed_bits)
    return needed_bits

# Gibt den Index des letzten Bits zurück, das nicht "1" ist
def get_last_bit(subnet_list):
    count = 0
    for x in subnet_list:
        if x != "1":
            break
        else:
            count += 1
    return count

# Druckt die Subnetze, Netzwerkinformationen und Broadcast-Adressen
def print_subnets(subnetmask, last_bit, subnetbits, ip, args):
    count = 0
    while count < len(subnetbits):
        subnetmask[last_bit:last_bit+len(subnetbits[0])] = subnetbits[count]
        subnet_id = (f"Subnetz {count+1}")
        print_hosts(subnetmask,last_bit,ip, args, subnet_id)
        count += 1
    print(table)

# Druckt Host-Informationen für ein Subnetz
def print_hosts(subnetmask,last_bit,ip,args, subnet_id):
    ip_bin = ip.bin[2:]
    ip_cut = ip_bin[:last_bit]
    ip_subnetted = subnetmask[:]
    ip_subnetted[0:last_bit] = ip_cut
    ip_str = ""
    ip_str = ''.join(ip_subnetted)
    broadcast_ip = get_broadcast(ip_subnetted,last_bit,get_subnet_bit_count(args))
    net_id = binary_ip_to_decimal(ip_str,False,False)
    first_host = binary_ip_to_decimal(ip_str,True,False)
    last_host = binary_ip_to_decimal(broadcast_ip,False,True)
    broadcast = binary_ip_to_decimal(broadcast_ip,False,False)
    table.add_row([subnet_id, net_id, first_host, last_host, broadcast])

# Gibt die Broadcast-Adresse für ein Subnetz zurück
def get_broadcast(ip,last_bit,needed_bit):
    broadcast_bits = ip[:]
    broadcast_bits = broadcast_bits[last_bit+needed_bit::1]
    for x in range(len(broadcast_bits)):
        broadcast_bits[x] = "1"
    broadcast_ip = ip[:]
    broadcast_ip[last_bit+needed_bit::] = broadcast_bits
    broadcast_ip = ''.join(broadcast_ip)
    return broadcast_ip

# Konvertiert eine Binär-IP-Adresse in eine Dezimal-IP-Adresse
def binary_ip_to_decimal(ip_str, bool_first_host, bool_last_host):
    octet_one = ip_str[0:8]
    octet_one = int(octet_one, 2)
    octet_two = ip_str[8:16]
    octet_two = int(octet_two, 2)
    octet_three = ip_str[16:24]
    octet_three = int(octet_three, 2)
    octet_four = ip_str [24:32]
    octet_four = int(octet_four, 2)
    if(bool_first_host == False):
        dec_ip = f"{octet_one}.{octet_two}.{octet_three}.{octet_four}"
    elif(bool_first_host == True):
        dec_ip = f"{octet_one}.{octet_two}.{octet_three}.{octet_four+1}"
    if(bool_last_host == True):
        dec_ip = f"{octet_one}.{octet_two}.{octet_three}.{octet_four-1}"
    return dec_ip

# Berechnet die neue Subnetzmaske für das letzte Subnetz und gibt sie zurück
def get_new_subnet_mask(subnetmask,last_bit, needed_bits, subnet_bits):
    new_subnet_mask = subnetmask[:]
    new_subnet_mask[last_bit:last_bit+needed_bits] = subnet_bits[-1]
    new_subnet_mask = ''.join(new_subnet_mask)
    new_subnet_mask = binary_ip_to_decimal(new_subnet_mask, False, False)
    return new_subnet_mask
    
# Berechnet den neuen CIDR-Präfix für das letzte Subnetz und gibt ihn zurück
def get_new_prefix(new_subnet_mask):
    prefix = 0
    subnet_mask = IPAddress(new_subnet_mask)
    subnet_mask_bin = subnet_mask.bin[2:]
    for x in subnet_mask_bin:
        if x == "1":
            prefix += 1 
    return prefix

# Überprüft, ob das Subnetz gültig ist (nicht zu viele Hosts)
def validate_subnet(last_bit, needed_bit):
    valid = False
    if (last_bit + needed_bit < 31):
        valid = True
    else:
        valid = False
    return valid

# Hauptfunktion, die den Code ausführt
def main():
    global table
    table = PrettyTable()
    table.field_names = ["Subnetz", "Netz-ID", "First Host", "Last Host", "Broadcast"]
    new_mask_prefix_table = PrettyTable()
    new_mask_prefix_table.field_names = ["Neue Subnetzsmaske", "Neuer CIDR Prefix",]
    parser = argparse.ArgumentParser()
    
    ### Argparse Argumente ###
    parser.add_argument("-ip", help="Enter a valid IPv4 Address", type=str, required=True, metavar="127.0.0.1")
    subnet_group = parser.add_mutually_exclusive_group(required=True)
    subnet_group.add_argument("-mask", help="Enter a valid subnet mask", type=str, metavar="255.255.255.0")
    subnet_group.add_argument("-prefix", help="Enter a valid Subnet Prefix", type=int, metavar=24)
    parser.add_argument("-a", "--amount", help="Amount of subnets wanted", type=int, required=True)

    args = parser.parse_args()
    ip = IPAddress(args.ip)
    subnet_mask = [*get_subnet_bin(args)]
    needed_bits_ls = get_needed_bits(args)
    last_bit = get_last_bit(subnet_mask)
    new_subnet_mask = get_new_subnet_mask(subnet_mask,last_bit,get_subnet_bit_count(args),needed_bits_ls)
    cidr_prefix = get_new_prefix(new_subnet_mask)
    if (validate_subnet(last_bit, get_subnet_bit_count(args))):
        print_subnets(subnet_mask,last_bit,needed_bits_ls, ip, args)
        new_mask_prefix_table.add_row([new_subnet_mask, get_new_prefix(new_subnet_mask)])
        print(new_mask_prefix_table)
    else:
        print("Zu wenig Host Adressen um Subnetze zu bilden.")

main()