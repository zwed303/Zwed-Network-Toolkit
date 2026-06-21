#!/usr/bin/env python3
"""
ZWED.DEV Network Toolkit
-------------------------
Tek bir menüden erişilen network araçları seti:
  1) IP Tracer        - IP geolocation
  2) Ping (ICMP)       - Host erişilebilirlik testi
  3) Port Tarayıcı     - TCP connect scan
  4) MAC Adresi Bulucu - Yerel ağ ARP taraması
  5) DNS Sorgulayıcı   - Domain <-> IP çözümleme

NOT: Port tarayıcı ve ARP tarayıcı sadece sahibi olduğun veya
tarama izni olan sistemler/ağlar üzerinde kullanılmalıdır.
"""

import os
import sys
import json
import socket
import shutil
import subprocess
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed


# ---------------- Renkler ----------------
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    PURPLE = "\033[35m"


BANNER = rf"""{C.MAGENTA}{C.BOLD}
   ███████╗██╗    ██╗███████╗██████╗
   ╚══███╔╝██║    ██║██╔════╝██╔══██╗
     ███╔╝ ██║ █╗ ██║█████╗  ██║  ██║
    ███╔╝  ██║███╗██║██╔══╝  ██║  ██║
   ███████╗╚███╔███╔╝███████╗██████╔╝
   ╚══════╝ ╚══╝╚══╝ ╚══════╝╚═════╝
{C.RESET}{C.CYAN}{C.BOLD}         ZWED.DEV{C.RESET}{C.DIM} • Network Toolkit{C.RESET}
"""


def clear():
    os.system("clear" if os.name == "posix" else "cls")


def header(title):
    clear()
    print(BANNER)
    print(f"  {C.PURPLE}{'─' * 50}{C.RESET}")
    print(f"  {C.GREEN}{C.BOLD}{title}{C.RESET}")
    print(f"  {C.PURPLE}{'─' * 50}{C.RESET}\n")


def box_line(label, value, width=46):
    label_str = f"{C.CYAN}{label:<13}{C.RESET}"
    value_str = f"{C.WHITE}{value}{C.RESET}"
    return f"  {C.DIM}│{C.RESET} {label_str}{C.DIM}:{C.RESET} {value_str}"


def box_top():
    print(f"  {C.PURPLE}┌{'─' * 50}┐{C.RESET}")


def box_bottom():
    print(f"  {C.PURPLE}└{'─' * 50}┘{C.RESET}")


def back_to_menu():
    print()
    input(f"  {C.YELLOW}↩  Ana menüye dönmek için [M] tuşlayıp Enter'a basınız...{C.RESET} ")


def signature():
    print(f"\n  {C.DIM}{'─' * 46}{C.RESET}")
    print(f"  💬 {C.PURPLE}{C.BOLD}@zwed.py{C.RESET}\n")


# ==================================================
# 1) IP TRACER
# ==================================================
def get_my_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=5) as r:
            return json.loads(r.read().decode()).get("ip")
    except Exception as e:
        print(f"{C.RED}[!] Kendi IP adresi alınamadı: {e}{C.RESET}")
        return None


def lookup_ip(ip):
    url = (
        f"http://ip-api.com/json/{ip}?"
        f"fields=status,message,country,countryCode,region,regionName,city,"
        f"zip,lat,lon,timezone,isp,org,as,query"
    )
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"{C.RED}[!] Hata: {e}{C.RESET}")
        return None


def tool_ip_tracer():
    header("📍  IP TRACER")
    ip = input(f"  {C.YELLOW}➤ Sorgulanacak IP (boş = kendi IP'n):{C.RESET} ").strip()
    if not ip:
        print(f"  {C.DIM}Kendi IP'niz tespit ediliyor...{C.RESET}")
        ip = get_my_ip()
        if not ip:
            back_to_menu()
            return

    print(f"  {C.DIM}{ip} sorgulanıyor...{C.RESET}")
    data = lookup_ip(ip)

    if not data or data.get("status") != "success":
        print(f"  {C.RED}[!] Sonuç bulunamadı.{C.RESET}")
        back_to_menu()
        return

    print()
    box_top()
    print(box_line("IP", data.get("query")))
    print(box_line("Ülke", f"{data.get('country')} ({data.get('countryCode')})"))
    print(box_line("Bölge", data.get("regionName")))
    print(box_line("Şehir", data.get("city")))
    print(box_line("Koordinat", f"{data.get('lat')}, {data.get('lon')}"))
    print(box_line("ISP", data.get("isp")))
    print(box_line("Org", data.get("org")))
    box_bottom()
    lat, lon = data.get("lat"), data.get("lon")
    if lat is not None:
        print(f"\n  🗺  {C.BLUE}https://www.google.com/maps?q={lat},{lon}{C.RESET}")

    signature()
    back_to_menu()


