import numpy as np
import math
from satex import Tensor

import matplotlib.pyplot as plt
import numpy as np
from .vtkplotter import Plotter
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .plot_vel_grid import plot_velocity_grid

from .. import Material
from .. import EBSD

from scipy.interpolate import griddata
import math

class Anisotropy:
    def __init__(self, stiffness_matrix, density):
        if stiffness_matrix is not None and density is not None:
            tensor_object = Tensor()
            self.cijkl = tensor_object.voigt_to_tensor(stiffness_matrix)
            self.rho = density
        else:
            tensor_object = Tensor()
            self.cijkl = None
            self.rho = None

    def christoffel_tensor(self, n):
        try:
            tik = np.zeros((3, 3))

            for i in range(3):
                for k in range(3):
                    tik[i, k] = np.tensordot(self.cijkl[i, :, k, :], np.outer(n, n))

            return tik
        except Exception as e:
            raise ValueError("Error in calculating the Christoffel tensor:", e)

    def wave_property(self, tik):
        try:
            eigenvalues, eigenvectors = np.linalg.eig(tik)
            indices = np.argsort(eigenvalues)[::-1]

            wave_moduli = [eigenvalues[i] for i in indices]
            polarization_directions = [eigenvectors[:, i] / np.linalg.norm(eigenvectors[:, i]) for i in indices]

            return tuple(wave_moduli), tuple(polarization_directions)
        except Exception as e:
            raise ValueError("Error in calculating wave properties:", e)

    def phase_velocity(self):
        try:
            vp = []
            vs1 = []
            vs2 = []

            theta_values = np.arange(0, math.pi + math.pi / 180, math.pi / 180)
            phi_values = np.arange(0, 2 * math.pi + math.pi / 180, math.pi / 180)

            theta, phi = np.meshgrid(theta_values, phi_values, indexing='ij')

            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)
            sin_phi = np.sin(phi)
            cos_phi = np.cos(phi)

            sin_theta_sin_phi = sin_theta * cos_phi
            sin_theta_cos_phi = sin_theta * sin_phi

            sqrt_rho = np.sqrt(self.rho)

            for i in range(theta.shape[0]):
                for j in range(phi.shape[1]):
                    n = np.array([sin_theta_sin_phi[i, j], sin_theta_cos_phi[i, j], cos_theta[i, j]])
                    tik = self.christoffel_tensor(n)
                    if tik is not None:
                        wave_moduli, polarization_directions = self.wave_property(tik)
                        vp.append(np.sqrt(wave_moduli[0] / self.rho))
                        vs1.append(np.sqrt(wave_moduli[1] / self.rho))
                        vs2.append(np.sqrt(wave_moduli[2] / self.rho))

            return tuple(vp), tuple(vs1), tuple(vs2)
        except Exception as e:
            raise ValueError("Error in calculating phase velocity:", e)
        
    def velocities(self):
        vp, vs1, vs2 = self.phase_velocity()
        return vp, vs1, vs2

    def anisotropy_values(self, stiffness_matrix = None, density = None, method = None, return_values=None):
        """
        Return values can ve maxvp, minv, maxvs1, minvs1, maxvs2, minvs2
        
        """

        if method == "array":
            anis_mat = []
            for i in stiffness_matrix:
                anis = Anisotropy(stiffness_matrix[i], density[i])
                anis_mat.append(self.anisotropy_values(anis))
                self.anisotropy_values(anis)
            return anis_mat

        vp, vs1, vs2 = self.velocities()
        maxvp = max(vp)
        minvp = min(vp)
        maxvs1 = max(vs1)
        minvs1 = min(vs1)
        maxvs2 = max(vs2)
        minvs2 = min(vs2)
        swaveAnisotropy_percent = 200 * (np.array(vs1) - np.array(vs2)) / (np.array(vs1) + np.array(vs2))
        max_vs_anisotropy_percent = max(swaveAnisotropy_percent)
        min_vs_anisotropy_percent = min(swaveAnisotropy_percent)
        p_wave_anisotropy_percent = 200 * (maxvp - minvp) / (maxvp + minvp)
        s1_wave_anisotropy_percent = 200 * (maxvs1 - minvs1) / (maxvs1 + minvs1)
        s2_wave_anisotropy_percent = 200 * (maxvs2 - minvs2) / (maxvs2 + minvs2)
        dvs = np.array(vs1) - np.array(vs2)
        maxdvs = max(dvs)
        vp_vs1 = np.array(vp) / np.array(vs1)
        AVpVs1 = 200 * (max(vp_vs1) - min(vp_vs1)) / (max(vp_vs1) + min(vp_vs1))

        if return_values == 'maxvp':
            return maxvp
        elif return_values == 'maxvs1':
            return maxvs1
        elif return_values == 'maxvs1':
            return maxvs1
        elif return_values == 'maxvs1':
            return maxvs1
        elif return_values == 'maxvs1':
            return maxvs1
        elif return_values == 'maxvs1':
            return maxvs1
        elif return_values == 'maxvs1':
            return maxvs1
        elif return_values == 'maxvs1':
            return maxvs1
        
        else:
            print("Max Vp: ", maxvp)
            print("Min Vp: ", minvp)
            print("Max Vs1: ", maxvs1)
            print("Min Vs1: ", minvs1)
            print("Max Vs2: ", maxvs2)
            print("Min Vs2: ", minvs2)
            print("Max vs anisotropy percent: ", max_vs_anisotropy_percent)
            print("Min vs anisotropy percent: ", min_vs_anisotropy_percent)
            print("P wave anisotropy percent: ", p_wave_anisotropy_percent)
            print("S1 Wave anisotropy percent: ", s1_wave_anisotropy_percent)
            print("S2 Wave anisotropy percent: ", s2_wave_anisotropy_percent)
            print("Velocity difference: ", maxdvs)
            print("Vp/Vs1 ratio: ", AVpVs1)
            return {
                'maxvp': maxvp,
                'minvp': minvp,
                'maxvs1': maxvs1,
                'minvs1': minvs1,
                'maxvs2': maxvs2,
                'minvs2': minvs2,
                'max_vs_anisotropy_percent': max_vs_anisotropy_percent,
                'min_vs_anisotropy_percent': min_vs_anisotropy_percent,
                'p_wave_anisotropy_percent': p_wave_anisotropy_percent,
                's1_wave_anisotropy_percent': s1_wave_anisotropy_percent,
                's2_wave_anisotropy_percent': s2_wave_anisotropy_percent,
                'maxdvs': maxdvs,
                'AVpVs1': AVpVs1
            }
        
    def plot_velocities(self, pressure_range, temperature_range, return_type, is_ebsd = False, phase = None, grid = [5, 5], filename = None, *args):
        """
        Return values can ve maxvp, minv, maxvs1, minvs1, maxvs2, minvs2 
        args can be [0, 1, 2, 3]
        give filename is is_ebsd is True
        """
        plot_velocity_grid(pressure_range, temperature_range, return_type, is_ebsd = False, phase = phase, grid = [5, 5], filename = None, *args)



    def plot(self, colormap="RdBu_r"):
        try:
            fig, axs = plt.subplots(2, 3, figsize=(15, 10))
            step = math.pi / 180

            # texts for each subplot
            texts = ['Ratio of VP to VS1', 'Velocity of P-waves (VP)', 'Velocity of S1-waves (VS1)', 
                    'Velocity of S2-waves (VS2)', 'Anisotropy measure for VP and VS1', 
                    'Anisotropy measure for VP and VS2']
            
            for i, ax in enumerate(axs.flat):
                x = []
                y = []
                c = []

                for theta in np.arange(0, math.pi / 2 + step, step):
                    for phi in np.arange(0, 2 * math.pi + step, step):
                        n = np.array([math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)])
                        tik = self.christoffel_tensor(n)
                        if tik is not None:
                            wave_moduli, _ = self.wave_property(tik)
                            vp = math.sqrt(wave_moduli[0] / self.rho)
                            vs1 = math.sqrt(wave_moduli[1] / self.rho)
                            vs2 = math.sqrt(wave_moduli[2] / self.rho)
                            vpvs1 = vp/vs1
                            x.append(n[0] / (1 + n[2]))
                            y.append(n[1] / (1 + n[2]))
                            if i == 0:
                                c.append(vpvs1)
                            elif i == 1:
                                c.append(vp)
                            elif i == 2:
                                c.append(vs1)
                            elif i == 3:
                                c.append(vs2)
                            elif i == 4:
                                c.append((vp - vs1) / (vp + vs1))
                            elif i == 5:
                                c.append((vp - vs2) / (vp + vs2))

                # Interpolate onto a regular grid
                xi = np.linspace(min(x), max(x), 100)
                yi = np.linspace(min(y), max(y), 100)
                xi, yi = np.meshgrid(xi, yi)
                zi = griddata((x, y), c, (xi, yi), method='linear')

                # Plotting contour lines for each subplot
                contours = ax.contour(xi, yi, zi, 5, colors='black')
                ax.clabel(contours, inline=True, fontsize=8)

                sc = ax.scatter(x, y, c=c, cmap=colormap, s=5)  # Reduce scatter dot size s for clarity
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.set_aspect('equal', 'box')

                # Adding above text at the bottom of each plot
                ax.text(0.5, -0.15, texts[i], ha='center', transform=ax.transAxes)

            axs[0, 0].set_title('VP/VS1')
            axs[0, 1].set_title('VP')
            axs[0, 2].set_title('VS1')
            axs[1, 0].set_title('VS2')
            axs[1, 1].set_title('AVpVs1')
            axs[1, 2].set_title('AVpVs2')

            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"An error occurred: {e}")


    def plotly(self):
        try:
            fig = go.Figure()

            step = math.pi / 180

            fig = make_subplots(rows=2, cols=3, subplot_titles=("VP/VS1", "VP", "VS1", "VS2", "AVpVs1", "AVpVs2"))

            for i in range(6):
                x = []
                y = []
                c = []

                for theta in np.arange(0, math.pi / 2 + step, step):
                    for phi in np.arange(0, 2 * math.pi + step, step):
                        n = np.array([math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)])
                        tik = self.christoffel_tensor(n)
                        if tik is not None:
                            wave_moduli, _ = self.wave_property(tik)
                            vp = math.sqrt(wave_moduli[0] / self.rho)
                            vs1 = math.sqrt(wave_moduli[1] / self.rho)
                            vs2 = math.sqrt(wave_moduli[2] / self.rho)
                            vpvs1 = vp/vs1
                            x.append(n[0] / (1 + n[2]))
                            y.append(n[1] / (1 + n[2]))
                            if i == 0:
                                c.append(vpvs1)
                            elif i == 1:
                                c.append(vp)
                            elif i == 2:
                                c.append(vs1)
                            elif i == 3:
                                c.append(vs2)
                            elif i == 4:
                                c.append((vp - vs1) / (vp + vs1))
                            elif i == 5:
                                c.append((vp - vs2) / (vp + vs2))

                row = i // 3 + 1
                col = i % 3 + 1
                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=c,
                        colorscale='RdBu',
                        colorbar=dict(title='Colorbar Title'),
                    ),
                    name='',
                ), row=row, col=col)

            fig.update_layout(
                title="Plot Title",
                xaxis_title="x",
                yaxis_title="y"
            )

            fig.show()
        except Exception as e:
            raise ValueError("Error in plotting:", e)


            
    def plotter_vs_splitting(self, density, voigt_stiffness):

        Plotter.plot_vs_splitting(voigt_stiffness, density)

    def plotter_vp(self, density, voigt_stiffness):

        Plotter.plot_vp(voigt_stiffness, density)

    def plotter_vs1(self, density, voigt_stiffness):

        Plotter.plot_vp(voigt_stiffness, density)

    def plotter_vs2(self, density, voigt_stiffness):

        Plotter.plot_vp(voigt_stiffness, density)
