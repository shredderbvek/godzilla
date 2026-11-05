[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
  [msh]
    type = GeneratedMeshGenerator
    dim = 3
    nx = 1
    ny = 1
    nz = 2
    xmin = 0.0
    xmax = 1.0
    ymin = 0.0
    ymax = 1.0
    zmin = 0.0
    zmax = 2.0
  []
  [subdomain_1]
    type = SubdomainBoundingBoxGenerator
    input = msh
    bottom_left = '0 0 0'
    top_right = '1.0 1.0 1.0'
    block_id = 1
    block_name = 'Block1'
  []
  [subdomain_2]
    type = SubdomainBoundingBoxGenerator
    input = subdomain_1
    bottom_left = '0 0 1.0'
    top_right = '1.0 1.0 2.0'
    block_id = 2
    block_name = 'Block2'
  []
  [breakmesh]
    input = subdomain_2
    type = BreakMeshByBlockGenerator
  []
  [add_side_sets]
    input = breakmesh
    type = SideSetsFromNormalsGenerator
    normals = '-1 0  0
                1 0  0
                0 -1 0
                0  1 0
                0  0 -1
                0  0  1'
    fixed_normal = true
    new_boundary = 'x0 x1 y0 y1 z0 z1'
  []
[]

[Physics/SolidMechanics/QuasiStatic/all]
  strain = FINITE
  add_variables = true
  generate_output = 'stress_zz'
[]

[Physics/SolidMechanics/CohesiveZone/czm_gb]
  boundary = 'Block1_Block2'
  strain = FINITE
[]

[AuxVariables]
  [damage]
    order = CONSTANT
    family = MONOMIAL
  []
  [fp_zz]
    order = CONSTANT
    family = MONOMIAL
  []
[]

[AuxKernels]
  [damage_aux]
    type = MaterialRealAux
    variable = damage
    property = damage
    boundary = 'Block1_Block2'
    execute_on = timestep_end
  []
  [fp_zz]
    type = RankTwoAux
    variable = fp_zz
    rank_two_tensor = plastic_deformation_gradient
    index_j = 2
    index_i = 2
    execute_on = timestep_end
  []
[]

[BCs]
  [fix_x]
    type = DirichletBC
    variable = disp_x
    boundary = 'x0'
    value = 0.0
  []
  [fix_y]
    type = DirichletBC
    variable = disp_y
    boundary = 'y0'
    value = 0.0
  []
  [fix_z]
    type = DirichletBC
    variable = disp_z
    boundary = 'z0'
    value = 0.0
  []
  [pull_z]
    type = FunctionDirichletBC
    variable = disp_z
    boundary = 'z1'
    function = '0.002 * t'
  []
[]

[Materials]
  # Grain 1 (Block 1) Elasticity
  [elasticity_tensor_1]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 1
    euler_angle_1 = 25.0
    euler_angle_2 = 40.0
    euler_angle_3 = 15.0
  []
  # Grain 2 (Block 2) Elasticity (Grain 2 orientation)
  [elasticity_tensor_2]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 2
    euler_angle_1 = 85.0
    euler_angle_2 = 30.0
    euler_angle_3 = 60.0
  []
  [stress]
    type = ComputeMultipleCrystalPlasticityStress
    crystal_plasticity_models = 'busso_orowan_update'
    tan_mod_type = exact
    maximum_substep_iteration = 30
  []
  # Busso-Orowan Crystal Plasticity Unirradiated Baseline (0.0 dpa)
  [busso_orowan_update]
    type = CrystalPlasticityBussoOrowanIrradiationUpdate
    number_slip_systems = 12
    slip_sys_file_name = input_files/slip_systems_FCC.txt
    slip_increment_tolerance = 0.05
    ao = 1.0e7
    p = 0.5
    q = 1.0
    activation = 5.0e-16
    k = 1.38e-20
    T = 573.0
    tau_not = 390.0
    G = 75581.0
    G_not = 88000.0
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
    dpa = 0.0
    dislocation_density_mobile_initial = 1.3e7
    dislocation_density_immobile_initial = 1.3e7
    r = 0.03
  []
  # Grain Boundary Cohesive Zone Model (CZM)
  [czm_mat]
    type = BiLinearMixedModeTraction
    boundary = 'Block1_Block2'
    penalty_stiffness = 1.0e6
    GI_c = 8.0
    GII_c = 8.0
    normal_strength = 900.0
    shear_strength = 600.0
    eta = 2.0
    viscosity = 1.0e-3
  []
[]

[Postprocessors]
  [stress_zz]
    type = ElementAverageValue
    variable = stress_zz
  []
  [disp_z_top]
    type = SideAverageValue
    variable = disp_z
    boundary = 'z1'
  []
  [strain_zz]
    type = ParsedPostprocessor
    expression = 'disp_z_top / 2.0'
    pp_names = 'disp_z_top'
  []
  [gb_damage]
    type = SideAverageValue
    variable = damage
    boundary = 'Block1_Block2'
  []
  [fp_zz_grain1]
    type = ElementAverageValue
    variable = fp_zz
    block = 1
  []
  [fp_zz_grain2]
    type = ElementAverageValue
    variable = fp_zz
    block = 2
  []
[]

[Preconditioning]
  [smp]
    type = SMP
    full = true
  []
[]

[Executioner]
  type = Transient
  solve_type = 'NEWTON'
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
  nl_abs_tol = 1.0e-7
  nl_rel_tol = 1.0e-5
  nl_max_its = 25

  start_time = 0.0
  end_time = 10.0
  dt = 0.1
  dtmin = 1.0e-4
  dtmax = 0.25

  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.1
    optimal_iterations = 5
    growth_factor = 1.25
    cutback_factor = 0.5
  []
[]

[Outputs]
  csv = true
  exodus = true
[]
