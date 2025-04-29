## 📘 README.md – Auto Swap & Liquidity Bot

### 📌 Deskripsi
Bot ini secara otomatis:
- Melakukan **20 transaksi swap WETH → KYO** setiap sesi
- Menambahkan **liquidity WETH + KYO** ke pool
- **Sleep 20–24 jam**, lalu **mengulang** proses tanpa batas (looping selamanya)

Dibuat khusus untuk jaringan **Soneium Testnet Minato**.

---

### 🛠️ Fitur Utama
- 🔁 Loop otomatis: swap → add liquidity → sleep → ulang
- 🔐 Menggunakan private key dari file `wallet.txt`
- 🔄 Transaksi aman dengan gas price dinamis & retry jika gagal
- 📂 ABI semua kontrak disimpan dalam satu file `abi.json`
- 🧪 Dirancang untuk testnet (tidak pakai dana riil)

---

### 📁 Struktur File
```
auto-swap-bot/
├── bot.py         ← Script utama bot
├── wallet.txt     ← Private key (tanpa tanda kutip)
└── abi.json       ← ABI semua kontrak (WETH, KYO, Router, Position Manager)
```

---

### 📦 Persiapan & Instalasi

1. **Clone repo** atau buat folder:
   ```bash
   git clone https://github.com/airdrop-org/kyo-finance.git
   ```

2. **Install dependency Python**:
   ```bash
   pip install web3 eth-account
   ```

3. **Buat file `wallet.txt`** dan tempel private key kamu (format: `0xabc...`)

4. **Salin file `abi.json`** dari isi yang tersedia di repo ini.

---

### ▶️ Menjalankan Bot

```bash
python3 bot.py
```

Output akan menampilkan:
- TX Hash untuk `approve`, `swap`, dan `add liquidity`
- Jeda acak antar swap
- Waktu tunggu sebelum sesi berikutnya

---

### ⚙️ Cara Kerja Bot

1. Melakukan `approve` untuk Router dan PositionManager
2. 20x swap acak: 0.0001–0.00015 WETH → KYO
3. Tambahkan semua WETH dan 1.83 KYO ke liquidity pool
4. Sleep selama 20–24 jam
5. **Ulangi lagi**

---

### 🛡️ Keamanan
- Jangan gunakan wallet utama
- Simpan `wallet.txt` dengan aman
- Hanya untuk testnet, **jangan pakai ETH asli**

---

### 🧠 Troubleshooting

| Masalah                                       | Solusi                                               |
|----------------------------------------------|------------------------------------------------------|
| `replacement transaction underpriced`        | Bot otomatis retry dengan gas price lebih tinggi     |
| `abi.json` not found                         | Pastikan file `abi.json` ada di direktori yang sama  |
| `insufficient funds`                         | Pastikan wallet testnet kamu punya cukup ETH WETH    |
| Swap tidak berhasil (KYO tidak keluar)       | Periksa `UniversalRouter` ABI benar atau tidak       |

---

### 📎 Catatan Penting
- Bot ini bersifat looping tanpa henti (loop forever)
- Jika ingin menghentikan bot: tekan `Ctrl + C`
- Ingin log ke file? Bisa ditambahkan ke `bot.py`
