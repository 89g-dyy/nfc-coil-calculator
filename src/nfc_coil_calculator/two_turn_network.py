"""Two-turn distributed LC network, algebra ported from the ST public calculator.

``x[0:8]`` are segment reactances and ``caps[0:4]`` are capacitor reactances.
Operand order is preserved so the expression stays comparable with the source.
Units and provenance are documented in docs/ALGORITHM.md.
"""


def two_turn_impedance(x, caps, omega):
    e, n, a, o, r, i, l, c = [omega * v for v in x]
    s, m, d, g = [-1 / (omega * v) for v in caps]
    return abs(
        e/(e*(o*r*i*l+o*i*l*c+r*i*l*c+o*r*l*s+o*i*l*s+o*l*c*s+r*l*c*s+i*l*c*s+o*r*i*m+o*r*l*m+
        o*i*c*m+r*i*c*m+o*l*c*m+r*l*c*m+o*r*s*m+o*i*s*m+o*l*s*m+o*c*s*m+r*c*s*m+i*c*s*m+l*c*s*m+
        o*r*i*d+o*i*l*d+r*i*l*d+o*i*c*d+r*i*c*d+o*r*s*d+o*i*s*d+o*l*s*d+r*l*s*d+i*l*s*d+o*c*s*d+
        r*c*s*d+i*c*s*d+o*r*m*d+o*i*m*d+r*i*m*d+o*l*m*d+r*l*m*d+o*c*m*d+r*c*m*d+r*s*m*d+i*s*m*d+
        l*s*m*d+c*s*m*d+o*i*l*g+r*i*l*g+o*l*s*g+r*l*s*g+i*l*s*g+o*i*m*g+r*i*m*g+o*l*m*g+r*l*m*g+
        o*s*m*g+r*s*m*g+i*s*m*g+l*s*m*g+o*i*d*g+r*i*d*g+o*s*d*g+r*s*d*g+i*s*d*g+o*m*d*g+r*m*d*g+
        s*m*d*g+a*(i*l*c+i*c*s+l*c*s+i*c*m+l*c*m+i*l*d+i*c*d+i*s*d+l*s*d+c*s*d+i*m*d+l*m*d+c*m*d+
        i*l*g+i*s*g+l*s*g+i*m*g+l*m*g+i*d*g+s*d*g+m*d*g+r*(i+s+m)*(c+d+g)+o*(r*(i+s+m)+(s+m)*(l+c+
        g)+i*(l+c+s+m+g)))+n*(r*l*c+i*l*c+r*c*m+i*c*m+l*c*m+r*l*d+i*l*d+r*c*d+i*c*d+r*m*d+i*m*d+
        l*m*d+c*m*d+r*l*g+i*l*g+r*m*g+i*m*g+l*m*g+r*d*g+i*d*g+m*d*g+o*(l*c+l*m+c*m+l*d+c*d+r*(l+m+
        d)+i*(l+m+d)+l*g+m*g+d*g)+a*(i*c+l*c+i*d+l*d+c*d+i*g+l*g+d*g+o*(r+i+l+c+g)+r*(c+d+
        g)))))/(a*o*r*i*l+a*o*r*i*c+a*r*i*l*c+o*r*i*l*c+a*o*r*l*s+a*o*i*l*s+a*o*r*c*s+a*o*i*c*s+
        a*r*l*c*s+o*r*l*c*s+a*i*l*c*s+o*i*l*c*s+a*o*r*i*m+a*o*r*l*m+a*o*r*c*m+a*r*i*c*m+o*r*i*c*m+
        a*r*l*c*m+o*r*l*c*m+a*o*r*s*m+a*o*i*s*m+a*o*l*s*m+a*o*c*s*m+a*r*c*s*m+o*r*c*s*m+a*i*c*s*m+
        o*i*c*s*m+a*l*c*s*m+o*l*c*s*m+a*r*i*l*d+o*r*i*l*d+a*r*i*c*d+o*r*i*c*d+a*r*l*s*d+o*r*l*s*d+
        a*i*l*s*d+o*i*l*s*d+a*r*c*s*d+o*r*c*s*d+a*i*c*s*d+o*i*c*s*d+a*r*i*m*d+o*r*i*m*d+a*r*l*m*d+
        o*r*l*m*d+a*r*c*m*d+o*r*c*m*d+a*r*s*m*d+o*r*s*m*d+a*i*s*m*d+o*i*s*m*d+a*l*s*m*d+o*l*s*m*d+
        a*c*s*m*d+o*c*s*m*d+a*o*i*l*g+a*r*i*l*g+a*o*i*c*g+a*r*i*c*g+a*i*l*c*g+o*i*l*c*g+r*i*l*c*g+
        a*o*l*s*g+a*r*l*s*g+a*i*l*s*g+a*o*c*s*g+a*r*c*s*g+a*i*c*s*g+a*l*c*s*g+o*l*c*s*g+r*l*c*s*g+
        i*l*c*s*g+a*o*i*m*g+a*r*i*m*g+a*o*l*m*g+a*r*l*m*g+a*o*c*m*g+a*r*c*m*g+a*i*c*m*g+o*i*c*m*g+
        r*i*c*m*g+a*l*c*m*g+o*l*c*m*g+r*l*c*m*g+a*o*s*m*g+a*r*s*m*g+a*i*s*m*g+a*l*s*m*g+o*c*s*m*g+
        r*c*s*m*g+i*c*s*m*g+l*c*s*m*g+a*i*l*d*g+o*i*l*d*g+r*i*l*d*g+a*i*c*d*g+o*i*c*d*g+r*i*c*d*g+
        a*l*s*d*g+o*l*s*d*g+r*l*s*d*g+i*l*s*d*g+a*c*s*d*g+o*c*s*d*g+r*c*s*d*g+i*c*s*d*g+a*i*m*d*g+
        o*i*m*d*g+r*i*m*d*g+a*l*m*d*g+o*l*m*d*g+r*l*m*d*g+a*c*m*d*g+o*c*m*d*g+r*c*m*d*g+a*s*m*d*g+
        o*s*m*d*g+r*s*m*d*g+i*s*m*d*g+l*s*m*d*g+c*s*m*d*g+e*(o*r*i*l+o*i*l*c+r*i*l*c+o*r*l*s+
        o*i*l*s+o*l*c*s+r*l*c*s+i*l*c*s+o*r*i*m+o*r*l*m+o*i*c*m+r*i*c*m+o*l*c*m+r*l*c*m+o*r*s*m+
        o*i*s*m+o*l*s*m+o*c*s*m+r*c*s*m+i*c*s*m+l*c*s*m+o*r*i*d+o*i*l*d+r*i*l*d+o*i*c*d+r*i*c*d+
        o*r*s*d+o*i*s*d+o*l*s*d+r*l*s*d+i*l*s*d+o*c*s*d+r*c*s*d+i*c*s*d+o*r*m*d+o*i*m*d+r*i*m*d+
        o*l*m*d+r*l*m*d+o*c*m*d+r*c*m*d+r*s*m*d+i*s*m*d+l*s*m*d+c*s*m*d+o*i*l*g+r*i*l*g+o*l*s*g+
        r*l*s*g+i*l*s*g+o*i*m*g+r*i*m*g+o*l*m*g+r*l*m*g+o*s*m*g+r*s*m*g+i*s*m*g+l*s*m*g+o*i*d*g+
        r*i*d*g+o*s*d*g+r*s*d*g+i*s*d*g+o*m*d*g+r*m*d*g+s*m*d*g+a*(i*l*c+i*c*s+l*c*s+i*c*m+l*c*m+
        i*l*d+i*c*d+i*s*d+l*s*d+c*s*d+i*m*d+l*m*d+c*m*d+i*l*g+i*s*g+l*s*g+i*m*g+l*m*g+i*d*g+s*d*g+
        m*d*g+r*(i+s+m)*(c+d+g)+o*(r*(i+s+m)+(s+m)*(l+c+g)+i*(l+c+s+m+g)))+n*(r*l*c+i*l*c+r*c*m+
        i*c*m+l*c*m+r*l*d+i*l*d+r*c*d+i*c*d+r*m*d+i*m*d+l*m*d+c*m*d+r*l*g+i*l*g+r*m*g+i*m*g+l*m*g+
        r*d*g+i*d*g+m*d*g+o*(l*c+l*m+c*m+l*d+c*d+r*(l+m+d)+i*(l+m+d)+l*g+m*g+d*g)+a*(i*c+l*c+i*d+
        l*d+c*d+i*g+l*g+d*g+o*(r+i+l+c+g)+r*(c+d+g))))+n*(r*i*l*c+r*l*c*s+i*l*c*s+r*i*c*m+r*l*c*m+
        r*c*s*m+i*c*s*m+l*c*s*m+r*i*l*d+r*i*c*d+r*l*s*d+i*l*s*d+r*c*s*d+i*c*s*d+r*i*m*d+r*l*m*d+
        r*c*m*d+r*s*m*d+i*s*m*d+l*s*m*d+c*s*m*d+r*i*l*g+r*l*c*g+i*l*c*g+r*l*s*g+i*l*s*g+r*i*m*g+
        r*l*m*g+r*c*m*g+i*c*m*g+l*c*m*g+r*s*m*g+i*s*m*g+l*s*m*g+r*i*d*g+r*l*d*g+i*l*d*g+r*c*d*g+
        i*c*d*g+r*s*d*g+i*s*d*g+i*m*d*g+l*m*d*g+c*m*d*g+s*m*d*g+o*(l*c*s+l*s*m+c*s*m+l*s*d+c*s*d+
        r*((c+s)*(m+d)+i*(l+m+d)+l*(c+s+m+d))+l*c*g+l*s*g+l*m*g+c*m*g+s*m*g+l*d*g+c*d*g+s*d*g+i*(l+
        m+d)*(s+g))+a*(i*c*s+l*c*s+i*s*d+l*s*d+c*s*d+i*c*g+l*c*g+i*s*g+l*s*g+i*d*g+l*d*g+c*d*g+
        s*d*g+o*(l*s+c*s+r*(i+l+c+s)+l*g+c*g+s*g+i*(s+g))+r*(c*s+c*d+s*d+c*g+s*g+i*(c+d+g)+l*(c+d+
        g)))))
    )
