#!/usr/bin/python

import sys, re

if len(sys.argv) < 2:
    print("Missing argument")
    sys.exit(1)
    
properties = []
variables = []
functions = []
signals = []
slots = []

for line in sys.argv[1].splitlines():
    decl = line.strip()

    match = re.search(r"([:\w]+\W+)(m_)?(\w+)", decl)

    if not match:
        print("Couldn't parse member variable, expected form: 'type [m_]name'")
        sys.exit(1)
        
    m_type = match.group(1).strip()

    m_isPointer = m_type.endswith("*")

    m_name = match.group(3)
    m_Name = m_name[0].upper() + m_name[1:]
    m_notify = f"{m_name}Changed"
    m_var = "m_" + m_name
    m_destroyed = f"{m_name}DestroyedHandler"

    properties.append(f"Q_PROPERTY({m_type} {m_name} READ {m_name} WRITE set{m_Name} NOTIFY {m_notify})")
    variables.append(f"{m_type} m_{m_name} {{}};")
    functions.append(f"{m_type} {m_name}() const {{ return {m_var}; }}")
    signals.append(f"void {m_notify}();")
    if m_isPointer:
        functions.append(f"""void set{m_Name}({m_type} v) {{
    if(v == {m_var}) {{
      return;
    }}
    if({m_var} != nullptr) {{
      /* Add (optional) code to deref {m_var} here */
      disconnect({m_var}, &QObject::destroyed, this, &CLASS_NAME::{m_destroyed});
    }}
    {m_var} = v;
    if({m_var} != nullptr) {{
      connect({m_var}, &QObject::destroyed, this, &CLASS_NAME::{m_destroyed});
    }}
    emit {m_notify}();
  }}"""
        )
        slots.append(f"""void {m_destroyed}(QObject *o) {{
    Q_ASSERT({m_var} == o);
    /* Add (optional) code to deref {m_var} here */
    {m_var} = nullptr;
    emit {m_notify}();
  }}""")
    else:
        functions.append(f"void set{m_Name}({m_type} v) {{ if(v != {m_var}) {{ {m_var} = v; emit {m_notify}(); }} }}")



print("\n".join(["  " + s for s in properties]))
print("\n".join(["  " + s for s in variables]))
print("public:")
print("\n".join(["  " + s for s in functions]))
if len(slots):
    print("private slots:")
    print("\n".join(["  " + s for s in slots]))
print("signals:")
print("\n".join(["  " + s for s in signals]))
