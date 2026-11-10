# 3% engineering strain — Marin comparison candidate: n=1, r=1.0, constant gs=True.
# Constitutive law: n_gss=1, r=1.0, gs=110*(Gamma_dot/1e-5)^0.005
# for Gamma_dot>0, otherwise gs=110 MPa, exactly matching the supplied C++.
# Exported gs_formula_saved is RECONSTRUCTED from the endpoint slip rate;
# it is not an internal material property. For direct gs export, see README.
# Two files differ ONLY in dtmax (0.05 and 0.025 s).
# Use with the supplied slip_systems_FCC.txt in the working directory.

[Mesh]
  [single_element]
    type = GeneratedMeshGenerator
    dim = 3
    nx = 1
    ny = 1
    nz = 1
    xmin = 0.0
    xmax = 1.0
    ymin = 0.0
    ymax = 1.0
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
    boundary = left     # x = 0
    value = 0.0
  []
  [fix_y]
    type = DirichletBC
    variable = disp_y
    boundary = bottom   # y = 0
    value = 0.0
  []
  [fix_z]
    type = DirichletBC
    variable = disp_z
    boundary = back     # z = 0
    value = 0.0
  []

  # Prescribed axial displacement on front face (z = 1): 3% engineering strain over 10 s
  [pull_z]
    type = FunctionDirichletBC
    variable = disp_z
    boundary = front    # z = 1
    function = '0.003 * t'
  []
[]

[Materials]
  # Single crystal anisotropic elasticity tensor (F321 parameters from Table 3)
  [elasticity_tensor]
    type = ComputeElasticityTensorCP
    C_ijkl = '185000 125000 125000 185000 104374 185000 118000 118000 118000'
    fill_method = symmetric9
    # Initial crystal orientation (Bunge Euler angles in degrees)
    euler_angle_1 = 185.27
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
    slip_sys_file_name = slip_systems_FCC.txt
    slip_increment_tolerance = 0.05             # Substep allowable slip increment tolerance

    # Flow rule parameters single crystal 
    ao = 1e-3                       #initial slip rate (1/s)
    xm = 0.05

    # slip resistance params single crystal Al (EB Marin paper)
    r = 1.0 # plane-based interaction coefficient
    h = 190 #fixed state hardening rate scaling coeff (MPa)
    gss_initial = 35 #slip system initial strength (MPa)
    gss_sat_initial = 110 # initial slip system saturation strength (MPa)
    ao_sat = 1e-05 # reference total slip rate (1/s)
    n_gss = 1             # nonlinear Voce exponent (test)
    xm_gss = 0.005 # saturation rate scaling exponent
    is_gss_sat_constant = true
  []
[]

# -------------------------------------------------------------
# Diagnostic output for nonlinear anisotropic Voce verification (r = 1.4)
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
  [weighted_rate_plane_1]
    family = MONOMIAL
    order = CONSTANT
  []
  [weighted_rate_plane_2]
    family = MONOMIAL
    order = CONSTANT
  []
  [weighted_rate_plane_3]
    family = MONOMIAL
    order = CONSTANT
  []
  [weighted_rate_plane_4]
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
  [compute_weighted_rate_plane_1]
    type = ParsedAux
    variable = weighted_rate_plane_1
    coupled_variables = 'total_abs_slip_rate slip_rate_01 slip_rate_02 slip_rate_03'
    # q=1 on own plane, 1.4 on other planes
    expression = '1.4*total_abs_slip_rate - 0.4*(abs(slip_rate_01)+abs(slip_rate_02)+abs(slip_rate_03))'
    execute_on = 'initial timestep_end'
  []
  [compute_weighted_rate_plane_2]
    type = ParsedAux
    variable = weighted_rate_plane_2
    coupled_variables = 'total_abs_slip_rate slip_rate_04 slip_rate_05 slip_rate_06'
    # q=1 on own plane, 1.4 on other planes
    expression = '1.4*total_abs_slip_rate - 0.4*(abs(slip_rate_04)+abs(slip_rate_05)+abs(slip_rate_06))'
    execute_on = 'initial timestep_end'
  []
  [compute_weighted_rate_plane_3]
    type = ParsedAux
    variable = weighted_rate_plane_3
    coupled_variables = 'total_abs_slip_rate slip_rate_07 slip_rate_08 slip_rate_09'
    # q=1 on own plane, 1.4 on other planes
    expression = '1.4*total_abs_slip_rate - 0.4*(abs(slip_rate_07)+abs(slip_rate_08)+abs(slip_rate_09))'
    execute_on = 'initial timestep_end'
  []
  [compute_weighted_rate_plane_4]
    type = ParsedAux
    variable = weighted_rate_plane_4
    coupled_variables = 'total_abs_slip_rate slip_rate_10 slip_rate_11 slip_rate_12'
    # q=1 on own plane, 1.4 on other planes
    expression = '1.4*total_abs_slip_rate - 0.4*(abs(slip_rate_10)+abs(slip_rate_11)+abs(slip_rate_12))'
    execute_on = 'initial timestep_end'
  []
