from pypdf import PdfReader
import glob, sys, re, logging

NP = '\s*(\d+(?:\.\d+)?)'  # 999 or 999.99
DP = '\s*(\d{2}/\d{2})'  # mm/dd

REY = re.compile(r'^.*\s\d+\s(\d{4})$')  # 年(4桁)
RED = re.compile(r'^'+DP+' (.+) \S+ Dividend Received - -'+NP+'$') # 配当
REN = re.compile(r'^([A-Z\s]+)$')  # 配当の security name 続き
RET = re.compile(r'^'+DP+' (.+) Non-Resident Tax -'+NP+'\D*$') # 配当の税金
RES = re.compile(r'^t?'+DP+'\s+(.+)\s+\S+\s+You Sold\s+z?\s?-'+NP+NP+NP+'f? -'+NP+NP+'$') # 売却
REG = re.compile(r'^([A-Z\s]*)\s(?:Long|Short)-term (gain|loss):'+NP+'\s?\S?$') # 売却時の損益
REB = re.compile(r'^'+DP+'\s+(.*) \S+ You Bought'+NP+NP+'.*$')  # 買付
REV = re.compile(r'^\sVALUE OF TRANSACTION'+NP+'$')  # 買付取引額

div = []  # 配当
tx = []   # 売買取引

def read_pdf(page):
    yy = '' # 年(4桁)
    lines = re.sub(' +', ' ', page.extract_text(extraction_mode='layout').replace(',','').replace('$','')).split("\n")
    for n, line in enumerate(lines):
        if r := REY.findall(line):  # 年表示行
            yy = r[0]
        elif r := RED.findall(line): # 配当行
            div.append({ 'date':yy+'/'+r[0][0], 'name':r[0][1], 'price':r[0][2], 'tax':'0.0'})
            div[-1]['name'] += r[0] if (r := REN.findall(lines[n+1])) else ''  # 次の行に名前の残りがあれば足す
        elif r := RET.findall(line):  # 配当の税金行。日付と security name が一致する配当にこの税金を加える
            [d.update(tax=r[0][2]) for d in div if (d['date'].endswith(r[0][0]) and r[0][1].startswith(d['name']))]
        elif r := RES.findall(line): # 売却行
            tx.append({'type':'売却', 'date':yy+'/'+r[0][0], 'name':r[0][1], 'qty':r[0][2], 'price':r[0][3],
                         'ttlcost':r[0][4], 'txcost':r[0][5], 'amount':r[0][6]})
            if r := REG.findall(lines[n+1]):  # 売却行の次行は損益行
                tx[-1]['name'] += r[0][0]   # security name の残り
                tx[-1]['gain'] = ('' if r[0][1] == 'gain' else '-') + r[0][2]  # 損失の時はマイナスの値に
        elif r := REB.findall(line):  # 買付行
            tx.append({'type':'買付', 'date':yy+'/'+r[0][0], 'name':r[0][1], 'qty':r[0][2], 'price':r[0][3],
                          'ttlcost':'', 'txcost':'', 'gain':''})
            tx[-1]['amount'] = r[0] if (r := REV.findall(lines[n+1])) else ''  # 買付行の次の行

if __name__ == "__main__":
    logging.getLogger("pypdf").setLevel(logging.ERROR) # pypdf の Warning 出力を抑止
    path = sys.argv[1] if (len(sys.argv) == 2) else '.'
    [[read_pdf(page) for page in PdfReader(file).pages] for file in glob.glob(path + '/*.pdf')]
    print('種類,日付,名前,価格,税金')
    [print('配当',d['date'],d['name'],d['price'],d['tax'],sep=',') for d in div]
    print('\n種類,日付,名前,量,価格,総コスト,取引コスト,総額,損益')
    [print(t['type'],t['date'],t['name'],t['qty'],t['price'],t['ttlcost'],t['txcost'],t['amount'],t['gain'],sep=',') for t in tx]
