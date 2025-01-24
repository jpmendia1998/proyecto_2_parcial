import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Productivity Index
def j(q_test, pwf_test, pr, pb, ef=1, ef2=None):
    if ef == 1:  # Darcy & Vogel
        if pwf_test >= pb:  # Subsaturated reservoir
            J = q_test / (pr - pwf_test)
        else:  # Saturated reservoir
            J = q_test / ((pr - pb) + (pb / 1.8) * \
                          (1 - 0.2 * (pwf_test / pb) - 0.8 * (pwf_test / pb) ** 2))

    elif ef != 1 and ef2 is None:  # Darcy & Standing
        if pwf_test >= pb:  # Subsaturated reservoir
            J = q_test / (pr - pwf_test)
        else:  # Saturated reservoir
            J = q_test / ((pr - pb) + (pb / 1.8) * \
                          (1.8 * (1 - pwf_test / pb) - 0.8 * ef * (1 - pwf_test / pb) ** 2))

    elif ef != 1 and ef2 is not None:  # Darcy & Standing
        if pwf_test >= pb:  # Subsaturated reservoir
            J = ((q_test / (pr - pwf_test)) / ef) * ef2
        else:  # Saturated reservoir
            J = ((q_test / ((pr - pb) + (pb / 1.8) * \
                            (1.8 * (1 - pwf_test / pb) - 0.8 * \
                             ef * (1 - pwf_test / pb) ** 2))) / ef) * ef2
    return J

# Q(bpd) @ Pb
def Qb(q_test, pwf_test, pr, pb, ef=1, ef2=None):
    qb = j(q_test, pwf_test, pr, pb, ef, ef2) * (pr - pb)
    return qb

# AOF(bpd)
def aof(q_test, pwf_test, pr, pb, ef=1, ef2=None):
    # Darcy & Vogel
    if (ef == 1 and ef2 is None):
        # Yac. subsaturado
        if pr > pb:
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef=1) + ((j(q_test, pwf_test, pr, pb) * pb) / 1.8)
        # Yac. Saturado
        else:
            AOF = q_test / (1 - 0.2 * (pwf_test / pr) - 0.8 * (pwf_test / pr) ** 2)

    # Darcy & Standing
    elif (ef < 1 and ef2 is None):
        # Yac. subsatuado
        if pr > pb:
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb, ef) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef) + ((j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * (
                            1.8 - 0.8 * ef)
        # Yac. saturado
        else:
            AOF = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (1 - pwf_test / pr) ** 2)) * (
                        1.8 * ef - 0.8 * ef ** 2)

    # Darcy & Standing
    elif (ef > 1 and ef2 is None):
        # Yac. subsaturado
        if pr > pb:
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb, ef) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef) + ((j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * (
                            0.624 + 0.376 * ef)
        # Yac. saturado
        else:
            AOF = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (1 - pwf_test / pr) ** 2)) * (
                        0.624 + 0.376 * ef)

    # Darcy & Standing (stimulation)
    elif (ef < 1 and ef2 >= 1):
        # Yac. subsaturado
        if pr > pb:
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb, ef, ef2) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef, ef2) + (j(q_test, pwf_test, pr, pb, ef, ef2) * pb / 1.8) * (
                            0.624 + 0.376 * ef2)
        # Yac. saturado
        else:
            AOF = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (1 - pwf_test / pr) ** 2)) * (
                        0.624 + 0.376 * ef2)

    # Darcy & Standing (Higher skin)
    elif (ef > 1 and ef2 <= 1):
        # Yac. subsaturado
        if pr > pb:
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb, ef, ef2) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef, ef2) + (j(q_test, pwf_test, pr, pb, ef, ef2) * pb / 1.8) * (
                            1.8 - 0.8 * ef2)
        # Yac. saturado
        else:
            AOF = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (1 - pwf_test / pr) ** 2)) * (
                        1.8 - 0.8 * ef2 ** 2)

    return AOF

# Seccion de caudales

