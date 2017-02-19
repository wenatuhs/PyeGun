def _get_chamfer(chamfer, direction='x'):
    """ Calculate chamfer radius.
    
    Keyword arguments:
    chamfer -- a float or a two element array-like.
        ex. 1.2 or (0.5, 1.4)
    direction -- ['x'] which radius to calculate, 'x' or 'y'
    
    Returns:
    radius -- the radius of the chamfer in the specific direction.
    """
    try:
        x = chamfer[0]
        return x if direction == 'x' else chamfer[1]
    except:
        return chamfer

def gen_halfcell(paras, title='Halfcell'):
    """ Generate autofish commands for a halfcell.
    
    Keyword arguments:
    paras -- the geometry parameters of the halfcell, all units are cm.
    title -- ['Halfcell'] the halfcell title appears in the autofish input file.
    
    Returns:
    halfcell -- the halfcell autofish commands.
    """
    l_half = paras['l_half']
    r_half = paras['r_half']
    c_half = paras['c_half']
    j_half = paras['j_half']
    r_tube = paras['r_tube']
    
    halfcell = ''';{10}
&PO X={12:.4f} Y={12:.4f}&
&PO X={12:.4f} Y={0:.4f}&
&PO X={1:.4f} Y={0:.4f}&
{11}&PO NT=2 X0={1:.4f} Y0={2:.4f} X={3:.4f} Y={12:.4f} A={3:.4f} B={4:.4f}&
&PO X={5:.4f} Y={6:.4f}&
&PO NT=2 X0={7:.4f} Y0={6:.4f} X={12:.4f} Y=-{9:.4f} A={8:.4f} B={9:.4f}&'''.format(
        r_half,
        l_half-_get_chamfer(j_half)-_get_chamfer(c_half),
        r_half-_get_chamfer(c_half, 'y'),
        _get_chamfer(c_half),
        _get_chamfer(c_half, 'y'),
        l_half-_get_chamfer(j_half),
        r_tube+_get_chamfer(j_half, 'y'),
        l_half,
        _get_chamfer(j_half),
        _get_chamfer(j_half, 'y'),
        title,
        '' if _get_chamfer(c_half)*_get_chamfer(c_half, 'y') else ';',
        0)
    
    return halfcell

def gen_fullcell(paras, title='Fullcell'):
    """ Generate autofish commands for a fullcell.
    
    Keyword arguments:
    paras -- the geometry parameters of the fullcell, all units are cm.
    title -- ['Fullcell'] the fullcell title appears in the autofish input file.
    
    Returns:
    fullcell -- the fullcell autofish commands.
    """
    p_start = paras['p_start']
    l_full = paras['l_full']
    r_full = paras['r_full']
    c_full = paras['c_full']
    j_full_l = paras['j_full_l']
    j_full_r = paras['j_full_r']
    r_tube_l = paras['r_tube_l']
    r_tube_r = paras['r_tube_r']
    
    fullcell = ''';{16}
&PO NT=2 X0={0:.4f} Y0={1:.4f} X={2:.4f} Y={18:.4f} A={2:.4f} B={3:.4f}&
&PO X={4:.4f} Y={5:.4f}&
{17}&PO NT=2 X0={6:.4f} Y0={5:.4f} X={18:.4f} Y={7:.4f} A={8:.4f} B={7:.4f}&
&PO X={9:.4f} Y={10:.4f}&
{17}&PO NT=2 X0={9:.4f} Y0={5:.4f} X={8:.4f} Y={18:.4f} A={8:.4f} B={7:.4f}&
&PO X={11:.4f} Y={12:.4f}&
&PO NT=2 X0={13:.4f} Y0={12:.4f} X={18:.4f} Y=-{14:.4f} A={15:.4f} B={14:.4f}&'''.format(
            p_start,
            r_tube_l+_get_chamfer(j_full_l, 'y'),
            _get_chamfer(j_full_l),
            _get_chamfer(j_full_l, 'y'),
            p_start+_get_chamfer(j_full_l),
            r_full-_get_chamfer(c_full, 'y'),
            p_start+_get_chamfer(j_full_l)+_get_chamfer(c_full),
            _get_chamfer(c_full, 'y'),
            _get_chamfer(c_full),
            p_start+l_full-_get_chamfer(c_full)-_get_chamfer(j_full_r),
            r_full,
            p_start+l_full-_get_chamfer(j_full_r),
            r_tube_r+_get_chamfer(j_full_r, 'y'),
            p_start+l_full,
            _get_chamfer(j_full_r, 'y'),
            _get_chamfer(j_full_r),
            title,
            '' if _get_chamfer(c_full)*_get_chamfer(c_full, 'y') else ';',
            0)
    
    return fullcell

def gen_drift(paras, title='Drift', final=True):
    p_start = paras['p_start']
    l_drift = paras['l_drift']
    r_left = paras['r_left']
    r_right = paras['r_right']
    p_end = p_start+l_drift

    if final:
        drift = ''';{5}
&PO X={0:.4f} Y={1:.4f}&
&PO X={2:.4f} Y={3:.4f}&
&PO X={2:.4f} Y={4:.4f}&
&PO X={4:.4f} Y={4:.4f}&'''.format(p_start, r_left, p_end, r_right, 0, title)
    else:
        drift = ''';{4}
&PO X={0:.4f} Y={1:.4f}&
&PO X={2:.4f} Y={3:.4f}&'''.format(p_start, r_left, p_end, r_right, title)
    
    return drift

def gen_setting(paras, title='Settings'):
    freq = paras['freq']
    xdri = paras['xdri']
    ydri = paras['ydri']
    dx = paras['dx']
    dy = paras['dy']

    settings = ''';{5}
&REG KPROB=1 ICYLIN=1
FREQ={0:.0f}
XDRI={1:.4f} YDRI={2:.4f}
DX={3:.4f} DY={4:.4f}&'''.format(freq, xdri, ydri, dx, dy, title)

    return settings

def gen_title(paras):
    title = paras['title']

    return title
