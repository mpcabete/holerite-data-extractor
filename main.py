import os
import pdfquery

pdf_path = os.path.join("pdfs", "Holerites.pdf")
pdf = pdfquery.PDFQuery(pdf_path)
if pdf is None:
    raise Exception("unable to load PDF")
i = 0
def read_table_field(field:str):
    label = pdf.pq('LTTextLineHorizontal:contains("'+field+'")')
    if(len(label)==0):
        return ""
    if label is None:
        raise Exception(field + "not found")

    if len(label) >1:
        print("found ",len(label), " elements")
        found = False
        for element in label:
            l = pdf.pq(element)
            left_corner = float(l.attr("x0"))
            bottom_corner = float(l.attr("y0"))
            offset = 190
            nat = pdf.pq(
                'LTTextLineHorizontal:overlaps_bbox("%s, %s, %s, %s")'
                % (left_corner+offset, bottom_corner+2 , left_corner + offset+10, bottom_corner+3)
            ).text()
            print("nat",nat)
            if "N" in nat:
                label = l
                found = True
                break

        if not found:
            print("last nat before error",nat)
            raise Exception("Nat. N not found for any entry")



    left_corner = float(label.attr("x0"))
    bottom_corner = float(label.attr("y0"))
    result = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("%s, %s, %s, %s")'
        % (left_corner+400, bottom_corner , left_corner + 450, bottom_corner)
    ).text()
    return result 

while True:
    pdf.load(i)
    print("Page ",i)
    label = pdf.pq('LTTextLineHorizontal:contains("Data Pagamento")')
    left_corner = float(label.attr("x0"))
    bottom_corner = float(label.attr("y0"))
    data = pdf.pq(
        'LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")'
        % (left_corner, bottom_corner - 10, left_corner + 50, bottom_corner)
    ).text()
    print(data)
    print("AUXILIO TRANSPORTE: ",read_table_field("AUXILIO TRANSPORTE"))
    print("CONTR.PREVID.RPPS-LC: ",read_table_field("CONTR.PREVID.RPPS-LC"))

    labels = pdf.pq('LTTextLineHorizontal:contains("Total")')
    for label in labels:
        label = pdf.pq(label)
        if "Vencimentos" in label.parent().text():
            break
    
    print("Vencimentos",len(label))
    left_corner = float(label.attr("x0"))
    bottom_corner = float(label.attr("y0"))
    data = pdf.pq(
        'LTTextLineHorizontal:overlaps_bbox("%s, %s, %s, %s")'
        % (left_corner, bottom_corner - 20, left_corner + 40, bottom_corner-15)
    ).text()
    print(data)

    i += 1

