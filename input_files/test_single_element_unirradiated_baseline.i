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

[Physics/SolidMechanics/QuasiStatic]
  [all]
    strain = FINITE
    add_variables = true
    generate_output = 'stress_xx stress_yy stress_zz'
  []
[]

[BCs]
  # Symmetry boundary conditions (roller supports)
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

  # Prescribed displacement on top face (z = 1) along z: 2% strain over 10 s
  [pull_z]
    type = FunctionDirichletBC
    variable = disp_z
    boundary = front    # z = 1
    function = '0.002 * t'
  []
[]

[Materials]
  # Single crystal anisotropic elasticity tensor (F321 parameters from Table 3)
  [elasticity_tensor]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    # Bunge Euler angles [phi1, Phi, phi2] in degrees (crystal orientation)
    # Set to [25, 40, 15] to activate multiple slip systems
    euler_angle_1 = 25.0
    euler_angle_2 = 40.0
    euler_angle_3 = 15.0
  []

  # Crystal Plasticity Stress Manager
  [stress]
    type = ComputeMultipleCrystalPlasticityStress
    crystal_plasticity_models = 'busso_orowan_update'
    tan_mod_type = exact
    maximum_substep_iteration = 30
  []

  # Custom constitutive model under test
  [busso_orowan_update]
    type = CrystalPlasticityBussoOrowanIrradiationUpdate
    number_slip_systems = 12
    slip_sys_file_name = slip_systems_FCC.txt
    slip_increment_tolerance = 0.05

    # Flow rule parameters
    ao = 1.0e7
    p = 0.5
    q = 1.0
    activation = 5.0e-16
    k = 1.38e-20
    T = 573.0
    tau_not = 390.0
    G = 75581.0
    G_not = 88000.0

    # Dislocation & defect parameters
    q_rho = 0.09
    q_d = 0.55
    A = 3.1e13
    B = 6.25e-6
    b = 2.54e-7
    k_mul = 0.06
    l_d = 1.0e-5
    R_c = 1.5e-6
    k_dyn = 100.0
    c = 0.9
    lambda = 1.5e-6

    # Irradiation condition (dpa = 2.85, set to 0.0 to test unirradiated baseline)
    dpa = 0.0
    dislocation_density_mobile_initial = 1.3e7
    dislocation_density_immobile_initial = 1.3e7
    r = 0.03
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
    dt = 1.0e-3
    optimal_iterations = 6
    growth_factor = 1.5
    cutback_factor = 0.5
  []
[]

[Outputs]
  exodus = true
  csv = true
[]
