#!/usr/bin/env python3
import base64, pathlib, sys
p=pathlib.Path(sys.argv[2]);text=p.read_text()
start=text.index('DATA_B85 = ');end=text.index('\n\nLEXICON',start)
s=base64.b85encode(pathlib.Path(sys.argv[1]).read_bytes()).decode()
chunks='\n'.join('    '+repr(s[i:i+100]) for i in range(0,len(s),100))
p.write_text(text[:start]+'DATA_B85 = (\n'+chunks+'\n)'+text[end:])
