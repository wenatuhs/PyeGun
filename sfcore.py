import os
from subprocess import Popen, PIPE

class SFCore:
    """ Superfish core for superfish simulation control.
    """

    def __init__(self, generator):
        self.generator = generator

    def run(self):
        root = '.'
        sim = self.generator.brain.name
        sim_path = os.path.join(root, sim)
        # Run Autofish
        af_input = [fname for fname in os.listdir(sim_path) if os.path.splitext(fname)[1] == '.af'][0]
        cmd = ['autofish', af_input]
        af = Popen(cmd, stdout=PIPE, cwd=sim_path)
        out = af.communicate()
        # Run SF7
        sf7_input = [fname for fname in os.listdir(sim_path) if os.path.splitext(fname)[1] == '.IN7'][0]
        t35_output = [fname for fname in os.listdir(sim_path) if os.path.splitext(fname)[1] == '.T35'][0]
        cmd = ['sf7', sf7_input, t35_output]
        sf7 = Popen(cmd, stdout=PIPE, cwd=sim_path)
        out = sf7.communicate()
