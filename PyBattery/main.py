import pybamm



def GettingStarted():
    model = pybamm.lithium_ion.DFN()
    sim = pybamm.Simulation(model)
    s = sim.solve([0, 3600])
    # print(s.t)
    sim.plot()

def main():
    print("pybamm")
    GettingStarted()

if __name__ == '__main__':
    main()
