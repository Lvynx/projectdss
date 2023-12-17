import pandas as pd
import numpy as np
import streamlit as st
from prettytable import PrettyTable

# Import data from CSV
file_path = 'evaluasi_motor.csv'  # Update with the correct file path
df = pd.read_csv(file_path)

weights = {
    'harga': 0.4,
    'kecepatan_maksimal': 0.3,
    'konsumsi_bbm': 0.2,
    'penjualan': 0.1
}

# Langkah 1: Normalisasi matriks keputusan
df_normalized = df.copy()
norm_factors = np.sqrt((df.iloc[:, 2:] ** 2).sum(axis=0))  # Angka pembagi untuk setiap kriteria
df_normalized.iloc[:, 2:] = df.iloc[:, 2:].apply(lambda x: x / np.sqrt((x ** 2).sum()), axis=0)

# Langkah 1a: Menimbang matriks keputusan
df_weighted = df_normalized.copy()
df_weighted.iloc[:, 2:] = df_normalized.iloc[:, 2:] * np.array([weights[col] for col in df_normalized.columns[2:]])

# Langkah 2: Menentukan matriks solusi ideal positif (A+) dan solusi ideal negatif (A-)
A_pos = df_weighted.iloc[:, 2:].max().values
A_neg = df_weighted.iloc[:, 2:].min().values

# Langkah 3: Menghitung jarak Euclidean antara setiap alternatif dengan solusi ideal positif dan solusi ideal negatif
df_pos = np.sqrt(((df_weighted.iloc[:, 2:].values - A_pos) ** 2).sum(axis=1))
df_neg = np.sqrt(((df_weighted.iloc[:, 2:].values - A_neg) ** 2).sum(axis=1))

# Langkah 4: Menghitung skor kedekatan relatif (Closeness) dari setiap alternatif
closeness = df_neg / (df_pos + df_neg)

# Langkah 5: Menentukan peringkat alternatif berdasarkan skor kedekatan relatif tertinggi
df['closeness'] = closeness
df['rank'] = df['closeness'].rank(ascending=False)

# Streamlit UI
st.title("Evaluasi Motor menggunakan Metode TOPSIS")
st.write("Oleh 210012 - Aryan Dafi, 210018 - Luthfi Ramadhan, 210030 - Chairal Octavyanz, 210050 - Daffa Yusranizar")

# Pilihan menu
menu_option = st.selectbox("Pilih Menu:", ["-", "Topsis", "Kriteria", "Pengurutan Sesuai Kategori"])

# Menu Topsis
if menu_option == "-":
    st.write("Pilih menu di atas untuk memulai.")

elif menu_option == "Topsis":

    # Menampilkan Keputusan Ternormalisasi dan Terbobot
    st.header("Keputusan Ternormalisasi dan Terbobot:")
    st.table(df_weighted)

    # Menampilkan nama motor dan bobotnya dalam tabel
    table_data = {'Nama Motor': [], 'Bobot': []}
    for col, weight in weights.items():
        table_data['Nama Motor'].append(col.capitalize())
        table_data['Bobot'].append(weight)

    st.header("Bobot Kriteria:")
    st.table(pd.DataFrame(table_data))

    # Menampilkan angka pembagi (normalization factor)
    st.header("Angka Pembagi (Normalization Factor) untuk Setiap Kriteria:")
    st.table(pd.DataFrame({'Kriteria': df_normalized.columns[2:], 'Normalization Factor': norm_factors}))

    # Menampilkan tabel A+ (solusi ideal positif)
    st.header("Matriks Solusi Ideal Positif (A+):")
    st.table(pd.DataFrame([A_pos], columns=df_weighted.columns[2:]))

    # Menampilkan tabel A- (solusi ideal negatif)
    st.header("Matriks Solusi Ideal Negatif (A-):")
    st.table(pd.DataFrame([A_neg], columns=df_weighted.columns[2:]))

    # Langkah 4: Menampilkan tabel D_Max dan D_Min
    D_Max_Min = pd.DataFrame({'ID': df['id'], 'D_Max': df_pos, 'D_Min': df_neg})
    st.header("Matriks D_Max dan D_Min:")
    st.table(D_Max_Min)

    # Menampilkan hasil peringkat
    st.header("Hasil Peringkat:")
    ranked_df = df[['id', 'nama_motor', 'closeness', 'rank', 'harga', 'kecepatan_maksimal', 'konsumsi_bbm', 'penjualan']].sort_values(by='rank')
    st.table(ranked_df)

