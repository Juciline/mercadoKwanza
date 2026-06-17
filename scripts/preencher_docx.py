import zipfile, xml.etree.ElementTree as ET, os
from unidecode import unidecode

SRC = 'Lab02_BDD_Distribuidas_.docx'
TMP = 'Lab02_BDD_Distribuidas_.tmp.docx'

with zipfile.ZipFile(SRC, 'r') as z:
    root = ET.fromstring(z.read('word/document.xml'))

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def make_paragraph(text):
    p = ET.Element(f'{{{W}}}p')
    r = ET.SubElement(p, f'{{{W}}}r')
    t = ET.SubElement(r, f'{{{W}}}t')
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return p

table_fills = {
    'FASE-2': {
        'fragmento luanda': '10011',
        'fragmento benguela': '9937',
        'fragmento huambo': '10052',
        'soma dos 3 fragmentos = total?': 'S',
        'query de fragmentacao vertical': 'S',
    },
    'FASE-3': {
        'slave_io_running -- benguela': 'Yes',
        'slave_sql_running -- benguela': 'Yes',
        'seconds_behind_master -- benguela': '0',
        'slave_io_running -- huambo': 'Yes',
        'seconds_behind_master -- huambo': '0',
        'benguela? (s/n)': 'S',
        'huambo? (s/n)': 'S',
    },
    'FASE-3B': {
        'slave quando o master estava pausado': 'Leituras funcionaram normalmente',
        'escrever com o master pausado': 'Conexao recusada (container paused)',
        'slave sincronizou automaticamente': 'S',
    },
    'FASE-4A': {
        'antes do update': '450',
        'apos update (antes do rollback)': '445',
        'apos rollback (igual ao inicial': '450 (Sim)',
        'apos commit': '445',
    },
    'FASE-4B': {
        'stock em benguela antes da transacao': '108',
        'stock em benguela apos a transacao (sucesso)': '98',
        'vendas em luanda antes': '30000',
        'vendas em luanda apos (sucesso)': '30001',
        'rollback executado': 'S',
        'stock em benguela apos rollback (igual ao inicial': '98 (Sim)',
    },
    'P1-A': {
        'count produto no luanda antes': '211',
        'count produto no benguela antes': '211',
        'count produto no benguela imediatamente': '215',
        'count produto no benguela apos 5 segundos': '216',
        'seconds_behind_master maximo': '0',
        'stock total fragmento luanda': '266334',
        'stock total fragmento benguela': '259966',
    },
    'P1-B': {
        'count cliente antes dos inserts': '5000',
        'count cliente apos inserts (luanda)': '5003',
        'count cliente apos 5s (benguela': '5003',
        'soma dos 3 fragmentos = total geral': 'S',
        'provincia com maior faturamento medio': 'Benguela',
        'seconds_behind_master maximo': '0',
    },
    'P2-A': {
        'stock produto em benguela antes': '98',
        'stock produto em benguela apos transacao ok': '88',
        'stock produto em benguela apos rollback': '88 (Sim)',
        'vendas em luanda antes': '30001',
        'vendas em luanda apos transacao ok': '30002',
        'vendas em luanda apos rollback': '30002 (Sim)',
        'log foi correctamente impresso': 'S',
    },
    'P2-B': {
        'stock huambo antes': '161',
        'stock huambo apos transferencia ok': '141',
        'stock benguela antes': '88',
        'stock benguela apos transferencia ok': '108',
        'stock insuficiente': 'S',
        'stock huambo apos rollback': '141 (Sim)',
        'stock benguela apos rollback': '108 (Sim)',
    },
    'P3-A': {
        'documentos migrados para mongodb': '30002',
        'tempo agregacao mongodb': '45.54 ms',
        'tempo query mysql': '55.68 ms',
        'qual foi mais rapido': 'MongoDB',
        'lojas no resultado': '15',
        'loja com maior total': 'Loja 14',
    },
    'P3-B': {
        'clientes migrados com vendas': '5003',
        'tempo consulta mongodb': '19.64 ms',
        'tempo consulta mysql': '61.94 ms',
        'qual foi mais rapido': 'MongoDB',
        'cliente com mais compras (mysql)': 'Antonio Gomes',
        'cliente com mais compras (mongodb': 'Antonio Gomes',
    },
}

