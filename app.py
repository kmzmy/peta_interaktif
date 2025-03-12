import os
import zipfile
from xml.etree import ElementTree as ET
from geopy.distance import geodesic
from flask import Flask, request, jsonify
from scipy.spatial import KDTree  # Struktur data untuk pencarian cepat

# Folder tempat file KML & KMZ berada
KML_FOLDER = r"C:\Users\admin\peta-interaktif\data"

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Tambahkan ini untuk mengizinkan semua domain mengakses API Flask

def baca_koordinat_kml(kml_content):
    """Mengekstrak koordinat dari string XML KML."""
    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    root = ET.fromstring(kml_content)
    
    placemarks = []
    for placemark in root.findall(".//kml:Placemark", ns):
        name = placemark.find("kml:name", ns)
        point = placemark.find(".//kml:Point/kml:coordinates", ns)
        polygon = placemark.find(".//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates", ns)

        if point is not None:
            coords = point.text.strip().split(",")
            lon, lat = float(coords[0]), float(coords[1])
            placemarks.append((name.text if name is not None else "Unnamed", (lon, lat)))

        elif polygon is not None:
            coords_list = polygon.text.strip().split()
            if coords_list:
                first_coords = coords_list[0].split(",")
                lon, lat = float(first_coords[0]), float(first_coords[1])
                placemarks.append((name.text if name is not None else "Unnamed", (lon, lat)))

    return placemarks

def load_kml_data():
    """Membaca semua file KML & KMZ dalam folder lalu menyimpan koordinatnya."""
    kml_data = []

    for file_name in os.listdir(KML_FOLDER):
        file_path = os.path.join(KML_FOLDER, file_name)

        try:
            if file_name.endswith(".kml"):
                with open(file_path, "r", encoding="utf-8") as f:
                    kml_content = f.read()
                    placemarks = baca_koordinat_kml(kml_content)

            elif file_name.endswith(".kmz"):
                with zipfile.ZipFile(file_path, "r") as z:
                    kml_files = [name for name in z.namelist() if name.endswith(".kml")]
                    if kml_files:
                        with z.open(kml_files[0]) as kml_file:
                            kml_content = kml_file.read().decode("utf-8")
                            placemarks = baca_koordinat_kml(kml_content)
                    else:
                        print(f"❌ Tidak ada file KML dalam {file_name}")
                        continue

            for name, (lon, lat) in placemarks:
                kml_data.append({"name": name, "file": file_name, "lat": lat, "lon": lon})

        except Exception as e:
            print(f"❌ Gagal membaca {file_name}: {e}")

    return kml_data

# Simpan data KML di memori untuk pencarian cepat
KML_DATA = load_kml_data()
POINTS = [(d["lat"], d["lon"]) for d in KML_DATA]  # List koordinat dalam format (lat, lon)
KD_TREE = KDTree(POINTS)  # Buat KDTree dari koordinat

@app.route('/cari', methods=['GET'])
def cari_kml_terdekat():
    """Mencari file KML/KMZ terdekat berdasarkan koordinat input."""
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)

    if lat is None or lon is None:
        return jsonify({"error": "Koordinat tidak valid"}), 400

    # Cari titik terdekat dalam KD-Tree
    _, index = KD_TREE.query((lat, lon))
    hasil = KML_DATA[index]

    return jsonify({
        "file_terdekat": hasil["file"],
        "nama": hasil["name"],
        "lat": hasil["lat"],
        "lon": hasil["lon"],
        "jarak_meter": round(geodesic((hasil["lat"], hasil["lon"]), (lat, lon)).meters, 2)
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
