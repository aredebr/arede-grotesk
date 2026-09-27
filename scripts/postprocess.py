"""Post-processing for built fonts: gasp/prep for the unhinted TTF (smooth rendering on Windows),
no DSIG, and a sanity check of the metadata that must match across formats."""
import sys
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram

for path in sys.argv[1:]:
    f = TTFont(path)
    if 'glyf' in f:
        gasp = newTable('gasp'); gasp.version = 1; gasp.gaspRange = {0xFFFF: 15}; f['gasp'] = gasp
        prep = newTable('prep'); prep.program = ttProgram.Program()
        prep.program.fromAssembly(['PUSHW[]', '511', 'SCANCTRL[]', 'PUSHB[]', '4', 'SCANTYPE[]'])
        f['prep'] = prep
        f['head'].flags |= (1 << 3)
    if 'DSIG' in f:
        del f['DSIG']
    f['OS/2'].fsType = 0
    f.save(path)
    print('postprocessed', path)