changes = 0
for tbl in root.iter(f'{{{W}}}tbl'):
    rows = list(tbl.iter(f'{{{W}}}tr'))

    header_text = ''
    for row in rows[:3]:
        for cell in row.iter(f'{{{W}}}tc'):
            for t in cell.iter(f'{{{W}}}t'):
                if t.text:
                    header_text += t.text
    header_norm = unidecode(header_text).lower()

    current_fase = None
    for fk in table_fills:
        if fk.lower() in header_norm:
            current_fase = fk
            break
    if current_fase is None:
        continue

    fills = table_fills[current_fase]

    for row in rows:
        cells = list(row.iter(f'{{{W}}}tc'))
        if len(cells) < 2:
            continue

        col1_text = ''
        for t in cells[0].iter(f'{{{W}}}t'):
            if t.text:
                col1_text += t.text
        col1_norm = unidecode(col1_text).lower()

        matched_val = None
        for key, val in fills.items():
            if key in col1_norm:
                matched_val = val
                break
        if matched_val is None:
            continue

        col2_has_text = False
        for t in cells[1].iter(f'{{{W}}}t'):
            if t.text and t.text.strip():
                col2_has_text = True
                break

        if col2_has_text:
            continue

        for p in list(cells[1].iter(f'{{{W}}}p')):
            cells[1].remove(p)
        cells[1].append(make_paragraph(matched_val))
        print(f'  [{current_fase}] "{col1_text.strip()[:50]}" -> "{matched_val}"')
        changes += 1

# Fill comparison tables (MySQL vs MongoDB)
for tbl in root.iter(f'{{{W}}}tbl'):
    rows = list(tbl.iter(f'{{{W}}}tr'))
    header_text = ''
    for row in rows[:3]:
        for cell in row.iter(f'{{{W}}}tc'):
            for t in cell.iter(f'{{{W}}}t'):
                if t.text:
                    header_text += t.text
    header_norm = unidecode(header_text).lower()

    if 'modelo de dados' not in header_norm:
        continue

    comp_fills = {
        'modelo de dados': ('Relacional (tabelas)', 'Documentos (NoSQL)'),
        'transacoes acid': ('Sim (ACID)', 'Nao (BASE)'),
        'escalabilidade horizontal': ('Limitada (master-slave)', 'Sim (nativa)'),
        'posicao no cap': ('CP', 'AP'),
        'consistencia dos dados': ('Forte (ACID)', 'Eventual (BASE)'),
        'velocidade em agregacoes': ('Mais lento', 'Mais rapido'),
        'recomendacao': ('MySQL para transacoes', 'MongoDB para agregacoes'),
    }

    for row in rows:
        cells = list(row.iter(f'{{{W}}}tc'))
        if len(cells) < 3:
            continue

        col1_text = ''
        for t in cells[0].iter(f'{{{W}}}t'):
            if t.text:
                col1_text += t.text
        col1_norm = unidecode(col1_text).lower()

        matched = None
        for key, (val_mysql, val_mongo) in comp_fills.items():
            if key in col1_norm:
                matched = (val_mysql, val_mongo)
                break
        if matched is None:
            continue

        # Fill MySQL/MongoDB columns (col 2, index 1 and col 3, index 2)
        for ci, val in [(1, matched[0]), (2, matched[1])]:
            if ci >= len(cells):
                continue
            col_text = ''
            for t in cells[ci].iter(f'{{{W}}}t'):
                if t.text:
                    col_text += t.text
            # Replace if empty or contains placeholder
            if not col_text.strip() or '(preencher)' in col_text.lower():
                for p in list(cells[ci].iter(f'{{{W}}}p')):
                    cells[ci].remove(p)
                cells[ci].append(make_paragraph(val))
                print(f'  [COMP] "{col1_text.strip()[:35]}" col{ci+1} -> "{val}"')
                changes += 1

xml_str = ET.tostring(root, encoding='unicode')
with zipfile.ZipFile(TMP, 'w', zipfile.ZIP_DEFLATED) as zout:
    with zipfile.ZipFile(SRC, 'r') as zin:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == 'word/document.xml':
                data = xml_str.encode('utf-8')
            zout.writestr(item, data)

os.replace(TMP, SRC)
print(f'\n{changes} celulas preenchidas.')