# ==================================================
# 2) PING (ICMP)
# ==================================================
def tool_ping():
    header("📡  PING (ICMP)")
    host = input(f"  {C.YELLOW}➤ Ping atılacak host/IP:{C.RESET} ").strip()
    if not host:
        back_to_menu()
        return

    count_raw = input(f"  {C.YELLOW}➤ Paket sayısı (varsayılan 4):{C.RESET} ").strip()
    count = count_raw if count_raw.isdigit() else "4"

    if not shutil.which("ping"):
        print(f"\n  {C.RED}[!] 'ping' komutu bulunamadı.{C.RESET}")
        print(f"  {C.DIM}Kurmak için: pkg install inetutils -y{C.RESET}")
        back_to_menu()
        return

    print(f"\n  {C.DIM}{host} pingleniyor...{C.RESET}\n")
    try:
        result = subprocess.run(
            ["ping", "-c", count, host],
            capture_output=True, text=True, timeout=int(count) * 3 + 5
        )
        output = result.stdout if result.stdout else result.stderr
        box_top()
        for line in output.strip().splitlines():
            colored = line
            if "bytes from" in line or "icmp_seq" in line:
                colored = f"{C.GREEN}{line}{C.RESET}"
            elif "unreachable" in line.lower() or "100% packet loss" in line.lower():
                colored = f"{C.RED}{line}{C.RESET}"
            print(f"  {C.DIM}│{C.RESET} {colored}")
        box_bottom()
    except subprocess.TimeoutExpired:
        print(f"  {C.RED}[!] Zaman aşımı.{C.RESET}")
    except Exception as e:
        print(f"  {C.RED}[!] Hata: {e}{C.RESET}")

    signature()
    back_to_menu()


# ==================================================
# 3) PORT TARAYICI
# ==================================================
def scan_port(ip, port, timeout=0.6):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            return port if result == 0 else None
    except Exception:
        return None


def tool_port_scanner():
    header("🔍  PORT TARAYICI")
    print(f"  {C.DIM}Not: Sadece sahibi olduğun veya izinli olduğun sistemleri tara.{C.RESET}\n")

    target = input(f"  {C.YELLOW}➤ Hedef host/IP:{C.RESET} ").strip()
    if not target:
        back_to_menu()
        return

    try:
        ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(f"  {C.RED}[!] Host çözümlenemedi.{C.RESET}")
        back_to_menu()
        return

    range_raw = input(f"  {C.YELLOW}➤ Port aralığı (örn 1-1024, varsayılan 1-1024):{C.RESET} ").strip()
    try:
        if "-" in range_raw:
            start, end = map(int, range_raw.split("-"))
        elif range_raw:
            start = end = int(range_raw)
        else:
            start, end = 1, 1024
    except ValueError:
        print(f"  {C.RED}[!] Geçersiz aralık, 1-1024 kullanılıyor.{C.RESET}")
        start, end = 1, 1024

    ports = range(start, end + 1)
    print(f"\n  {C.DIM}{ip} üzerinde {len(ports)} port taranıyor...{C.RESET}\n")

    open_ports = []
    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = {executor.submit(scan_port, ip, p): p for p in ports}
        for future in as_completed(futures):
            result = future.result()
            if result:
                open_ports.append(result)

    open_ports.sort()
    box_top()
    if open_ports:
        for p in open_ports:
            try:
                service = socket.getservbyport(p)
            except Exception:
                service = "bilinmiyor"
            print(box_line(f"Port {p}", f"{C.GREEN}AÇIK{C.RESET} ({service})"))
    else:
        print(f"  {C.DIM}│ Açık port bulunamadı.{C.RESET}")
    box_bottom()

    signature()
    back_to_menu()


# ==================================================
# 4) MAC ADRESİ BULUCU (ARP SCANNER - yerel ağ)
# ==================================================
def ping_host(ip):
    try:
        subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2
        )
    except Exception:
        pass


def get_arp_table():
    # Önce 'ip neigh' dene, olmazsa 'arp -a'
    if shutil.which("ip"):
        try:
            out = subprocess.run(["ip", "neigh"], capture_output=True, text=True, timeout=5)
            return out.stdout
        except Exception:
            pass
    if shutil.which("arp"):
        try:
            out = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=5)
            return out.stdout
        except Exception:
            pass
    return None


