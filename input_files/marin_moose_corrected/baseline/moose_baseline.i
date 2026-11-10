# Matched crystal single-element: ONE 1x1x1 mm HEX, X tension.
# Derived from the previously tested Voce verification file.
# Compare to abaqus_marin_baseline.inp: t=0..1 s, Ux=0.05t, strain=5%.
# Crystal parameters and orientation pinned to the supplied UMAT external data.
# Internal integration and slip kinetics may still differ between codes.
# See README.md for Euler convention, stiffness, slip-system, and hardening checks.

[Mesh]
  [single_element]
    type = GeneratedMeshGenerator
    dim = 3
    nx = 1
    ny = 1
    nz = 1
    xmin = -0.5
    xmax = 0.5
    ymin = -0.5
    ymax = 0.5
    zmin = 0.0
    zmax = 1.0
  []
[]

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

# Modern Solid Mechanics QuasiStatic Physics action
[Physics/SolidMechanics/QuasiStatic]
  [all]
    strain = FINITE
    add_variables = true
    generate_output = 'stress_xx stress_yy stress_zz'
  []
[]

[BCs]
  # Symmetry / roller boundary conditions
  [fix_x]
    type = DirichletBC
    variable = disp_x
    boundary = left     # x = -0.5
    value = 0.0
  []
  [fix_y]
    type = DirichletBC
    variable = disp_y
    boundary = bottom   # y = -0.5
    value = 0.0
  []
  [fix_z]
    type = DirichletBC
    variable = disp_z
    boundary = back     # z = 0
    value = 0.0
  []

  # Same as Abaqus: Ux=0.05*t on x=+0.5; length=1 mm; t_end=1 s
  [pull_x]
    type = FunctionDirichletBC
    variable = disp_x
    boundary = right    # x = +0.5
    function = '0.05 * t'
  []
[]

[Materials]
  # Single crystal anisotropic elasticity tensor (F321 parameters from Table 3)
  [elasticity_tensor]
    type = ComputeElasticityTensorCP
    C_ijkl = '185000 125000 125000 185000 125000 185000 118000 118000 118000'
    fill_method = symmetric9
    # Verified: Kocks (275.27, 80.07, 303.66) -> Bunge (5.27,80.07,146.34)
    # UMAT AnglesToRotMatrix == MOOSE active CP matrix for these angles.
    euler_angle_1 = 5.27
    euler_angle_2 = 80.07
    euler_angle_3 = 146.34
  []

  # Crystal Plasticity Stress Update Manager
  [stress]
    type = ComputeMultipleCrystalPlasticityStress
    crystal_plasticity_models = 'voce_update'
    tan_mod_type = exact
    maximum_substep_iteration = 5      # Reduced from 30 to prevent 2^30 substepping stall
  []

  # Custom KalidindiVoce constitutive model under test
  [voce_update]
    type = CrystalPlasticityKalidindiVoceUpdate
    number_slip_systems = 12
    slip_sys_file_name = slip_systems_FCC_MAT1.txt
    slip_increment_tolerance = 0.05             # Substep allowable slip increment tolerance

    # Flow rule parameters single crystal 
    ao = 1e-3                       #initial slip rate (1/s)
    xm = 0.05

    # Directly matched to this case Mat1/fcc.sx values (mode 1).
    r = 1.0 # isotropic hardening; require UMAT hardmtx all ones
    h = 190 #fixed state hardening rate scaling coeff (MPa)
    gss_initial = 35 #slip system initial strength (MPa)
    gss_sat_initial = 110 #initial slip system saturation strength (MPa)
    ao_sat = 5e10
    xm_gss = 0.0 # constant saturation baseline (matches UMAT xms=0 when configured)
    n_gss = 1
    is_gss_sat_constant = true
  []
[]

