#!/usr/bin/python

import sys, re

if len(sys.argv) < 2:
    print("Missing argument")
    sys.exit(1)

str = sys.argv[1].strip()

p = re.compile(r"(\w+\W+)(m_)?(\w+)")
match = re.search(p, str)

if not match:
    print("Couldn't parse member variable, expected form: 'type m_name'")
    sys.exit(1)
    
# print(str, match, match.groups())

m_type = match.group(1).strip()
m_prefix = match.group(2) if match.group(2) else "m_"
m_name = match.group(3)
m_Name = m_name[0].upper() + m_name[1:]
m_notify = f"{m_name}Changed"
m_var = m_prefix + m_name

print(f'''\
  {m_type} m_{m_name} {{}};
  Q_PROPERTY({m_type} {m_name} READ {m_name} WRITE set{m_Name} NOTIFY {m_notify})
public:
  {m_type} {m_name}() const {{ return {m_var}; }}
  void set{m_Name}({m_type} v) {{ if(v != {m_var}) {{ {m_var} = v; emit {m_notify}(); }} }}
signals:
  void {m_notify}();
''')