def tool_arp_scanner():
    header("🖧  MAC ADRESİ BULUCU (Yerel Ağ)")
    print(f"  {C.DIM}Bu araç sadece bağlı olduğun WiFi/yerel ağdaki cihazları bulur.{C.RESET}\n")

    if not shutil.which("ping"):
        print(f"  {C.RED}[!] 'ping' komutu bulunamadı. pkg install inetutils -y{C.RESET}")
        back_to_menu()
        return
    if not (shutil.which("ip") or shutil.which("arp")):
        print(f"  {C.RED}[!] 'ip' veya 'arp' komutu bulunamadı.{C.RESET}")
        print(f"  {C.DIM}Kurmak için: pkg install net-tools -y{C.RESET}")
        back_to_menu()
        return

    subnet = input(f"  {C.YELLOW}➤ Taranacak yerel ağ (örn 192.168.1):{C.RESET} ").strip()
    if not subnet:
        back_to_menu()
        return

    print(f"\n  {C.DIM}{subnet}.1-254 taranıyor (biraz sürebilir)...{C.RESET}")

    ips = [f"{subnet}.{i}" for i in range(1, 255)]
    with ThreadPoolExecutor(max_workers=64) as executor:
        list(executor.map(ping_host, ips))

    raw = get_arp_table()
    if not raw:
        print(f"  {C.RED}[!] ARP tablosu okunamadı.{C.RESET}")
        back_to_menu()
        return

    found = []
    for line in raw.splitlines():
        if subnet not in line:
            continue
        parts = line.replace("(", " ").replace(")", " ").split()
        ip_addr, mac = None, None
        for token in parts:
            if token.count(".") == 3 and token.split(".")[0].isdigit():
                ip_addr = token
            if token.count(":") == 5:
                mac = token
        if ip_addr and mac and mac.lower() != "00:00:00:00:00:00":
            found.append((ip_addr, mac))

    print()
    box_top()
    if found:
        for ip_addr, mac in sorted(set(found)):
            print(box_line(ip_addr, mac))
    else:
        print(f"  {C.DIM}│ Cihaz bulunamadı (ARP cache boş olabilir).{C.RESET}")
    box_bottom()

    signature()
    back_to_menu()


# ==================================================
# 5) DNS SORGULAYICI
# ==================================================
def tool_dns_lookup():
    header("🌐  DNS SORGULAYICI")
    query = input(f"  {C.YELLOW}➤ Domain veya IP girin:{C.RESET} ").strip()
    if not query:
        back_to_menu()
        return

    print()
    box_top()
    is_ip = query.replace(".", "").isdigit() and query.count(".") == 3

    try:
        if is_ip:
            host, aliases, _ = socket.gethostbyaddr(query)
            print(box_line("IP", query))
            print(box_line("Hostname", host))
            if aliases:
                print(box_line("Aliases", ", ".join(aliases)))
        else:
            host, aliases, ips = socket.gethostbyname_ex(query)
            print(box_line("Domain", query))
            print(box_line("IP(ler)", ", ".join(ips)))
            if aliases:
                print(box_line("Aliases", ", ".join(aliases)))
    except socket.herror:
        print(f"  {C.DIM}│ Bu IP için PTR (reverse DNS) kaydı bulunamadı.{C.RESET}")
    except socket.gaierror:
        print(f"  {C.DIM}│ Domain çözümlenemedi.{C.RESET}")
    box_bottom()

    # Ek kayıt türleri (dig kuruluysa)
    if not is_ip and shutil.which("dig"):
        print(f"\n  {C.DIM}Ek kayıtlar (dig):{C.RESET}")
        for record in ["MX", "NS", "TXT"]:
            try:
                out = subprocess.run(
                    ["dig", "+short", query, record],
                    capture_output=True, text=True, timeout=5
                ).stdout.strip()
                if out:
                    print(box_line(record, out.replace(chr(10), " | ")))
            except Exception:
                pass
    elif not is_ip:
        print(f"\n  {C.DIM}MX/NS/TXT kayıtları için: pkg install dnsutils -y{C.RESET}")

    signature()
    back_to_menu()


# ==================================================
# ANA MENÜ
# ==================================================
MENU = {
    "1": ("IP Tracer", tool_ip_tracer),
    "2": ("Ping (ICMP)", tool_ping),
    "3": ("Port Tarayıcı", tool_port_scanner),
    "4": ("MAC Adresi Bulucu (ARP)", tool_arp_scanner),
    "5": ("DNS Sorgulayıcı", tool_dns_lookup),
}


def main_menu():
    while True:
        clear()
        print(BANNER)
        print(f"  {C.PURPLE}{'─' * 50}{C.RESET}")
        for key, (name, _) in MENU.items():
            print(f"  {C.CYAN}{C.BOLD}[{key}]{C.RESET} {C.WHITE}{name}{C.RESET}")
        print(f"  {C.RED}{C.BOLD}[0]{C.RESET} {C.WHITE}Çıkış{C.RESET}")
        print(f"  {C.PURPLE}{'─' * 50}{C.RESET}")

        choice = input(f"\n  {C.YELLOW}➤ Bir araç seçin:{C.RESET} ").strip()

        if choice == "0" or choice.lower() == "q":
            print(f"\n  {C.DIM}Görüşürüz! 💬 @zwed.py{C.RESET}\n")
            break
        elif choice in MENU:
            try:
                MENU[choice][1]()
            except KeyboardInterrupt:
                print(f"\n  {C.YELLOW}[!] İşlem iptal edildi.{C.RESET}")
                back_to_menu()
        else:
            print(f"\n  {C.RED}[!] Geçersiz seçim.{C.RESET}")
            input(f"  {C.DIM}Devam etmek için Enter'a basın...{C.RESET}")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n  {C.DIM}Çıkış yapıldı.{C.RESET}\n")
        sys.exit(0)

