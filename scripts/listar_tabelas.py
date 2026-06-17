import zipfile, xml.etree.ElementTree as ET

with zipfile.ZipFile('Lab02_BDD_Distribuidas_.docx', 'r') as z:
    root = ET.fromstring(z.read('word/document.xml'))

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

for tbl_idx, tbl in enumerate(root.iter(f'{{{W}}}tbl')):
    rows = list(tbl.iter(f'{{{W}}}tr'))
    has_registo = False
    for row in rows:
        for cell in row.iter(f'{{{W}}}tc'):
            for t in cell.iter(f'{{{W}}}t'):
                if t.text and 'REGISTO DE RESULTADOS' in t.text:
                    has_registo = True
                    break

    if not has_registo:
        continue

    print(f'\n═══ TABLE {tbl_idx} ═══')
    for row_idx, row in enumerate(rows):
        cells = list(row.iter(f'{{{W}}}tc'))
        cell_texts = []
        for c in cells:
            texts = []
            for t in c.iter(f'{{{W}}}t'):
                if t.text:
                    t_clean = t.text.strip()
                    if t_clean:
                        texts.append(t_clean)
            cell_texts.append(' | '.join(texts) if texts else '')
        print(f'  Row {row_idx}: {cell_texts}')