# Qo (bpd) @ Darcy Conditions
def qo_darcy(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    qo = j(q_test, pwf_test, pr, pb) * (pr - pwf)
    return qo

#Qo(bpd) @ vogel conditions
def qo_vogel(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    qo = aof(q_test, pwf_test, pr, pb) * \
         (1 - 0.2 * (pwf / pr) - 0.8 * ( pwf / pr)**2)
    return qo


# Qo(bpd) @ vogel conditions
def qo_ipr_compuesto(q_test, pwf_test, pr, pwf, pb):
    if pr > pb:  # Yac. subsaturado
        if pwf >= pb:
            qo = qo_darcy(q_test, pwf_test, pr, pwf, pb)
        elif pwf < pb:
            qo = Qb(q_test, pwf_test, pr, pb) + \
                 ((j(q_test, pwf_test, pr, pb) * pb) / 1.8) * \
                 (1 - 0.2 * (pwf / pb) - 0.8 * (pwf / pb) ** 2)

    elif pr <= pb:  # Yac. Saturado
        qo = qo_vogel(q_test, pwf_test, pr, pwf, pb)

    return qo

# Qo(bpd) @Standing Conditions
def qo_standing(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    if pr <= pb:  # Yacimiento saturado
        q = q_test * ef * ((pr**2 - pwf**2) / (pr**2 - pwf_test**2))
    else:  # Yacimiento sub-saturado
        if pwf >= pb:
            ef = ef if ef2 is None else ef * ef2
            q = q_test * ef * ((pr - pwf) / (pr - pwf_test))
        else:  # pwf < pb
            q_saturado = q_test * ef * ((pr**2 - pb**2) / (pr**2 - pwf_test**2))
            q_subsaturado = q_test * ef * ((pb - pwf) / (pr - pwf_test))
            q = q_saturado + q_subsaturado

    return q

# Flujo monofasico
def j_darcy(ko, h, bo, uo, re, rw, s, flow_regime='seudocontinuo'):
    if flow_regime == 'seudocontinuo':
        J_darcy = ko * h / (141.2 * bo * uo * (np.log(re / rw) - 0.75 + s))

    elif flow_regime == 'continuo':
        J_darcy = ko * h / (141.2 * bo * uo * (np.log(re / rw) + s))

    return J_darcy

def q_darcy(ko,h,pr,pwf,s,uo,bo,re,rw, flow_regime='seudocontinuo'):
    if flow_regime == 'seudocontinuo':
        Q_darcy=(ko*h*(pr-pwf))/(141.2*bo*(np.log(re / rw)-0.75 + s))
    elif flow_regime == 'continuo':
        Q_darcy=(ko*h*(pr-pwf))/(141.2*bo*(np.log(re / rw) + s))
    return Q_darcy


# IPR Curve
def IPR_curve_methods(q_test, pwf_test, pr, pwf: list, pb, ef=1, ef2=None, method=None):
    fig, ax = plt.subplots(figsize=(20, 10))
    df = pd.DataFrame()
    df['Pwf(psia)'] = pwf

    if method == 'Darcy':
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_darcy(q_test, pwf_test, pr, x, pb))
    elif method == 'Vogel':
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_vogel(q_test, pwf_test, pr, x, pb))
    elif method == 'IPR_compuesto':
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_ipr_compuesto(q_test, pwf_test, pr, x, pb))
    elif method == "Standing":
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_standing(q_test, pwf_test, pr, x, pb, ef, ef2))

    df = df.sort_values(by='Qo(bpd)', ascending=True)

    if df.empty:
        print("El DataFrame está vacío.")
        return

    x = df['Qo(bpd)']
    y = df['Pwf(psia)']

    # Spline interpolation
    X_Y_Spline = make_interp_spline(x, y)
    X_ = np.linspace(x.min(), x.max(), 500)
    Y_ = X_Y_Spline(X_)

    # Plot
    ax.plot(X_, Y_, c='g')
    ax.set_xlabel('Qo(bpd)')
    ax.set_ylabel('Pwf(psia)')
    ax.set_title('IPR')
    ax.set(xlim=(0, df['Qo(bpd)'].max() + 10), ylim=(0, df['Pwf(psia)'].max() + 100))

    if method != "Darcy":
        ax.annotate(
            'Bubble Point', xy=(Qb(q_test, pwf_test, pr, pb), pb),
            xytext=(Qb(q_test, pwf_test, pr, pb) + 100, pb + 100),
            arrowprops=dict(arrowstyle='->', lw=1)
        )
        ax.axhline(y=pb, color='r', linestyle='--')
        ax.axvline(x=Qb(q_test, pwf_test, pr, pb), color='r', linestyle='--')

    ax.grid()

    # Mostrar la gráfica en Streamlit
    st.pyplot(fig)

def Qo(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    qo = 0  # Initialize qo with a default value

    if ef == 1 and ef2 is None:
        if pr > pb:  # Yacimiento subsaturado
            if pwf >= pb:
                qo = qo_darcy(q_test, pwf_test, pr, pwf, pb)
            elif pwf < pb:
                qo = Qb(q_test, pwf_test, pr, pb) + \
                    ((j(q_test, pwf_test, pr, pb) * pb) / 1.8) * \
                    (1 - 0.2 * (pwf / pb) - 0.8 * (pwf / pb)**2)
        else:  # Yacimiento saturado
            qo = qo_vogel(q_test, pwf_test, pr, pwf, pb)

    elif ef != 1 and ef2 is None:
        if pr > pb:  # Yacimiento subsaturado
            if pwf >= pb:
                qo = qo_darcy(q_test, pwf_test, pr, pwf, pb, ef)
            elif pwf < pb:
                qo = Qb(q_test, pwf_test, pr, pb, ef) + \
                    ((j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * \
                    (1.8 * (1 - pwf / pb) - 0.8 * ef * (1 - pwf / pb)**2)
        else:  # Yacimiento saturado
            qo = qo_standing(q_test, pwf_test, pr, pwf, pb, ef)

    elif ef != 1 and ef2 is not None:
        if pr > pb:  # Yacimiento subsaturado
            if pwf >= pb:
                qo = qo_darcy(q_test, pwf_test, pr, pwf, pb, ef, ef2)
            elif pwf < pb:
                qo = Qb(q_test, pwf_test, pr, pb, ef, ef2) + \
                    ((j(q_test, pwf_test, pr, pb, ef, ef2) * pb) / 1.8) * \
                    (1.8 * (1 - pwf / pb) - 0.8 * ef * (1 - pwf / pb)**2)
        else:  # Yacimiento saturado
            qo = qo_standing(q_test, pwf_test, pr, pwf, pb, ef, ef2)

    else:
        raise ValueError("Invalid combination of ef and ef2 values")

    return qo