# Menu Kriteria
elif menu_option == "Kriteria":
    # Tentukan langkah (step) untuk setiap kriteria berdasarkan kisaran nilai
    step_harga = (df['harga'].max() - df['harga'].min()) / 100
    step_kecepatan = (df['kecepatan_maksimal'].max() - df['kecepatan_maksimal'].min()) / 100
    step_konsumsi = (df['konsumsi_bbm'].max() - df['konsumsi_bbm'].min()) / 100

    # Slider untuk kriteria harga
    harga_range = st.slider("Harga Range (Rp)", min_value=float(df['harga'].min()), max_value=float(df['harga'].max()), value=(float(df['harga'].min()), float(df['harga'].max())), step=step_harga)

    # Slider untuk kriteria kecepatan maksimal
    kecepatan_range = st.slider("Kecepatan Maksimal Range (km/h)", min_value=float(df['kecepatan_maksimal'].min()), max_value=float(df['kecepatan_maksimal'].max()), value=(float(df['kecepatan_maksimal'].min()), float(df['kecepatan_maksimal'].max())), step=step_kecepatan)

    # Slider untuk kriteria konsumsi BBM
    konsumsi_range = st.slider("Konsumsi BBM Range (km/l)", min_value=float(df['konsumsi_bbm'].min()), max_value=float(df['konsumsi_bbm'].max()), value=(float(df['konsumsi_bbm'].min()), float(df['konsumsi_bbm'].max())), step=step_konsumsi)

    # Filter data berdasarkan slider
    filtered_df = df[(df['harga'] >= harga_range[0]) & (df['harga'] <= harga_range[1]) &
                     (df['kecepatan_maksimal'] >= kecepatan_range[0]) & (df['kecepatan_maksimal'] <= kecepatan_range[1]) &
                     (df['konsumsi_bbm'] >= konsumsi_range[0]) & (df['konsumsi_bbm'] <= konsumsi_range[1])]

    # Hitung persentase rekomendasi untuk setiap motor
    filtered_df['recomendation_percentage'] = (1 - (filtered_df['rank'] - 1) / len(filtered_df)) * 100

    # Menampilkan tabel hasil peringkat hanya untuk 15 produk dengan rekomendation percentage tertinggi
    st.header("Hasil Peringkat:")
    ranked_df = filtered_df[['nama_motor', 'recomendation_percentage']].sort_values(by='recomendation_percentage', ascending=False).head(15)
    st.table(ranked_df)

    # Menampilkan tabel detail produk untuk motor rekomendasi tertinggi
    recommended_motor = filtered_df.loc[filtered_df['recomendation_percentage'].idxmax()]
    st.header("Detail Produk Motor Rekomendasi:")
    detail_table = recommended_motor[['nama_motor', 'recomendation_percentage', 'harga', 'kecepatan_maksimal', 'konsumsi_bbm']]
    st.table(detail_table)

elif menu_option == 'Pengurutan Sesuai Kategori':
    # Menu untuk menampilkan hasil peringkat
    st.header("Hasil Peringkat:")

    # Dropdown menu untuk memilih kriteria pengurutan
    sorting_criteria = st.selectbox("Pilih Kriteria Pengurutan:", list(weights.keys()))

    # Checkbox untuk menentukan urutan pengurutan (ascending atau descending)
    ascending_order = st.checkbox("Urutkan Secara Ascending", True)

    # Sorting DataFrame berdasarkan kriteria yang dipilih dan urutan
    sorted_df = df.sort_values(by=sorting_criteria, ascending=ascending_order)

    # Menampilkan tabel hasil peringkat
    st.table(sorted_df[['id', 'nama_motor', 'closeness', 'rank', sorting_criteria]])
