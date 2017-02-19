import os
from subprocess import Popen, PIPE
from utils.gencell import gen_halfcell, gen_fullcell, gen_drift, gen_setting, gen_title

class SFGenerator:
    """ Superfish input file Generator.
    """

    def __init__(self, brain):
        self.brain = brain

    def gen_af(self):
        """ Generate the autofish input file of the rf gun.
        """
        name = self.brain.name
        gun = self.brain.gun

        gen_element = {
            'title': gen_title,
            'setting': gen_setting, 
            'halfcell': gen_halfcell,
            'fullcell': gen_fullcell,
            'drift': gen_drift}
        ctx = '\n\n'.join([gen_element[element['type']](element['paras']) for element in gun])

        self._gen_sim_folder()
        self._clean_up_sim_folder()
        with open(os.path.join('.', name, name+'.af'), 'w') as f:
            f.write(ctx)

    def gen_sf7(self):
        """ Generate the sf7 input file of the rf gun.
        """
        name = self.brain.name
        gun = self.brain.gun  # gun = [title, setting, halfcell, fullcell..., drift]

        setting = gun[1]
        drift = gun[-1]
        dx = setting['paras']['dx']
        z_end = drift['paras']['p_start']+drift['paras']['l_drift']
        num = int(2*z_end/dx)
        
        ctx = '''Line
{0:.4f} {2:.4f} {1:.4f} {2:.4f}
{3}
End'''.format(0, z_end, 0, num)
        
        with open(os.path.join('.', name, name+'.IN7'), 'w') as f:
            f.write(ctx)

    def _clean_up_sim_folder(self):
        root = '.'
        sim = self.brain.name
        sim_path = os.path.join(root, sim)

        if os.name == 'posix':
            cmd = 'rm *'
        else:
            cmd = 'del /s/q/f *'
        rm = Popen(cmd, cwd=sim_path, shell=True)
        out = rm.communicate()

    def _gen_sim_folder(self):
        root = '.'
        sim = self.brain.name
        sim_path = os.path.join(root, sim)

        if not os.path.isdir(sim_path):
            cmd = ['mkdir', sim]
            mk = Popen(cmd, cwd=root, shell=(os.name != 'posix'))
            out = mk.communicate()
