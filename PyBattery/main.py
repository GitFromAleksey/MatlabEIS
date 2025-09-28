import pybamm
import numpy as np


def Tutor1_HowToRunAModel():
    model = pybamm.lithium_ion.DFN()
    sim = pybamm.Simulation(model)
    s = sim.solve([0, 3600])
    # print(s.)
    sim.plot()

def Tutor2_CompareModels():
    models = [
        pybamm.lithium_ion.SPM(),
        pybamm.lithium_ion.SPMe(),
        pybamm.lithium_ion.DFN()
    ]
    sims = []
    for model in models:
        sim = pybamm.Simulation(model=model)
        sim.solve([0,3600])
        sims.append(sim)
    pybamm.dynamic_plot(sims)

def Tutor3_BasicPlotting():
    model = pybamm.lithium_ion.DFN()
    for var_name in model.variable_names():
        print(var_name)
    # electrolyte = model.variables.search("Voltage")
    # print(f'electrolyte:{electrolyte}')
    sim = pybamm.Simulation(model=model)
    sim.solve([0,3600])
    output_variables = ['Resistance [Ohm]', 'Power [W]','Current [A]','Voltage [V]']
    sim.plot(output_variables)
    sim.plot_voltage_components()
    sim.plot_voltage_components(split_by_electrode=True)

def Current(t):
    return 0.1*pybamm.sin(2*np.pi*t/60)
def Tutor4_SettingParameterValues():
    parameter_values = pybamm.ParameterValues('Chen2020')
    print(f'parameter_values:{parameter_values}')
    print(f'Electrode height:{parameter_values["Electrode height [m]"]} [m]')
    print(f'{parameter_values.search("electrolyte")}')
    model = pybamm.lithium_ion.DFN()
    model.print_parameter_info()
    parameter_values['Current function [A]'] = Current # 100
    sim = pybamm.Simulation(model=model, parameter_values=parameter_values)
    sim.solve([0,3600])
    sim.plot()

def Tutor5_RunExperiments():
    experiment = pybamm.Experiment(
        [
            "Discharge at C/10 for 10 hours or until 3.3 V",
            "Rest for 1 hour",
            "Charge at 1 A until 4.1 V",
            "Hold at 4.1 V until 50 mA",
            "Rest for 1 hour",
        ]
    )
    model = pybamm.lithium_ion.DFN()
    sim = pybamm.Simulation(model, experiment=experiment)
    sim.solve()
    sim.plot()
    # sim.solution.cycles[0].plot()
    for cycle in sim.solution.cycles:
        cycle.plot()
    # Direct instructions
    pybamm.step.current(1, duration="1 hour", termination="2.5 V")
    pybamm.step.string("Discharge at 1A for 1 hour or until 2.5V")

def main():
    print("pybamm")
    # HowToRunAModel()
    # Tutor2_CompareModels()
    # Tutor3_BasicPlotting()
    # Tutor4_SettingParameterValues()
    Tutor5_RunExperiments()

if __name__ == '__main__':
    main()
