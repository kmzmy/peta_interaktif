import os
import zipfile

# Folder tempat menyimpan file KMZ
folder_path = "C:/Users/admin/peta-interaktif/data"

# Loop semua file di dalam folder
for filename in os.listdir(folder_path):
    if filename.lower().endswith(".kmz"):  # Cek file KMZ
        kmz_path = os.path.join(folder_path, filename)  
        
        # Nama file output (ubah dari .kmz ke .kml)
        kml_output_path = os.path.join(folder_path, filename.replace(".kmz", ".kml"))

        # Ekstrak file KML dari KMZ
        with zipfile.ZipFile(kmz_path, 'r') as z:
            # Cari file .kml dalam ZIP
            kml_files = [f for f in z.namelist() if f.endswith(".kml")]
            
            if kml_files:
                # Ambil file KML pertama dan ekstrak isinya
                with z.open(kml_files[0]) as kml_file:
                    kml_content = kml_file.read().decode("utf-8")
                
                # Simpan hasil sebagai file .kml
                with open(kml_output_path, "w", encoding="utf-8") as output_file:
                    output_file.write(kml_content)
                
                print(f"✅ Berhasil mengonversi: {filename} → {filename.replace('.kmz', '.kml')}")
            else:
                print(f"❌ Tidak ditemukan file .kml dalam {filename}")