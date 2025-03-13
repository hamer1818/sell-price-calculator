# Satış Fiyat Hesaplayıcı

Bu uygulama, satış yapan kişilerin ürün fiyatlandırmasını kolaylaştırmak amacıyla geliştirilmiştir. Alış fiyatı, komisyon oranı, kargo ücreti ve kar marjı gibi faktörleri hesaba katarak optimal satış fiyatını belirler.

## Özellikler

- **Manuel Hesaplama:** Tekli ürünler için anlık satış fiyatı hesaplama
- **Toplu Hesaplama:** Excel dosyasından birden fazla ürün için toplu fiyat hesaplama
- **Özelleştirilebilir Parametreler:** Komisyon, kargo ve kar oranları için esnek ayarlar
- **Dışa Aktarma:** Sonuçları Excel formatında dışa aktarabilme

## Gereksinimler

- Python 3.6+
- PyQt6
- pandas
- xlsxwriter

## Kurulum

```bash
git clone https://github.com/kullaniciadiniz/sell_price_calculator.git
cd sell_price_calculator
pip install -r requirements.txt
```

## Kullanım

```bash
python main.py
```

## Excel Dosya Formatı

Excel dosyanızın en az "Alış Fiyatı" sütununu içermesi gerekmektedir. İsteğe bağlı olarak aşağıdaki sütunlar eklenebilir:

- **Ürün Adı**: Ürün tanımı (isteğe bağlı)
- **Komisyon**: Yüzde olarak komisyon oranı (varsayılan: %10)
- **Kargo Ücreti**: TL olarak kargo ücreti (varsayılan: 30₺)
- **Kar**: Yüzde olarak kar marjı (varsayılan: %20)

## Lisans

MIT
