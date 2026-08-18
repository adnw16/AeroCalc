# Airfoil-surface-area-to-volume-calculator-shape-optimiser

This project is a Python implementation of my individual academic research project. In the original paper, I investigated the surface area-to-volume (SA:V) ratio of bodies of revolution generated from different airfoil shapes, specifically comparing a Sears-Haack body, a NACA0012 airfoil, and a custom airfoil design.

**The paper derived:**
- Volume: \(V = \int_a^b \pi f(x)^2 dx\)
- Surface Area: \(SA = \int_a^b 2\pi f(x) \sqrt{1 + (f'(x))^2} dx\)
- The Sears-Haack body formula: \(r(x) = R_{max}[4x(1-x)]^{3/4}\)

**This project extends that work by:**
- Automating the data fetching process via the [Foil.tools API](https://foil.tools/api-docs)
- Bypassing manual calculation for results
- Visualizing the results with plots
