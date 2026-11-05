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
    function = '0.002 * t'
  []
[]

[Materials]
  # Single crystal anisotropic elasticity tensor (F321 parameters from Table 3)
  [elasticity_tensor]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    # Initial crystal orientation (Bunge Euler angles in degrees)
    euler_angle_1 = 25.0
    euler_angle_2 = 40.0
    euler_angle_3 = 15.0
  []

  # Crystal Plasticity Stress Update Manager
  [stress]
    type = ComputeMultipleCrystalPlasticityStress
    crystal_plasticity_models = 'busso_orowan_update'
    tan_mod_type = exact
    maximum_substep_iteration = 30     # Increased to allow subcycling under fast slip rates
  []

  # Custom Busso-Orowan constitutive model under test
  [busso_orowan_update]
    type = CrystalPlasticityBussoOrowanIrradiationUpdate
    number_slip_systems = 12
    slip_sys_file_name = slip_systems_FCC.txt
    slip_increment_tolerance = 0.05             # Substep allowable slip increment tolerance

    # Flow rule parameters (Liu et al. Table 4)
    ao = 1.0e7                        # Reference attempt frequency (1/s)
    p = 0.5
    q = 1.0
    activation = 5.0e-16              # Activation energy Q0 (0.001 J)
    k = 1.38e-20                      # Boltzmann constant (0.001 J/K)
    T = 573.0                         # Temperature in K (300 C = 573 K)
    tau_not = 390.0                   # Reference threshold tau_0 (MPa)
    G = 75581.0                       # Shear modulus at T (MPa)
    G_not = 88000.0                   # Shear modulus at 0K (MPa)

    # Dislocation & irradiation defect parameters (Liu et al. Table 5)
    q_rho = 0.09                      # Dislocation statistical factor
    q_d = 0.55                        # Loop defect strength factor
    A = 3.1e13                        # Loop density scaling factor (1/mm^3)
    B = 6.25e-6                       # Loop diameter scaling factor (mm)
    b = 2.54e-7                       # Burgers vector magnitude (mm)
    k_mul = 0.06                      # Dislocation proliferation rate
    l_d = 1.0e-5                      # Average mobile dislocation length (mm)
    R_c = 1.5e-6                      # Critical annihilation radius (mm)
    k_dyn = 100.0                     # Dynamic recovery coefficient
    c = 0.9                           # Loop annihilation exponent
    lambda = 1.5e-6                   # Mean free path (mm)

    # Irradiation condition: 2.85 dpa (set to 0.0 for unirradiated baseline)
    dpa = 2.85
    dislocation_density_mobile_initial = 1.3e7
    dislocation_density_immobile_initial = 1.3e7
    r = 0.03                          # Latent hardening ratio (A_alpha_beta)
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