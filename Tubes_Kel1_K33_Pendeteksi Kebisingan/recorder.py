import numpy as np
import sounddevice as sd
import math
import soundfile as sf


#KAMUS
# SAMPLE_RATE (int) = variabel untuk menyimpan frekuensi sampling audio
# CHANNELS (int) = variabel untuk menyimpan jumlah channel audio yang dipakai
# DURATION (int) = variabel untuk menyimpan durasi rekaman suara dalam detik
# berisik (bool) = variabel untuk menentukan apakah ruangan terdeteksi bising atau tidak
# data_nama_suara (list string) = array untuk menyimpan daftar nama atau jenis suara yang bisa dipilih pengguna
# data_db_suara (list int) = array untuk menyimpan perkiraan tingkat kebisingan (dB) dari setiap jenis suara
# array_pilihan_suara (list int) = array berisi  nilai desibel dari setiap jenis suara yang dipilih
# array_lama_durasi (list int) = array berisi durasi paparan setiap jenis suara yang dipilih dalam satuan detik

# aman (bool) = variabel untuk menentukan apakah tingkat kebisingan dan durasi paparan masih memenuhi batas aman
# durasi_max (int/float) = variabel batas maksimum durasi paparan berdasarkan tingkat kebisingan
# bising_max (int) = variabel batas maksimum tingkat kebisingan (dB) dalam perhitungan NAB
# i (int) = variabel iterasi dalam proses loop

# frame_count (int) = variabel berisi jumlah frame audio yang akan direkam berdasarkan sample rate dan durasi perekaman
# audio (numpy array) = variabel berisi data hasil perekaman suara dari mikrofon
# peak (int) = variabel berisi nilai amplitudo maksimum dari hasil perekaman suara
# THRESHOLD (int) = variabel untuk menyimpan batas amplitudo dalam menentukan apakah suatu ruangan terdeteksi bising atau tidak
# sample_rate (int) = variabel untuk menyimpan frekuensi sampling dari file audio alarm yang dibaca

# index (int) = variabel penghitung untuk menunjukkan urutan data suara yang sedang dimasukkan
# selesai (bool) = variabel untuk menentukan apakah proses pengamatan sudah selesai atau masih berlanjut
# lanjut (int) = variabel untuk menyimpan pilihan pengguna untuk melanjutkan atau mengakhiri proses pengamatan
# total_durasi (int) = variabel untuk menyimpan jumlah keseluruhan durasi paparan dari semua jenis suara
# isi_log (float) = variabel untuk menyimpan hasil perhitungan energi suara berbobot durasi sebelum dikonversi menjadi desibel
# desibel_gabungan (float) = variabel untuk menyimpan hasil perhitungan tingkat kebisingan gabungan dari seluruh sumber suara
# lama_berada (float) = variabel berisikan durasi pengguna berada di area pengamatan dalam detik
# keamanan (bool) = variabel berisikan hasil pemeriksaan apakah paparan kebisingan termasuk aman atau berbahaya

# input_suara (int) = variabel berisi nomor jenis suara yang dipilih oleh pengguna
# input_durasi (int) = variabel berisi durasi paparan suara yang dimasukkan oleh pengguna dalam detik

# jawaban (int) = variabel berisi pilihan pengguna untuk melakukan pengukuran suara secara langsung atau melalui pengamatan
# pilihan (int) = variabel berisi pilihan pengguna untuk mengulangi pengukuran atau mengakhiri program


SAMPLE_RATE = 44100
CHANNELS = 1
DURATION = 3
berisik = False


data_nama_suara = [
 "Percakapan Di Kantor (pelan)",
    "Percakapan di Kantor (keras)",
    "Alat-Alat listrik Bising",
    "Mesin-Mesin Pabrik Bising",
    "Radio Keras ",
    "Sistem HVAC/AC",
    "Printer/Fotokopi",
    "Komputer/Server",
    "Telepon/Notifikasi ",
    "Furniture (kursi/laci)",
    "Penyedot debu",
    "Pintu",
    "Lalu Lintas Kendaraan Ringan",
    "Lalu Lintas Kendaraan Berat",
    "Klakson Kendaraan",
    "Kegiatan Konstruksi"
]

data_db_suara = [
    50,
    70,
    100,
    120,
    90,
    55,
    65,
    45,
    70,
    60,
    65,
    70,
    75,
    85,
    90,
    95
]

array_pilihan_suara = []
array_lama_durasi=[]

def batas_NAB (lama_berada, desibel_gabungan):
    aman = False
    durasi_max = 57600
    bising_max = 82
    i = 0

    if desibel_gabungan <= 82:
        aman = True
    else:
        while bising_max <= desibel_gabungan:
            durasi_max = 57600/(2**i)
            bising_max = 82 + 3*i

            if (desibel_gabungan <= bising_max) and (lama_berada <= durasi_max):
                aman = True
            else:
                aman = False

                break
            i+=1

    return aman

def selesai():
    print("===============================")
    print("     Program Selesai")
    print("===============================")

