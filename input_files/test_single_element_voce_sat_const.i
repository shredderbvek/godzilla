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

  # Prescribed axial displacement on front face (z = 1): 2% engineering strain over 10 s
  [pull_z]
    type = FunctionDirichletBC
    variable = disp_z
    boundary = front    # z = 1
    function = '0.0006 * t'
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
    r = 1 #latent hardening coefficient
    h = 190 #fixed state hardening rate scaling coeff (MPa)
    gss_initial = 35 #slip system initial strength (MPa)
    gss_sat_initial = 110 #initial slip system saturation strength (MPa)
    xm_gss = 1 # (m') saturation strength rate scaling exponent
    is_gss_sat_constant = true
  []
[]

[Postprocessors]
  [stress_zz]
    type = ElementAverageValue
    variable = stress_zz
  []
  [strain_zz]
    type = ElementAverageValue
    variable = disp_z
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