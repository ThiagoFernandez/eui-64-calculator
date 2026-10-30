import argparse
import ipaddress
from getmac import get_mac_address

HEX = "0123456789abcdef"

def crear_args():
    p = argparse.ArgumentParser(description="EUI-64 CALCULATOR")
    p.add_argument("-m", "--mac", type=str, default=get_mac_address(), help="Ingrese la mac")
    p.add_argument("-p", "--prefix", type=str, required=True, help="Ingrese el prefijo")
    return p.parse_args()

def calcular_iid(mac):
    # 1. normalizo la mac
    mac_normalizada = ""
    for b in mac.strip():
        if b not in ":-.":
            mac_normalizada += b.lower()

    # 2. valido la mac normalizada
    if len(mac_normalizada) != 12:
        raise ValueError(f"MAC inválida: {mac!r} (se esperan 12 dígitos hex)")
    for b in mac_normalizada:
        if b not in HEX:
            raise ValueError(f"MAC inválida: {mac!r} (carácter no hex: {b!r})")

    # 3. parto la mac para insertar el "fffe" en la mitad
    second_step = mac_normalizada[:6] + "fffe" + mac_normalizada[6:]

    # 4. invierto el 7mo bit del primer octeto
    primer_octeto = int(second_step[:2], 16) ^ 0x02
    nuevo_octeto = format(primer_octeto, "02x")
    iid = nuevo_octeto + second_step[2:]

    return iid


def formatear_iid(iid):
    grupos = []
    for i in range(0, len(iid), 4):
        grupos.append(iid[i:i + 4])
    return ":".join(grupos)


def armar_direccion(prefijo, iid):
    try:
        red = ipaddress.IPv6Network(prefijo) # esto me da la red
    except ValueError as e:
        raise ValueError(f"Prefijo inválido: {prefijo!r} ({e})")

    if red.prefixlen != 64:
        raise ValueError(f"Prefijo inválido: {prefijo} (no es /64)")

    direccion = int(red.network_address) | int(iid, 16) # junto la red con el iid
    return str(ipaddress.IPv6Address(direccion))                  # me formatea la direccion a ipv6

def obtener_ra():
    pass


def main():
    args = crear_args()
    try:
        iid = calcular_iid(args.mac)
        print("IID:", formatear_iid(iid))
        direccion = armar_direccion(args.prefix, iid)
        print("Dirección:", direccion)
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