[]

# -------------------------------------------------------------
# CSV postprocessors: all 12 strengths, Gamma_dot, Lambda_dot by plane,
# and sampled reconstructed saturation. No constant-gs analytic solution
# exists for the variable-gs test; use check_voce_3pct.py to evaluate
# independent integration of the exported rate histories.
# -------------------------------------------------------------
[Postprocessors]
  # Reconstruct saturation using the same constitutive expression at saved steps.
  # Important: not the internal saturation at intermediate Newton/substep states.
  [gs_formula_saved]
    type = ParsedPostprocessor
    pp_names = Gamma_dot
    expression = 'if(Gamma_dot>0,110*pow(Gamma_dot/1e-5,0.005),110)'
    execute_on = 'initial timestep_end'
  []
  [gs_minus_g0_saved]
    type = ParsedPostprocessor
    pp_names = gs_formula_saved
    expression = 'gs_formula_saved-35'
    execute_on = 'initial timestep_end'
  []
  [stress_zz]
    type = ElementAverageValue
    variable = stress_zz
    execute_on = 'initial timestep_end'
  []
  [strain_zz]
    type = SideAverageValue
    variable = disp_z
    boundary = front
    execute_on = 'initial timestep_end'
    # Engineering strain = front displacement / L0; L0=1
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
  [gss_spread_01_12]
    type = ParsedPostprocessor
    pp_names = 'gss_01_num gss_12_num'
    expression = 'gss_01_num - gss_12_num'
    execute_on = 'initial timestep_end'
  []
  [gss_02_num]
    type = ElementAverageValue
    variable = gss_02
    execute_on = 'initial timestep_end'
  []
  [gss_03_num]
    type = ElementAverageValue
    variable = gss_03
    execute_on = 'initial timestep_end'
  []
  [gss_05_num]
    type = ElementAverageValue
    variable = gss_05
    execute_on = 'initial timestep_end'
  []
  [gss_06_num]
    type = ElementAverageValue
    variable = gss_06
    execute_on = 'initial timestep_end'
  []
  [gss_07_num]
    type = ElementAverageValue
    variable = gss_07
    execute_on = 'initial timestep_end'
  []
  [gss_08_num]
    type = ElementAverageValue
    variable = gss_08
    execute_on = 'initial timestep_end'
  []
  [gss_09_num]
    type = ElementAverageValue
    variable = gss_09
    execute_on = 'initial timestep_end'
  []
  [gss_10_num]
    type = ElementAverageValue
    variable = gss_10
    execute_on = 'initial timestep_end'
  []
  [gss_11_num]
    type = ElementAverageValue
    variable = gss_11
    execute_on = 'initial timestep_end'
  []
  [Lambda_plane_1_dot]
    type = ElementAverageValue
    variable = weighted_rate_plane_1
    execute_on = 'initial timestep_end'
  []
  [Lambda_plane_1]
    type = TimeIntegratedPostprocessor
    value = Lambda_plane_1_dot
    time_integration_scheme = implicit-euler
    execute_on = 'initial timestep_end'
  []
  [Lambda_plane_2_dot]
    type = ElementAverageValue
    variable = weighted_rate_plane_2
    execute_on = 'initial timestep_end'
  []
  [Lambda_plane_2]
    type = TimeIntegratedPostprocessor
    value = Lambda_plane_2_dot
    time_integration_scheme = implicit-euler
    execute_on = 'initial timestep_end'
  []
  [Lambda_plane_3_dot]
    type = ElementAverageValue
    variable = weighted_rate_plane_3
    execute_on = 'initial timestep_end'
  []
  [Lambda_plane_3]
    type = TimeIntegratedPostprocessor
    value = Lambda_plane_3_dot
    time_integration_scheme = implicit-euler
    execute_on = 'initial timestep_end'
  []
  [Lambda_plane_4_dot]
    type = ElementAverageValue
    variable = weighted_rate_plane_4
    execute_on = 'initial timestep_end'
  []
  [Lambda_plane_4]
    type = TimeIntegratedPostprocessor
    value = Lambda_plane_4_dot
    time_integration_scheme = implicit-euler
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
  end_time = 10.0

  dtmin = 1.0e-8
  dtmax = 0.025 # timestep-size ceiling

  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 1.0e-3                        # Start with 0.001 s to resolve initial elastic loading
    optimal_iterations = 6
    growth_factor = 1.5
    cutback_factor = 0.5
  []
[]

[Outputs]
  exodus = true
  csv = true
[]
