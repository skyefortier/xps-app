import sys; sys.path.insert(0,'/Users/skyefortier/xps-app')
from autofit.grammar import resolve, Phase, MaterialClass
from autofit.engine import match_components_to_slots, FittedComponent
g=resolve([Phase(id='sample',material_class=MaterialClass('conductor'),regions=('C 1s',))],'C 1s',allow_structural_fallback=True)
m=g.candidates[0]; s=m.slots[0]
lo,hi=s.be_window; fw=0.5*(s.fwhm_range[0]+s.fwhm_range[1])
for amp in (0.5, 1.5, 5.0):
    c=FittedComponent(slot_role=s.role,position=0.5*(lo+hi),fwhm=fw,amplitude=amp,shape_params={},line_shape=s.line_shape)
    mp=match_components_to_slots([c],m,noise_floor=1.0)
    print(f"amplitude {amp:>4} counts (noise_floor default 1.0): slot {s.role!r} occupied={mp[s.role] is not None}")
