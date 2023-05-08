import argparse
from netaddr import *
from prettytable import PrettyTable

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
    
def get_needed_bits(args):
    needed_bits = get_subnet_bit_size(args)
    bit_list = []
    count = 0
    for x in range(args.amount):
        bit_list.append(str(bin(count)[2:].zfill(needed_bits)))
        count += 1    
    return bit_list

def get_subnet_bit_size(args):
    needed_bits = 0
    pow_sum = 0
    while args.amount > pow_sum:
        needed_bits = needed_bits + 1
        pow_sum = pow(2,needed_bits)
    return needed_bits

def get_last_bit(subnet_list):
    count = 0
    for x in subnet_list:
        if x != "1":
            break
        else:
            count += 1
    return count

def print_subnets(subnetmask, last_bit, subnetbits, ip, args):
    count = 0
    while count < len(subnetbits):
        subnetmask[last_bit:last_bit+len(subnetbits[0])] = subnetbits[count]
        subnet_id = (f"Subnetz {count+1}")
        print_hosts(subnetmask,last_bit,ip, args, subnet_id)
        count += 1
    print(table)

def print_hosts(subnetmask,last_bit,ip,args, subnet_id):
    ip_bin = ip.bin[2:]
    ip_cut = ip_bin[:last_bit]
    ip_subnetted = subnetmask[:]
    ip_subnetted[0:last_bit] = ip_cut
    ip_str = ""
    ip_str = ''.join(ip_subnetted)
    broadcast_ip = get_broadcast(ip_subnetted,last_bit,get_subnet_bit_size(args))
    net_id = binary_ip_to_decimal(ip_str,False,False)
    first_host = binary_ip_to_decimal(ip_str,True,False)
    last_host = binary_ip_to_decimal(broadcast_ip,False,True)
    broadcast = binary_ip_to_decimal(broadcast_ip,False,False)
    table.add_row([subnet_id, net_id, first_host, last_host, broadcast])

def get_broadcast(ip,last_bit,needed_bit):
    last_host = ip[:]
    last_host = last_host[last_bit+needed_bit::1]
    for x in range(len(last_host)):
        last_host[x] = "1"
    broadcast_ip = ip[:]
    broadcast_ip[last_bit+needed_bit::] = last_host
    broadcast_ip = ''.join(broadcast_ip)
    return broadcast_ip

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
    elif(bool_last_host == True):
        dec_ip = f"{octet_one}.{octet_two}.{octet_three}.{octet_four-1}"
    return dec_ip

def get_new_subnet_mask(subnetmask,last_bit, needed_bits, subnet_bits):
    new_subnet_mask = subnetmask[:]
    new_subnet_mask[last_bit:last_bit+needed_bits] = subnet_bits[-1]
    new_subnet_mask = ''.join(new_subnet_mask)
    new_subnet_mask = binary_ip_to_decimal(new_subnet_mask, False, False)
    return new_subnet_mask
    
def get_new_prefix(new_subnet_mask):
    prefix = 1
    subnet_mask = IPAddress(new_subnet_mask)
    subnet_mask_bin = subnet_mask.bin[2:]
    for x in subnet_mask_bin:
        if x == "1":
            prefix += 1 
    return prefix

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
    print_subnets(subnet_mask,last_bit,needed_bits_ls, ip, args)
    new_subnet_mask = get_new_subnet_mask(subnet_mask,last_bit,get_subnet_bit_size(args),needed_bits_ls)
    new_mask_prefix_table.add_row([new_subnet_mask, get_new_prefix(new_subnet_mask)])
    print(new_mask_prefix_table)

main()