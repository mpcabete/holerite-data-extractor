import os
import pdfquery

pdf_path = os.path.join("pdfs", "Holerites.pdf")
pdf = pdfquery.PDFQuery(pdf_path)
if pdf is None:
    raise Exception("unable to load PDF")
i = 0
def read_table_field(field:str):
    label = pdf.pq('LTTextLineHorizontal:contains("'+field+'")')
    if label is None:
        raise Exception(field + "not found")
    left_corner = float(label.attr("x0"))
    bottom_corner = float(label.attr("y0"))
    result = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("%s, %s, %s, %s")'
        % (left_corner+400, bottom_corner , left_corner + 450, bottom_corner)
    ).text()
    return result 

while True:
    pdf.load(i)
    label = pdf.pq('LTTextLineHorizontal:contains("Data Pagamento")')
    if label is None:
        raise Exception("date not found")
    left_corner = float(label.attr("x0"))
    bottom_corner = float(label.attr("y0"))
    data = pdf.pq(
        'LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")'
        % (left_corner, bottom_corner - 10, left_corner + 50, bottom_corner)
    ).text()
    print(data)
    print("AUXILIO TRANSPORTE: ",read_table_field("AUXILIO TRANSPORTE"))
    print("CONTR.PREVID.RPPS-LC: ",read_table_field("CONTR.PREVID.RPPS-LC"))

    i += 1
