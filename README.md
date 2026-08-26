# AeroCalc: an airfoil-sa:v-calculator

This project is a Python implementation of my individual academic research project. In the original paper, I investigated the surface area-to-volume (SA:V) ratio of bodies of revolution generated from different airfoil shapes, specifically comparing a Sears-Haack body, a NACA0012 airfoil, and a custom airfoil design.

Note: Chart visualizations and output styling were accelerated using AI generation tools.

**The paper derived the mathematical formulae for:**
- Volume
- Surface Area
- The Sears-Haack body formula

**This project extends that work by:**
- Automating the data fetching process via the [Foil.tools API](https://foil.tools/api-docs)
- Bypassing manual calculation for results
- Visualizing the results with plots

**Future implementation**
- Implementation for non-symmetrical airfoils
- Bézier curve generated airfoil shape optimisation
