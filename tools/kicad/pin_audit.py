import pathlib, re, sys

def extract_pins(kicad_text, symbol_name):
    start = kicad_text.find(f'(symbol "{symbol_name}"')
    if start == -1:
        return None
    depth=0
    end=start
    for i in range(start, len(kicad_text)):
        if kicad_text[i]=='(':
            depth+=1
        elif kicad_text[i]==')':
            depth-=1
            if depth==0:
                end=i+1
                break
    block = kicad_text[start:end]
    pins = {}
    # Robust: name "..." ) \s* (number "..."
    for m in re.finditer(r'name "([^"]+)"\s*\)\s*\(number "([^"]+)"', block):
        name = m.group(1)
        num = m.group(2)
        pins[num] = name
    return pins

def audit(symbol_name, file_path, expected):
    txt = pathlib.Path(file_path).read_text(encoding="utf-8")
    pins = extract_pins(txt, symbol_name)
    if pins is None:
        print(f"FAIL {symbol_name} in {file_path}: not found")
        return False
    ok = True
    exp_nums = set(expected.keys())
    actual_nums = set(pins.keys())
    if exp_nums != actual_nums:
        missing = exp_nums - actual_nums
        extra = actual_nums - exp_nums
        if missing:
            print(f"FAIL {symbol_name} {pathlib.Path(file_path).name}: missing pins {sorted(missing)}")
            ok=False
        if extra:
            print(f"FAIL {symbol_name} {pathlib.Path(file_path).name}: extra pins {sorted(extra)}")
            ok=False
    for num, exp_name in expected.items():
        actual = pins.get(num)
        if actual != exp_name:
            print(f"FAIL {symbol_name} pin {num} in {pathlib.Path(file_path).name}: expected '{exp_name}' got '{actual}'")
            ok=False
    if ok:
        print(f"PASS {symbol_name} in {pathlib.Path(file_path).name}: {len(pins)} pins OK")
    return ok

expected_ads1262 = {
    "1":"AIN8","2":"AIN9","3":"AINCOM","4":"CAPP","5":"CAPN","6":"AVDD","7":"AVSS","8":"REFOUT","9":"START","10":"CS","11":"SCLK","12":"DIN","13":"DOUT/DRDY","14":"DRDY","15":"XTAL1/CLKIN","16":"XTAL2","17":"BYPASS","18":"DGND","19":"DVDD","20":"RESET/PWDN","21":"AIN0","22":"AIN1","23":"AIN2","24":"AIN3","25":"AIN4","26":"AIN5","27":"AIN6","28":"AIN7"
}
expected_ad5764 = {
    "1":"SYNC","2":"SCLK","3":"SDIN","4":"SDO","5":"CLR","6":"LDAC","7":"D0","8":"D1","9":"RSTOUT","10":"RSTIN","11":"DGND","12":"DVCC","13":"AVDD","14":"PGND","15":"AVSS","16":"ISCC","17":"AGNDD","18":"VOUTD","19":"VOUTC","20":"AGNDC","21":"AGNDB","22":"VOUTB","23":"VOUTA","24":"AGNDA","25":"REFAB","26":"REFCD","27":"NC","28":"REFGND","29":"NC","30":"AVSS","31":"AVDD","32":"BIN/2sCOMP"
}
expected_lt1970 = {
    "1":"VEE","2":"V-","3":"OUT","4":"SENSE+","5":"FILTER","6":"SENSE-","7":"VCC","8":"-IN","9":"+IN","10":"VEE","11":"VEE","12":"VCSNK","13":"VCSRC","14":"COM","15":"ENABLE","16":"ISRC_N","17":"ISNK_N","18":"TSD","19":"V+","20":"VEE","21":"VEE"
}
expected_lt5400 = {
    "1":"R1A","2":"R2A","3":"R3A","4":"R4A","5":"R4B","6":"R3B","7":"R2B","8":"R1B","9":"EP"
}

base = pathlib.Path("E:/ReRAM-SMU V1/hardware/kicad/ReRAM-SMU-V1")
results = []
results.append(audit("ReRAM_SMU:ADS1262IPW", base/"sheets/06_CURRENT_FRONTEND_ADC.kicad_sch", expected_ads1262))
results.append(audit("ReRAM_SMU:AD5764", base/"sheets/02_DAC_SOURCE_COMMAND.kicad_sch", expected_ad5764))
results.append(audit("ReRAM_SMU:LT1970A", base/"sheets/03_OUTPUT_STAGE.kicad_sch", expected_lt1970))
results.append(audit("ReRAM_SMU:LT5400", base/"sheets/04_KELVIN_SENSE.kicad_sch", expected_lt5400))
results.append(audit("ReRAM_SMU:ADS1262IPW", base/"lib/ReRAM-SMU-V1.kicad_sym", expected_ads1262))
results.append(audit("ReRAM_SMU:AD5764", base/"lib/ReRAM-SMU-V1.kicad_sym", expected_ad5764))
results.append(audit("ReRAM_SMU:LT1970A", base/"lib/ReRAM-SMU-V1.kicad_sym", expected_lt1970))
results.append(audit("ReRAM_SMU:LT5400", base/"lib/ReRAM-SMU-V1.kicad_sym", expected_lt5400))

if all(results):
    print("ALL PIN AUDITS PASS")
    sys.exit(0)
else:
    print("SOME PIN AUDITS FAIL")
    sys.exit(1)
