#arquivo que faz o download de todas as fontes de uma vez, fazendo a geração do pdf ser mais rápida
import os
import requests

def download_file(url, filepath):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filepath}")
    else:
        print(f"Failed to download: {url}")

def main():
    fonts_dir = os.path.join("templates", "fonts")
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)

    fonts = {
        "Montserrat-Regular.ttf": "https://fonts.gstatic.com/s/montserrat/v31/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCtr6Ew-.ttf",
        "Montserrat-SemiBold.ttf": "https://fonts.gstatic.com/s/montserrat/v31/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCu170w-.ttf",
        "Montserrat-Bold.ttf": "https://fonts.gstatic.com/s/montserrat/v31/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCuM70w-.ttf",
        "OpenSans-Regular.ttf": "https://fonts.gstatic.com/s/opensans/v44/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0C4n.ttf",
        "OpenSans-SemiBold.ttf": "https://fonts.gstatic.com/s/opensans/v44/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsgH1y4n.ttf"
    }

    for filename, url in fonts.items():
        filepath = os.path.join(fonts_dir, filename)
        download_file(url, filepath)

if __name__ == "__main__":
    main()
