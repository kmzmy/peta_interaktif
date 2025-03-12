from fastkml import kml

def test_kml(file_path):
    with open(file_path, 'rb') as f:
        doc = f.read()

    # Hapus encoding UTF-8 jika ada di dalam file KML
    doc = doc.replace(b'<?xml version="1.0" encoding="UTF-8"?>', b'')

    k = kml.KML()
    k.from_string(doc)  # Jika tidak error, berarti perbaikan berhasil

    print("✅ File KML berhasil dibaca!")

# Uji dengan file KML yang ada
test_kml(r"C:\Users\admin\peta-interaktif\data\contoh.kml")