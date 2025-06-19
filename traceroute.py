import sys
import socket
import requests
import plotly.express as px

# Site cu informații despre Ip luat de pe internet (link https://ipinfo.io/)
fake_HTTP_header = {
    'referer': 'https://ipinfo.io/',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36'
}

lista_de_tari = []

# Crearea socket-urilor pentru trimiterea UDP și primirea ICMP
UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
ICMP_recover_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
ICMP_recover_socket.settimeout(3)

def traceroute(ip, port):
    # Setarea socket-ului pentru trimiterea UDP
    TTL = 64
    addr = None
    for i in range(1, TTL + 1):
        UDP_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, i)

        try:
            # Trimite pachet UDP către IP și portul dat
            UDP_socket.sendto(b'Inabakumori rules tbh', (ip, port))

            try:
                # Așteaptă răspuns ICMP de la destinație; 63535 este dimensiunea maximă a datelor ICMP
                _, addr = ICMP_recover_socket.recvfrom(63535)
                print(f"ttl:{i} Ip:{addr[0]}\n")

                try:
                    # Foloseste API (Ip_loc este de tip Response)
                    Ip_loc = requests.get(f'http://ip-api.com/json/{addr[0]}?fields=status,country,regionName,city,lat,lon',
                                       headers=fake_HTTP_header)
                    loc_data = Ip_loc.json()
                    city = loc_data.get('city')
                    country = loc_data.get('country')

                    lista_de_tari.append(country)
                    print(f"{city},{country}\n")
                except Exception:
                    print("[Location lookup failed]\n")

                if addr[0] == ip:
                    print("Destination reached.")
                    break
            except socket.timeout:
                print(f"{i} timeout.")
        except Exception as f:
            print(f)

    return addr

# Creaza un nou thread pentru a rula traceroute
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("no.")
        sys.exit(1)
    ip = sys.argv[1]
    port = int(sys.argv[2])

    traceroute(ip, port)

    # plotly
    # Subpunctul pentru crearea hărții 
    df = px.data.gapminder()
    df = df[df['country'].isin(lista_de_tari)]
    fig = px.scatter_geo(df, locations='iso_alpha',
                         hover_name='country',
                         title='Router locations',
                         color_discrete_sequence=['red'])
    fig.write_html("traceroute_map.html")