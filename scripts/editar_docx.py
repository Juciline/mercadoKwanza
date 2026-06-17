import zipfile, xml.etree.ElementTree as ET, os, shutil

SRC = 'Lab02_BDD_Distribuidas_.docx'
TMP = 'Lab02_BDD_Distribuidas_.tmp.docx'
BAK = 'Lab02_BDD_Distribuidas_.backup.docx'

# Backup
shutil.copy2(SRC, BAK)

with zipfile.ZipFile(SRC, 'r') as z:
    xml = z.read('word/document.xml')
    root = ET.fromstring(xml)

ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
changes = []

# Collect all text elements with their index
all_elems = []
for i, elem in enumerate(root.iter()):
    tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
    if tag == 't':
        all_elems.append((i, elem))

# 1. Replace "50000" -> "90000" (ITEM_VENDA count)
for i, elem in all_elems:
    if elem.text and elem.text.strip() == '50000':
        elem.text = elem.text.replace('50000', '90000')
        changes.append(f'[idx {i}] "50000" -> "90000"')

# 2. Replace standalone "nenhum" -> "2" (but not part of larger words)
for i, elem in all_elems:
    if elem.text and elem.text.strip() == 'nenhum':
        elem.text = '2'
        changes.append(f'[idx {i}] "nenhum" -> "2"')

# 3. Find the blank elements after "COUNT(*) FROM VENDA (Luanda)" and fill
for idx, (i, elem) in enumerate(all_elems):
    if elem.text and '*) FROM VENDA (Luanda)' in elem.text:
        # The next non-empty text element that is just spaces should be 30000
        for j in range(idx + 1, min(idx + 5, len(all_elems))):
            next_idx, next_elem = all_elems[j]
            if next_elem.text and next_elem.text.strip() == '':
                next_elem.text = '30000'
                changes.append(f'[idx {next_idx}] VENDA count -> "30000"')
                break

# 4. Find the blank elements after "COUNT(*) FROM CLIENTE (Luanda)" and fill
for idx, (i, elem) in enumerate(all_elems):
    if elem.text and '*) FROM CLIENTE (Luanda)' in elem.text:
        for j in range(idx + 1, min(idx + 5, len(all_elems))):
            next_idx, next_elem = all_elems[j]
            if next_elem.text and next_elem.text.strip() == '':
                next_elem.text = '5000'
                changes.append(f'[idx {next_idx}] CLIENTE count -> "5000"')
                break

# 5. Find "(S/N)" after "carregados automaticamente" and fill the blank before it
for idx, (i, elem) in enumerate(all_elems):
    if elem.text and '(S/N)' in elem.text and 'carregados' not in elem.text:
        # Look backwards for the label "carregados automaticamente"
        for lookback in range(idx - 1, max(0, idx - 10), -1):
            lb_idx, lb_elem = all_elems[lookback]
            if lb_elem.text and 'automaticamente' in lb_elem.text:
                # Found it! The blank element is right after (S/N)
                # Actually, let me look for the blank right after (S/N)
                for k in range(idx + 1, min(idx + 5, len(all_elems))):
                    blank_idx, blank_elem = all_elems[k]
                    if blank_elem.text and blank_elem.text.strip() == '':
                        blank_elem.text = 'S'
                        changes.append(f'[idx {blank_idx}] Carregado automaticamente -> "S"')
                        break
                break

# Write modified XML
xml_str = ET.tostring(root, encoding='unicode')
with zipfile.ZipFile(TMP, 'w', zipfile.ZIP_DEFLATED) as zout:
    with zipfile.ZipFile(SRC, 'r') as zin:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'word/document.xml':
                data = xml_str.encode('utf-8')
            zout.writestr(item, data)

os.replace(TMP, SRC)

print(f'Total alteracoes: {len(changes)}')
for c in changes:
    print(f'  {c}')
print(f'\nBackup: {BAK}')
