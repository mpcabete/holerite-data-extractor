import os
import pdfquery
from pandas import DataFrame
import pandas as pd
import json

PDFS_DIR="pdfs"
SHEETS_DIR="tabelas"


# Open and read the JSON file
with open('alicotas.json', 'r') as file:
    alicotas = json.load(file)

# Print the data
def get_alicota(ano,vencimentos):
    alicotas_correntes = alicotas.get(ano)
    if alicotas_correntes is None:
        alicotas_correntes = alicotas.get("2022")

    for faixa in alicotas_correntes["faixas"]:
        if faixa["baseCalculo"] == "infinity":
            return (faixa["deducao"],faixa["aliquota"]/100)

        if float(vencimentos)>faixa["baseCalculo"]:
            continue
        else:
            return (faixa["deducao"],faixa["aliquota"]/100)

def extract_value_from_position(pdf ,label, x_offset, y_offset, width = 50, height = 50,method="overlaps"):
    left_corner = float(label.attr("x0"))
    bottom_corner = float(label.attr("y0"))
    result = pdf.pq(
        'LTTextLineHorizontal:%s_bbox("%s, %s, %s, %s")'
        % (method,
            left_corner + x_offset,
           bottom_corner + y_offset,
           left_corner + x_offset+width,
           bottom_corner+y_offset+height
       )
    ).text()
    return result

def br_string_to_float(value_str):
    return float(value_str.split(' ')[0].replace(".","").replace(",","."))

def read_auxilio_table_field(pdf,field: str):
    labels = pdf.pq('LTTextLineHorizontal:contains("' + field + '")')
    if len(labels) == 0:
        return ""
    total = 0
    for element in labels:
        label = pdf.pq(element)
        result = extract_value_from_position(pdf,label, 400, 0, height=0)
        result_float = br_string_to_float(result)
        total += result_float

    return total

def read_contrib_table_field(pdf,field: str):
    label = pdf.pq('LTTextLineHorizontal:contains("' + field + '")')
    if len(label) == 0:
        return ""

    if len(label) > 1:
        found = False
        for element in label:
            l = pdf.pq(element)
            nat = extract_value_from_position(pdf,l,190,2,width=10,height=1)
            if "N" in nat:
                label = l
                found = True
                break

        if not found:
            raise Exception("Nat. N not found for any entry")

    result = extract_value_from_position(pdf,label,400,0,width=50,height=0)
    result_float = br_string_to_float(result)
    return result_float

def process_pdf(pdf_path,sheet_path):
    pdf = pdfquery.PDFQuery(pdf_path) 
    if pdf is None:
        raise Exception("unable to load PDF")
    i = 0

    data_pagamento = []
    auxilio_transporte = []
    contrib_previd = []
    vencimentos = []
    total_pages = pdf.doc.catalog['Pages'].resolve()['Count']
    for i in range(total_pages):
        # if(i == 4):
        #     break
        pdf.load(i)
        print("Processando pagina ", i+1)
        label = pdf.pq('LTTextLineHorizontal:contains("Data Pagamento")')
        data = extract_value_from_position(pdf,label,0,-10,width=50,height=10,method="in")
        data_pagamento.append(data)
        auxilio_transporte.append(read_auxilio_table_field(pdf,"AUXILIO TRANSPORTE"))
        contrib_previd.append(read_contrib_table_field(pdf,"CONTR.PREVID.RPPS-LC"))

        labels = pdf.pq('LTTextLineHorizontal:contains("Total")')
        for label in labels:
            label = pdf.pq(label)
            if "Vencimentos" in label.parent().text():
                break

        data = extract_value_from_position(pdf,label, 0, -20, width=40, height=5)
        value = br_string_to_float(data)
        vencimentos.append(value)

    df = DataFrame({
        "Data Pagamento": data_pagamento,
        "Vencimentos":vencimentos,
        "Contribuicao previdencia": contrib_previd,
        "OUTRAS DEDUÇÕES" : 0,
        "Auxilio Transporte": auxilio_transporte,
    })

    df["Ano"] = df["Data Pagamento"].str.split("/").str[-1]

    df["Data Pagamento"] = pd.to_datetime(df["Data Pagamento"],format="%d/%m/%Y")
    df.sort_values(by="Data Pagamento", ascending=True, inplace=True)
    df["Data Pagamento"]= df["Data Pagamento"].dt.strftime('%d/%m/%Y')
    df["DPTE"] = 189.59
    df[['PARCELAS A DEDUZIR','ALIQUOTA IR']] = df.apply(
        lambda row: get_alicota(row['Ano'],row['Vencimentos']), 
        axis=1,
        result_type='expand'
    )
    print(df)

    df.to_excel(sheet_path, index=False)

pdf_files = os.listdir(PDFS_DIR)

if not os.path.exists(SHEETS_DIR):
   os.makedirs(SHEETS_DIR)

for pdf_file in pdf_files:
    pdf_path = os.path.join("pdfs",pdf_file)
    process_pdf(pdf_path,os.path.join(SHEETS_DIR,f"{os.path.splitext(pdf_file)[0]}.xlsx"))
