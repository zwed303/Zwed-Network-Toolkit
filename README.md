# ZWED.DEV Network Toolkit

Tek bir terminal menüsünden erişilen, temel ağ teşhis ve keşif araçları seti. Python ile yazılmıştır, Termux ve Linux üzerinde çalışır.

```
   ███████╗██╗    ██╗███████╗██████╗
   ╚══███╔╝██║    ██║██╔════╝██╔══██╗
     ███╔╝ ██║ █╗ ██║█████╗  ██║  ██║
    ███╔╝  ██║███╗██║██╔══╝  ██║  ██║
   ███████╗╚███╔███╔╝███████╗██████╔╝
   ╚══════╝ ╚══╝╚══╝ ╚══════╝╚═════╝
            ZWED.DEV • Network Toolkit
```

## Özellikler

| # | Araç | Açıklama |
|---|------|----------|
| 1 | **IP Tracer** | Bir IP adresinin ülke/şehir/ISP bilgisini gösterir |
| 2 | **Ping (ICMP)** | Hedefin erişilebilir olup olmadığını test eder |
| 3 | **Port Tarayıcı** | Belirtilen port aralığında açık portları bulur (TCP connect scan) |
| 4 | **MAC Adresi Bulucu** | Aynı yerel ağdaki (WiFi) cihazları ve MAC adreslerini listeler |
| 5 | **DNS Sorgulayıcı** | Domain ↔ IP çözümleme, ek olarak MX/NS/TXT kayıtları |

Tüm araçlar tek menüden seçilir, her işlem sonunda ana menüye dönülür — tool kapanmaz.

## Kurulum

### Termux

```bash
pkg update
pkg install python git inetutils net-tools dnsutils -y
git clone https://github.com/KULLANICI_ADIN/zwed-network-toolkit.git
cd zwed-network-toolkit
python zwed_toolkit.py
```

### Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install python3 git iputils-ping net-tools dnsutils -y
git clone https://github.com/KULLANICI_ADIN/zwed-network-toolkit.git
cd zwed-network-toolkit
python3 zwed_toolkit.py
```

### Tek dosya indirme (git olmadan)

```bash
curl -O https://raw.githubusercontent.com/zwed303/zwed-network-toolkit/main/zwed_toolkit.py
python zwed_toolkit.py
```

## Kullanım

Programı çalıştır, menüden bir numara seç (`1`-`5`), istenen bilgiyi gir. İşlem bitince:

```
↩  Ana menüye dönmek için [M] tuşlayıp Enter'a basınız...
```

Çıkış için ana menüde `0` veya `q` yaz.

## Bağımlılıklar

Sadece Python standart kütüphanesi kullanılır, ek pip paketi gerekmez. Bazı araçlar sistem komutlarına ihtiyaç duyar:

- `ping` → `inetutils` (Termux) / `iputils-ping` (Debian)
- `ip` / `arp` → `net-tools`
- `dig` (opsiyonel, DNS ek kayıtlar için) → `dnsutils`

Eksik komutlar için araç çalışırken hangi paketi kurman gerektiğini söyler.

## Sorumlu Kullanım

Port tarayıcı ve MAC adresi bulucu araçları **sadece sahibi olduğun veya tarama izni olan sistemler/ağlar üzerinde** kullanılmalıdır. Başka birinin ağını veya sunucusunu izinsiz taramak bulunduğun ülkenin yasalarına göre suç teşkil edebilir. Bu araçlar eğitim ve kendi altyapını test etme amacıyla geliştirilmiştir.

## Lisans

MIT

