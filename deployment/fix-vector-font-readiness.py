from pathlib import Path
import sys
root=Path(sys.argv[1])
p=root/'crates/ui-egui/src/app.rs'
s=p.read_text()
old='let fonts = theme::interface_fonts();\n'
new='let fonts = crate::local_chinese::with_chinese(theme::interface_fonts());\n'
assert s.count(old)==1, 'expected exactly one initial interface font definition'
s=s.replace(old,new,1)
old='ctx.set_fonts(crate::local_chinese::with_chinese(fonts.clone()));\n'
new='ctx.set_fonts(fonts.clone());\n'
assert s.count(old)==1, 'expected exactly one wrapped initial font setter'
s=s.replace(old,new,1)
p.write_text(s)
print('VectorCraft font readiness now compares the installed Chinese-extended definitions')