# -------------------------------------------------------------
# Diagnostic output: all 12 slip strengths and signed slip rates
# Material vector property indices are 0-based: 0,...,11
# MONOMIAL/CONSTANT: elementwise values at one element
# -------------------------------------------------------------
[AuxVariables]
  [gss_01]
    family = MONOMIAL
    order = CONSTANT
  []
  [gss_02]
    family = MONOMIAL
    order = CONSTANT
  []
  [gss_03]
    family = MONOMIAL
    order = CONSTANT
  []
  [gss_04]
    family = MONOMIAL
    order = CONSTANT
  []
  [gss_05]
    family = MONOMIAL
    order = CONSTANT
  []
  [gss_06]
    family = MONOMIAL
    order = CONSTANT
  []
  [gss_07]
    family = MONOMIAL
    order = CONSTANT
  []
  [gss_08]
    family = MONOMIAL
    order = CONSTANT
  []
  [gss_09]
    family = MONOMIAL
    order = CONSTANT
  []
  [gss_10]
    family = MONOMIAL
    order = CONSTANT
  []
  [gss_11]
    family = MONOMIAL
    order = CONSTANT
  []
  [gss_12]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_01]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_02]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_03]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_04]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_05]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_06]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_07]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_08]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_09]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_10]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_11]
    family = MONOMIAL
    order = CONSTANT
  []
  [slip_rate_12]
    family = MONOMIAL
    order = CONSTANT
  []
  [total_abs_slip_rate]
    family = MONOMIAL
    order = CONSTANT
  []
[]

[AuxKernels]
  [extract_gss_01]
    type = MaterialStdVectorAux
    variable = gss_01
    property = slip_resistance
    index = 0
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_01]
    type = MaterialStdVectorAux
    variable = slip_rate_01
    property = slip_increment
    index = 0
    execute_on = 'initial timestep_end'
  []
  [extract_gss_02]
    type = MaterialStdVectorAux
    variable = gss_02
    property = slip_resistance
    index = 1
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_02]
    type = MaterialStdVectorAux
    variable = slip_rate_02
    property = slip_increment
    index = 1
    execute_on = 'initial timestep_end'
  []
  [extract_gss_03]
    type = MaterialStdVectorAux
    variable = gss_03
    property = slip_resistance
    index = 2
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_03]
    type = MaterialStdVectorAux
    variable = slip_rate_03
    property = slip_increment
    index = 2
    execute_on = 'initial timestep_end'
  []
  [extract_gss_04]
    type = MaterialStdVectorAux
    variable = gss_04
    property = slip_resistance
    index = 3
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_04]
    type = MaterialStdVectorAux
    variable = slip_rate_04
    property = slip_increment
    index = 3
    execute_on = 'initial timestep_end'
  []
  [extract_gss_05]
    type = MaterialStdVectorAux
    variable = gss_05
    property = slip_resistance
    index = 4
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_05]
    type = MaterialStdVectorAux
    variable = slip_rate_05
    property = slip_increment
    index = 4
    execute_on = 'initial timestep_end'
  []
  [extract_gss_06]
    type = MaterialStdVectorAux
    variable = gss_06
    property = slip_resistance
    index = 5
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_06]
    type = MaterialStdVectorAux
    variable = slip_rate_06
    property = slip_increment
    index = 5
    execute_on = 'initial timestep_end'
  []
  [extract_gss_07]
    type = MaterialStdVectorAux
    variable = gss_07
    property = slip_resistance
    index = 6
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_07]
    type = MaterialStdVectorAux
    variable = slip_rate_07
    property = slip_increment
    index = 6
    execute_on = 'initial timestep_end'
  []
  [extract_gss_08]
    type = MaterialStdVectorAux
    variable = gss_08
    property = slip_resistance
    index = 7
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_08]
    type = MaterialStdVectorAux
    variable = slip_rate_08
    property = slip_increment
    index = 7
    execute_on = 'initial timestep_end'
  []
  [extract_gss_09]
    type = MaterialStdVectorAux
    variable = gss_09
    property = slip_resistance
    index = 8
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_09]
    type = MaterialStdVectorAux
    variable = slip_rate_09
    property = slip_increment
    index = 8
    execute_on = 'initial timestep_end'
  []
  [extract_gss_10]
    type = MaterialStdVectorAux
    variable = gss_10
    property = slip_resistance
    index = 9
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_10]
    type = MaterialStdVectorAux
    variable = slip_rate_10
    property = slip_increment
    index = 9
    execute_on = 'initial timestep_end'
  []
  [extract_gss_11]
    type = MaterialStdVectorAux
    variable = gss_11
    property = slip_resistance
    index = 10
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_11]
    type = MaterialStdVectorAux
    variable = slip_rate_11
    property = slip_increment
    index = 10
    execute_on = 'initial timestep_end'
  []
  [extract_gss_12]
    type = MaterialStdVectorAux
    variable = gss_12
    property = slip_resistance
    index = 11
    execute_on = 'initial timestep_end'
  []
  [extract_slip_rate_12]
    type = MaterialStdVectorAux
    variable = slip_rate_12
    property = slip_increment
    index = 11
    execute_on = 'initial timestep_end'
  []
  [compute_total_abs_slip_rate]
    type = ParsedAux
    variable = total_abs_slip_rate
    coupled_variables = 'slip_rate_01 slip_rate_02 slip_rate_03 slip_rate_04 slip_rate_05 slip_rate_06 slip_rate_07 slip_rate_08 slip_rate_09 slip_rate_10 slip_rate_11 slip_rate_12'
    expression = 'abs(slip_rate_01)+abs(slip_rate_02)+abs(slip_rate_03)+abs(slip_rate_04)+abs(slip_rate_05)+abs(slip_rate_06)+abs(slip_rate_07)+abs(slip_rate_08)+abs(slip_rate_09)+abs(slip_rate_10)+abs(slip_rate_11)+abs(slip_rate_12)'
    execute_on = 'initial timestep_end'
  []
