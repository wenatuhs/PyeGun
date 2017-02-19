import numpy as np
from sfgenerator import SFGenerator
from sfcore import SFCore
from analyzer import Analyzer
from utils.physicshelper import freq2lamb

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

    def make_gun(self, vars=[]):
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
        if not vars:
            vars = [a]*(fc_num+1)
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
                'r_half': vars[0],
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
                    'r_full': vars[i+1],
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
                'r_left': b,
                'r_right': b}}
        gun.append(drift)
        self.gun = gun

    def test_gun(self, vars=[]):
        self.make_gun(vars)
        generator = SFGenerator(self)
        generator.gen_af()
        generator.gen_sf7()
        # core = SFCore(generator)
        # core.run()
        # analyzer = Analyzer(core)
        # analyzer.analyze()
        # analyzer.plot_efield(True, True)
    
    def _cal_jacobian(self):
        None
        # try:
        #     len(steps)
        # except:
        #     steps = steps*np.ones(len(origin))
            
        # mat = []
        # data = evaluate(origin, paras, root, '001', 1, 0, 0, 0, **kwargs)
        # delta = np.array(target)-data
        # for i in range(len(origin)):
        #     _origin = np.copy(origin)
        #     _origin[i] += steps[i]
        #     _origin = float4(_origin)
        #     _data = evaluate(_origin, paras, root, '001', 1, 0, 0, 0, **kwargs)
        #     mat.append((_data-data)/steps[i])
        # mat = np.array(mat).transpose()
        
        # return mat, delta

    def seek(self):
        None
        # if origin is None:
        #     origin = np.array([paras['r_half'], paras['r_full'], paras['r_hom']])
        
        # steps = maxstep
        # mat, delta = cal_matrix(origin, steps, target, paras, root, **kwargs)
        # cycle = 0
        # print('Cycle {0}: delta={1}'.format(cycle, list(delta)))
        
        # while np.sum(np.abs(delta) > error) and (cycle <= maxcycles):
        #     imat = np.linalg.inv(mat)
        #     delta_x = np.dot(delta, imat.transpose())
            
        #     _origin = float4(origin+delta_x)
        #     if np.array_equal(_origin, origin):
        #         _data = evaluate(origin, paras, root, '001', 1, 1, 1, 1, **kwargs)
        #         print('The local best solution has been achieved in cycle {}, however it does not satisfy the accuracy requirements.'.format(cycle))
                
        #         return origin, delta
        #     else:
        #         origin = _origin
                
        #     dis = delta_x/2
        #     ones = np.ones(len(dis))
        #     steps = np.max([np.min([dis, maxstep*ones], 0), minstep*ones], 0)
        #     mat, delta = cal_matrix(origin, steps, target, paras, root, **kwargs)
        #     cycle += 1
        #     print('Cycle {0}: delta={1}'.format(cycle, list(delta)))
        
        # _data = evaluate(origin, paras, root, '001', 1, 1, 1, 1, **kwargs)
        # if cycle > maxcycles and (np.sum(np.abs(delta) > error)):
        #     print('Sorry, can not find solutions with enough accuracy in {} cycles!'.format(maxcycles))
        # else:
        #     print('Suceed! Find good solutions in {} cylce(s)!'.format(cycle))
        
        # return origin, delta

if __name__ == "__main__":
    brain = Brain(11424, 5.6)
    brain.test_gun()