def hitung_suara():
    frame_count = int(DURATION * SAMPLE_RATE)

    print(f"Recording {DURATION} seconds...")
    audio = sd.rec(frame_count,
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype="int16")
    sd.wait()
    print("Recording finished.")
    print("")

    peak = int(np.abs(audio).max())
    print(f"peak amplitude: {peak} out of 32767")

    if peak == 0:
        print("WARNING: every sample is zero. The microphone captured silence.")

    THRESHOLD = 5000

    if peak > THRESHOLD:
        print("\033[31m===============================\033[0m")
        print("\033[31mRUANGAN TERDETEKSI BISING\033[0m")
        print("\033[31m===============================\033[0m")
        print("")
        audio, sample_rate = sf.read("audio/alarm.wav")
        sd.play(audio, sample_rate)
        sd.wait()
        return True
    else:
        print("Ruangan terdeteksi tidak bising.")
        print("")
        return False

def pengamatan():
    index = 0
    selesai = False
    while not selesai:
        pengamatan_input_data(index)
        print("Apakah masih ada suara lain?")
        while True:
                try:
                    lanjut = int(input("Ketik '1' untuk iya, ketik '2' untuk tidak: "))
                    if lanjut in (1, 2):
                        break
                    print("\033[31mInput harus berupa bilangan bulat '1' atau '2'!\033[0m")
                except ValueError:
                    print("\033[31mInput harus berupa bilangan bulat '1' atau '2'!\033[0m")

        if lanjut == 1:
            index += 1
        elif lanjut == 2:
            selesai = True
    total_durasi = sum(array_lama_durasi)

    isi_log = 0

    for i in range (len(array_pilihan_suara)):
        isi_log += (array_lama_durasi[i]/total_durasi) * 10 ** (0.1 * array_pilihan_suara[i])

    desibel_gabungan = 10 * math.log10(isi_log)

    while True:
            try:
                lama_berada = float(input("Masukkan berapa lama anda berada dalam area ini (detik): "))
                if lama_berada >= 0:
                    break
                print("\033[31mInput harus berupa bilangan positif!\033[0m")
            except ValueError:
                        print("\033[31mInput harus berupa bilangan positif!\033[0m")

    keamanan = batas_NAB(lama_berada, desibel_gabungan)

    if keamanan == True:
        print("Desibel Gabungannya adalah: ", desibel_gabungan, ". suara ini aman")

    else: 
        print("Desibel Gabungannya adalah: ", desibel_gabungan, ". Ini berbahaya")

def pengamatan_input_data(index):
    print("DATA SUARA:")
    for i in range (len(data_db_suara)):
        print(i+1,'.', end=" ")
        print(data_nama_suara[i])

    while True:
            try:
                input_suara = int(input("Ketik 1 angka yang berisikan suara yang kamu dengar saat ini: "))
                if input_suara in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16):
                    break
                print("\033[31mInput harus berupa bilangan bulat 1 sampai 16!\033[0m")
            except ValueError:
                print("\033[31mInput harus berupa bilangan bulat 1 sampai 16!\033[0m")
    
    while True:
                try:
                    input_durasi = int(input("Berapa lama kamu sudah mendengarnya? (detik): "))
                    if input_durasi >= 0:
                        break
                    print("\033[31mInput harus berupa bilangan positif!\033[0m")
                except ValueError:
                            print("\033[31mInput harus berupa bilangan positif!\033[0m")

    array_pilihan_suara.append(data_db_suara[input_suara-1])
    array_lama_durasi.append(input_durasi)

def main():
    print("===============================")
    print("  Program pendeteksi suara")
    print("===============================")
    print("Deskripsi:")
    print("Program ini dibuat untuk mendeteksi kebisingan ruangan melalui 2 cara, yaitu dengan merekam suara langsung atau dengan memasukkan data.\nUntuk program merekam, ruangan akan dianggap bising jika amplitudo suara melebihi 5000,\nSedangkan dalam program memasukkan data/pengamatan, standar kebisingan didasarkan Keputusan Menteri Tenaga Kerja No. KEP-51/MEN/1999")
    print("")
    print("Apakah ingin mengukur secara langsung atau melalui pengamatan?")
    while True:
                try:
                    jawaban = int(input("Ketik '1' jika ingin secara langsung, '2' jika melalui pengamatan: "))
                    if jawaban in (1, 2):
                        break
                    print("\033[31mInput harus berupa bilangan bulat '1' atau '2'!\033[0m")
                except ValueError:
                    print("\033[31mInput harus berupa bilangan bulat '1' atau '2'!\033[0m")

    print("===============================")
    if jawaban == 1:
        berisik = hitung_suara()

        if berisik:
            print("Apakah ingin diulang hingga ruangan tidak bising?")
            while True:
                try:
                    pilihan = int(input("Ketik '1' untuk iya, ketik '2' untuk tidak: "))
                    if pilihan in (1, 2):
                        break
                    print("\033[31mInput harus berupa bilangan bulat '1' atau '2'!\033[0m")
                except ValueError:
                    print("\033[31mInput harus berupa bilangan bulat '1' atau '2'!\033[0m")
            
            if pilihan == 1:
                while berisik:
                    print("===============================")
                    berisik = hitung_suara()     

            elif pilihan == 2:
                selesai()

            else: 
                print("")
                print("Input harus berupa bilangan bulat '1' atau '2'!")

        if not berisik:
            selesai()

    elif jawaban == 2:
        pengamatan()

    else:
        print("")
        print("Input Salah")

main()