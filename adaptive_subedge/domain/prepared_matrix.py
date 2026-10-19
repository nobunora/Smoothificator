"""Finite prepared matrix conditions; final volume is independent of clearance."""
from dataclasses import dataclass
from fractions import Fraction as F

STAGES=('h_volume','retract_wipe','startup_extra_speed','volume_speed')
AREAS=tuple(map(F,('.000075','.000150','.000300','.000600','.001200')))
AXES={
 'h_volume':(('h_cmd_mm','mm',tuple(map(F,('.010','.015','.020','.030','.040')))),('final_volume_mm3_per_mm','mm3/mm',AREAS)),
 'retract_wipe':(('retract_mm','mm',tuple(map(F,('.4','.7','1','1.3','1.6')))),('wipe_mm','mm',tuple(map(F,('.25','.5','1','1.5','2'))))),
 'startup_extra_speed':(('startup_extra_e_mm','mm filament',tuple(map(F,('0','.00005','.00010','.00015','.00020')))),('start_debt_unretract_speed_mm_s','mm/s',tuple(map(F,('6','12','18','24','30'))))),
 'volume_speed':(('final_volume_mm3_per_mm','mm3/mm',AREAS),('print_speed_mm_s','mm/s',tuple(map(F,('5','10','20','30','40'))))),
}

@dataclass(frozen=True)
class PreparedMatrixPolicy:
    trial_id:str
    schema_version:int=2
    def __post_init__(self):
        if type(self.trial_id) is not str or self.trial_id not in STAGES or type(self.schema_version) is not int or self.schema_version!=2:
            raise ValueError('closed prepared matrix policy required')

@dataclass(frozen=True)
class PreparedMatrixCondition:
    cell_id:str
    row:int
    column:int
    h_cmd_mm:F=F('.02')
    final_volume_mm3_per_mm:F=F('.0003')
    print_speed_mm_s:F=F(20)
    retract_mm:F=F('1.6')
    wipe_mm:F=F(1)
    start_debt_unretract_speed_mm_s:F=F(30)
    startup_extra_e_mm:F=F(0)
    def __post_init__(self):
        if type(self.cell_id) is not str or type(self.row) is not int or type(self.column) is not int or not 0<=self.row<5 or not 0<=self.column<5 or self.cell_id!=f'{self.row*5+self.column+1:02d}':
            raise ValueError('closed prepared matrix cell coordinates required')
        for name in ('h_cmd_mm','final_volume_mm3_per_mm','print_speed_mm_s','retract_mm','wipe_mm','start_debt_unretract_speed_mm_s','startup_extra_e_mm'):
            value=getattr(self,name)
            if type(value) is not F or value<0 or (not value and name!='startup_extra_e_mm') or max(abs(value.numerator).bit_length(),value.denominator.bit_length())>128:
                raise ValueError('bounded exact prepared matrix condition required')

def prepared_conditions(policy):
    if type(policy) is not PreparedMatrixPolicy:raise ValueError('exact prepared matrix policy required')
    rows,columns=AXES[policy.trial_id]
    return tuple(PreparedMatrixCondition(f'{r*5+c+1:02d}',r,c,**{rows[0]:rows[2][r],columns[0]:columns[2][c]}) for r in range(5) for c in range(5))

SPEED_RATIOS=tuple(map(F,('.2','.4','.6','.8','1')))

@dataclass(frozen=True)
class SourceRatioMatrixPolicy:
    trial_id:str='volume_speed'
    schema_version:int=3
    def __post_init__(self):
        if type(self.trial_id) is not str or self.trial_id!='volume_speed' or type(self.schema_version) is not int or self.schema_version!=3:
            raise ValueError('closed source-relative matrix policy required')

def source_relative_conditions(policy,reference_speed_mm_s):
    if type(policy) is not SourceRatioMatrixPolicy or type(reference_speed_mm_s) is not F or reference_speed_mm_s<=0 or max(abs(reference_speed_mm_s.numerator).bit_length(),reference_speed_mm_s.denominator.bit_length())>128:
        raise ValueError('exact source-relative policy and reference required')
    return tuple(PreparedMatrixCondition(f'{r*5+c+1:02d}',r,c,final_volume_mm3_per_mm=AREAS[r],print_speed_mm_s=reference_speed_mm_s*SPEED_RATIOS[c]) for r in range(5) for c in range(5))