[]

# -------------------------------------------------------------
# CSV postprocessors: g(Gamma) vs isotropic Voce analytic law
# exact continuous solution: g = 110 - 75*exp(-190*Gamma/75)
# Gamma computed via backward rectangular rule on global steps
# (approximate if CP internal substepping occurs).
# -------------------------------------------------------------
[Postprocessors]
  [stress_xx]
    type = ElementAverageValue
    variable = stress_xx
    execute_on = 'initial timestep_end'
  []
  [strain_xx]
    type = SideAverageValue
    variable = disp_x
    boundary = right
    execute_on = 'initial timestep_end'
    # Engineering strain = Ux(x=+0.5)/Lx, Lx=1 mm
  []
  [gss_01_num]
    type = ElementAverageValue
    variable = gss_01
    execute_on = 'initial timestep_end'
  []
  [gss_04_num]
    type = ElementAverageValue
    variable = gss_04
    execute_on = 'initial timestep_end'
  []
  [gss_12_num]
    type = ElementAverageValue
    variable = gss_12
    execute_on = 'initial timestep_end'
  []
  [Gamma_dot]
    type = ElementAverageValue
    variable = total_abs_slip_rate
    execute_on = 'initial timestep_end'
  []
  [Gamma_abs]
    type = TimeIntegratedPostprocessor
    value = Gamma_dot
    time_integration_scheme = implicit-euler
    execute_on = 'initial timestep_end'
  []
  [gss_analytic]
    type = ParsedPostprocessor
    pp_names = Gamma_abs
    expression = '110 - 75*exp(-(190.0/75.0)*Gamma_abs)'
    execute_on = 'initial timestep_end'
  []
  [gss_01_error]
    type = ParsedPostprocessor
    pp_names = 'gss_01_num gss_analytic'
    expression = 'gss_01_num - gss_analytic'
    execute_on = 'initial timestep_end'
  []
  [gss_spread_01_12]
    type = ParsedPostprocessor
    pp_names = 'gss_01_num gss_12_num'
    expression = 'gss_01_num - gss_12_num'
    execute_on = 'initial timestep_end'
  []
[]

[Executioner]
  type = Transient
  solve_type = 'PJFNK'

  # Direct LU solver (ideal for 1-element unit testing, prevents ASM subdomain zero-block errors)
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'

  nl_abs_tol = 1.0e-8
  nl_rel_tol = 1.0e-6
  nl_max_its = 25

  start_time = 0.0
  end_time = 1.0

  dtmin = 1.0e-8
  dtmax = 0.005

  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 1.0e-6   # Same initial nominal increment as Abaqus
    optimal_iterations = 6
    growth_factor = 1.5
    cutback_factor = 0.5
  []
[]

[Outputs]
  file_base = moose_baseline
  exodus = true
  csv = true
[]
