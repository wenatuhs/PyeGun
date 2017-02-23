import numpy as np
from sfgenerator import SFGenerator
from sfcore import SFCore
from analyzer import Analyzer
from utils.physicshelper import freq2lamb
from utils.roundup import float4
from utils.newton import seek_root

class Brain:
    """ e-Gun CPU.
    """

    def __init__(self, freq=2856, cell_num=1.6, name='e-gun', options=None):
        self.freq = freq
        self.cell_num = cell_num
        self.name = name
        self.options = options
        self.gun = ''

    def _cal_drive_point(self):
        freq = self.freq
        cell_num = self.cell_num
        lamb = freq2lamb(freq)*1e-1  # mm to cm
        a = 2.405/(2*np.pi)*lamb  # [cm] matched cell radius

        xdri = (cell_num-int(cell_num/2)-1/2)*lamb/2
        ydri = a/2

        return xdri, ydri

    def make_gun(self, x):
        freq = self.freq
        cell_num = self.cell_num
        fc_num = int(cell_num)
        hc_ratio = cell_num-fc_num
        # Gun geometry
        lamb = freq2lamb(freq)*1e-1  # mm to cm
        a = 2.405/(2*np.pi)*lamb  # [cm] matched cell radius
        b = a/4  # tube radius
        r = a/4  # chamfer/joint radius
        l_full = lamb/2
        l_half = hc_ratio*l_full
        l_drift = 1.2*l_full  # gun exit drift distance
        # Simulation settings
        name = self.name
        xdri, ydri = self._cal_drive_point()
        dx = lamb/100  # 100 meshgrids per wavelength

        # Compose the gun
        gun = []
        p_start = 0
        # Add title and setting
        title = {
            'type': 'title',
            'paras': {
                'title': name}}
        setting = {
            'type': 'setting',
            'paras': {
                'freq': freq,
                'xdri': xdri,
                'ydri': ydri,
                'dx': dx,
                'dy': dx}}
        gun += [title, setting]
        # Add halfcell
        halfcell = {
            'type': 'halfcell',
            'paras': {
                'l_half': l_half,
                'r_half': x[0],
                'c_half': r,
                'j_half': r,
                'r_tube': b}}
        gun.append(halfcell)
        p_start += l_half
        # Add fullcell(s)
        for i in range(fc_num):
            fullcell = {
                'type': 'fullcell',
                'paras': {
                    'p_start': p_start,
                    'l_full': l_full,
                    'r_full': x[i+1],
                    'c_full': r,
                    'j_full_l': r,
                    'j_full_r': r,
                    'r_tube_l': b,
                    'r_tube_r': b}}
            gun.append(fullcell)
            p_start += l_full
        # Add drift
        drift = {
            'type': 'drift',
            'paras': {
                'p_start': p_start,
                'l_drift': l_drift,
                'r_right': b}}
        gun.append(drift)
        self.gun = gun

    def test_gun(self, x):
        self.make_gun(x)
        generator = SFGenerator(self)
        generator.gen_af()
        generator.gen_sf7()
        core = SFCore(generator)
        core.run()
        analyzer = Analyzer(core)
        analyzer.analyze()
        # analyzer.plot_efield(False, True)
        freq = analyzer.info['f']/self.freq-1
        flat = analyzer.info['flat']-1
        y = np.append(freq, flat)
        return y

    def _init_guess(self):
        lamb = freq2lamb(self.freq)*1e-1  # mm to cm
        a = float4(2.405/(2*np.pi)*lamb)
        cnum = int(self.cell_num)+1
        x = [a]*cnum
        return x

    def seek(self):
        try:
            step = self.options['step']
        except KeyError:
            step = 1e-3
        
        def jacob(x):
            y = self.test_gun(x)
            mat = []
            for i in range(len(x)):
                _x = np.copy(x)
                _x[i] += step
                _x = float4(_x)
                _y = self.test_gun(_x)
                mat.append((_y-y)/step)
            mat = np.array(mat).transpose()
            return y, mat

        x = self._init_guess()
        seek_root(x, jacob, self.options)

if __name__ == "__main__":
    options = {
        'err': 1e-3,
        'max_cycle': 100,
        'eta': 0.5,
        'step': 1e-3
    }
    brain = Brain(11424, 3.6, '3P6GUN', options)
    brain.seek()
    # x = brain._init_guess()
    # brain.test_gun(x)
