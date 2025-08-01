# 📋 Share Text Parser & Exporter

This Streamlit app parses unstructured textual data representing land share ownership and converts it into structured tabular form. Users can paste raw text (e.g., copied from land registry documents), and export the parsed result to **Excel**, **Word**, or **PDF**.

## ✅ Features

- Parse owner names and fractional shares from unstructured text.
- Automatically convert fractional shares (like `1/2`, `3/7`) into decimals.
- Export data to:
  - Excel (`.xlsx`)
  - Word (`.docx`) with styled tables
  - PDF (`.pdf`) with headers and formatted rows

---

## 📝 Sample Input Text

Paste the following kind of text into the input field:

गुरमीत सिंह पुत्र कुलवंत सिंह निवासी अमृतसर
603/3076 भाग

हरजीत कौर पत्नी गुरमीत सिंह
गांव मजीठा
500/3076 भाग

जसविंदर सिंह पुत्र गुरमीत सिंह
गांव मजीठा

मनप्रीत कौर पत्नी जसविंदर सिंह
700/3076 भाग

This input will be parsed into:

| Owner Name + Narration                      | Share Fraction   | Share (Decimal) |
|--------------------------------------------|------------------|------------------|
| गुरमीत सिंह पुत्र कुलवंत सिंह निवासी अमृतसर | 603/3076 भाग     | 0.1961           |
| हरजीत कौर पत्नी गुरमीत सिंह गांव मजीठा     | 500/3076 भाग     | 0.1625           |
| जसविंदर सिंह पुत्र गुरमीत सिंह गांव मजीठा   | *(blank)*        | *(blank)*        |
| मनप्रीत कौर पत्नी जसविंदर सिंह             | 700/3076 भाग     | 0.2275           |

> ℹ️ Owners without associated fractions are still listed but shown without share values.

---

## 🚀 How to Use

1. Run the app:
   ```bash
   streamlit run app.py
