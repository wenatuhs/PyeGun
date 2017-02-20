import os
import numpy as np
import matplotlib.pyplot as plt
from utils.peakdetect import peakdetect

class Analyzer:
    """ Superfish simulation result analyzer.
    """

    def __init__(self, core):
        self.core = core
        self.info = None
    
    def _cal_flatness(self, Ez, lookahead=20):
        ''' Calculate the flatness of the e-gun.
        
        Keyword arguments:
        Ez -- axial electric field in MV/m.
        
        Returns:
        flatness -- flatness of the field.'''
        num = int(self.core.generator.brain.cell_num)+1  # number of cells

        peaks = peakdetect(Ez, lookahead=lookahead)[0]
        if len(peaks) == num:
            p_values = np.array(peaks)[:, 1]
            return (p_values/p_values[0])[1:]
        else:
            print("Peak number doesn't match cell number!")
            return np.nan

    def analyze(self):
        ''' Read cavity physical parameters in a .SFO file.
        
        Returns:
        paras -- the dict of physical parameters.
            name -- .SFO filename
            f -- frequency [MHz]
            T -- transit time factor
            Q -- quality factor
            Z -- shunt impedence [MOhm/m]
            ZTT -- effective shunt impedence [MOhm/m]
            R/Q -- shape factor
            eta -- Emax/E0
            nu -- Ecathode/Emax
            Emap -- axial electric field data. Unit: z [cm], Ez [MV/m].'''
        root = '.'
        sim = self.core.generator.brain.name
        sim_path = os.path.join(root, sim)

        sfo_output = [fname for fname in os.listdir(sim_path) if os.path.splitext(fname)[1] == '.SFO'][0]
        with open(os.path.join(sim_path, sfo_output), 'r') as f:
            flag = 0
            paras = {}
            z = []
            Ez = []
            
            for l in f.readlines():
                if flag == 1:
                    try:
                        data = l.split()
                        z.append(float(data[0]))
                        Ez.append(float(data[1]))
                    except:
                        pass
                elif flag == 2:
                    try:
                        tokens = l.split()
                        if tokens[0] == 'Frequency':
                            paras['f'] = float(tokens[2])
                        elif tokens[0] == 'Transit-time':
                            paras['T'] = float(tokens[3])
                        elif tokens[0] == 'Q':
                            paras['Q'] = float(tokens[2])
                            paras['Z'] = float(tokens[6])
                        elif tokens[0] == 'Rs*Q':
                            paras['ZTT'] = float(tokens[6])
                        elif tokens[0] == 'r/Q':
                            paras['R/Q'] = float(tokens[2])
                        elif tokens[0] == 'Peak-to-average':
                            paras['eta'] = float(tokens[4])
                    except:
                        pass
                if l.startswith('for normalization ASCALE'):
                    flag = 1
                elif l.startswith('Total cavity stored'):
                    flag = 0
                elif l.startswith("All calculated values below refer to the mesh geometry only."):
                    flag = 2
                elif l.startswith("Wall segments:"):
                    break
            z, Ez = np.array(z), np.array(Ez)
            paras['nu'] = Ez[0]/np.max(Ez)
            paras['Emap'] = np.vstack((z, Ez/1e6))
            paras['flat'] = self._cal_flatness(Ez)
            paras['name'] = sfo_output

        self.info = paras

    def read_SF7(self):
        """ Read axial electric field data in the OUTSF7.TXT file that generated by superfish.
        
        Returns:
        z, Ez -- axial electric field data. Unit: z [cm], Ez [MV/m].
        """
        root = '.'
        sim = self.core.generator.brain.name
        sim_path = os.path.join(root, sim)
        sf7_output = 'OUTSF7.TXT'
        
        with open(os.path.join(sim_path, sf7_output), 'r') as f:
            flag = 0
            z = []
            Ez = []
            for l in f.readlines():
                if l.startswith('Number of increments'):
                    flag = 1
                if flag:
                    try:
                        data = l.split()
                        z.append(float(data[0]))
                        Ez.append(float(data[2]))
                    except:
                        pass

        return np.vstack((np.array(z), np.array(Ez))) # [cm, MV/m]

    def plot_efield(self, show=True, save=False):
        """ Plot the axial electric field in a .SFO file that generated by superfish.
        
        Keyword arguments:
        show -- if show the figure. [True]
        save -- save the figure or not. [False]
        """
        root = '.'
        sim = self.core.generator.brain.name
        sim_path = os.path.join(root, sim)

        z, Ez = self.info['Emap']
        freq = self.info['f']
        flat = self.info['flat']

        fig, ax = plt.subplots(1, 1)
        ax.set(xlim=(z[0], z[-1]), xlabel='z (cm)', ylabel='Ez (MV/m)')
        flatlist = '\n'.join(['p{0}/p0 = {1:.2f}'.format(i+1, flat[i]) for i in range(len(flat))])
        comment = '{0}\nfreq = {1:.2f} MHz\n{2}'.format(sim, freq, flatlist)
        ax.plot(z, Ez, label=comment)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1), borderaxespad=0)
        fig.tight_layout()
        if save:
            pdfname = os.path.join(sim_path, sim+'.pdf')
            fig.savefig(pdfname, bbox_inches='tight')
        if not show:
            plt.close(fig)
        else:
            plt.show()
    
    def export_efield(self, target='astra'):
        root = '.'
        sim = self.core.generator.brain.name
        sim_path = os.path.join(root, sim)

        emap = self.read_SF7()
        emap[0] /= 1e2  # cm to m
        if emap[1][0] < 0:  # reverse the sign
            emap[1] = -emap[1]
        emap[1] /= np.max(np.abs(emap[1]))  # normalization

        np.savetxt(os.path.join(sim_path, sim+'.dat'), emap.transpose(), '%.6e')
