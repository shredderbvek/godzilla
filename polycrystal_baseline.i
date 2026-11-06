[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
  [fmg]
    type = FileMeshGenerator
    file = input_files/simulation.msh
  []
  [add_external_sidesets]
    type = SideSetsFromNormalsGenerator
    input = fmg
    normals = '-1 0 0
                1 0 0
                0 -1 0
                0 1 0
                0 0 -1
                0 0 1'
    new_boundary = 'x0 x1 y0 y1 z0 z1'
  []
[]

[AuxVariables]
  [pk2]
    order = CONSTANT
    family = MONOMIAL
  []
  [fp_zz]
    order = CONSTANT
    family = MONOMIAL
  []
  [e_zz]
    order = CONSTANT
    family = MONOMIAL
  []
  [gss]
    order = CONSTANT
    family = MONOMIAL
  []
  [slip_increment]
    order = CONSTANT
    family = MONOMIAL
  []
[]

[Physics/SolidMechanics/QuasiStatic/all]
  strain = FINITE
  add_variables = true
  generate_output = 'stress_xx stress_yy stress_zz'
[]

[AuxKernels]
  [pk2]
    type = RankTwoAux
    variable = pk2
    rank_two_tensor = second_piola_kirchhoff_stress
    index_j = 2
    index_i = 2
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
  [e_zz]
    type = RankTwoAux
    variable = e_zz
    rank_two_tensor = total_lagrangian_strain
    index_j = 2
    index_i = 2
    execute_on = timestep_end
  []
  [gss]
    type = MaterialStdVectorAux
    variable = gss
    property = slip_resistance
    index = 0
    execute_on = timestep_end
  []
  [slip_inc]
    type = MaterialStdVectorAux
    variable = slip_increment
    property = slip_increment
    index = 0
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
  [tdisp]
    type = FunctionDirichletBC
    variable = disp_z
    boundary = 'z1'
    function = '0.005*t'
  []
[]

[Materials]
  [elasticity_tensor_1]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 1
    euler_angle_1 = 236.3354
    euler_angle_2 = 80.0725
    euler_angle_3 = 264.7298
  []
  [elasticity_tensor_2]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 2
    euler_angle_1 = 41.8132
    euler_angle_2 = 78.4388
    euler_angle_3 = 284.0152
  []
  [elasticity_tensor_3]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 3
    euler_angle_1 = 272.7027
    euler_angle_2 = 147.2213
    euler_angle_3 = 6.9862
  []
  [elasticity_tensor_4]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 4
    euler_angle_1 = 333.7666
    euler_angle_2 = 25.5609
    euler_angle_3 = 343.2670
  []
  [elasticity_tensor_5]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 5
    euler_angle_1 = 98.1966
    euler_angle_2 = 8.6597
    euler_angle_3 = 344.3933
  []
  [elasticity_tensor_6]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 6
    euler_angle_1 = 108.0456
    euler_angle_2 = 54.2462
    euler_angle_3 = 336.6538
  []
  [elasticity_tensor_7]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 7
    euler_angle_1 = 347.1522
    euler_angle_2 = 31.9676
    euler_angle_3 = 200.9590
  []
  [elasticity_tensor_8]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 8
    euler_angle_1 = 313.5730
    euler_angle_2 = 104.3612
    euler_angle_3 = 203.6033
  []
  [elasticity_tensor_9]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 9
    euler_angle_1 = 87.9897
    euler_angle_2 = 95.3342
    euler_angle_3 = 278.3551
  []
  [elasticity_tensor_10]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 10
    euler_angle_1 = 148.8949
    euler_angle_2 = 60.4047
    euler_angle_3 = 214.4550
  []
  [elasticity_tensor_11]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 11
    euler_angle_1 = 331.0921
    euler_angle_2 = 26.8145
    euler_angle_3 = 314.2997
  []
  [elasticity_tensor_12]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 12
    euler_angle_1 = 279.8280
    euler_angle_2 = 41.3468
    euler_angle_3 = 115.8273
  []
  [elasticity_tensor_13]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 13
    euler_angle_1 = 289.1642
    euler_angle_2 = 158.3131
    euler_angle_3 = 226.2362
  []
  [elasticity_tensor_14]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 14
    euler_angle_1 = 257.6250
    euler_angle_2 = 52.8299
    euler_angle_3 = 149.9900
  []
  [elasticity_tensor_15]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 15
    euler_angle_1 = 256.4646
    euler_angle_2 = 72.5293
    euler_angle_3 = 4.8102
  []
  [elasticity_tensor_16]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 16
    euler_angle_1 = 109.7929
    euler_angle_2 = 130.6286
    euler_angle_3 = 188.4566
  []
  [elasticity_tensor_17]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 17
    euler_angle_1 = 76.2698
    euler_angle_2 = 119.0664
    euler_angle_3 = 172.3726
  []
  [elasticity_tensor_18]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 18
    euler_angle_1 = 52.8436
    euler_angle_2 = 86.3865
    euler_angle_3 = 149.5131
  []
  [elasticity_tensor_19]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 19
    euler_angle_1 = 276.6932
    euler_angle_2 = 139.7564
    euler_angle_3 = 237.3951
  []
  [elasticity_tensor_20]
    type = ComputeElasticityTensorCP
    C_ijkl = '255537 104374 104374 255537 104374 255537 75581 75581 75581'
    fill_method = symmetric9
    block = 20
    euler_angle_1 = 307.4926
    euler_angle_2 = 72.5962
    euler_angle_3 = 99.6311
  []

  [stress]
    type = ComputeMultipleCrystalPlasticityStress
    crystal_plasticity_models = 'busso_orowan_update'
    tan_mod_type = exact
    maximum_substep_iteration = 30
  []

  [busso_orowan_update]
    type = CrystalPlasticityBussoOrowanIrradiationUpdate
    number_slip_systems = 12
    slip_sys_file_name = slip_systems_FCC.txt
    slip_increment_tolerance = 0.05

    # Flow rule parameters (Liu et al. Table 4)
    ao = 1.0e7
    p = 0.5
    q = 1.0
    activation = 5.0e-16
    k = 1.38e-20
    T = 573.0
    tau_not = 390.0
    G = 75581.0
    G_not = 88000.0

    # Dislocation & irradiation defect parameters (Liu et al. Table 5)
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

    # Irradiation condition: 2.85 dpa
    dpa = 0
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
  [pk2]
    type = ElementAverageValue
    variable = pk2
  []
  [fp_zz]
    type = ElementAverageValue
    variable = fp_zz
  []
  [e_zz]
    type = ElementAverageValue
    variable = e_zz
  []
  [gss]
    type = ElementAverageValue
    variable = gss
  []
  [slip_increment]
    type = ElementAverageValue
    variable = slip_increment
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
  line_search = 'none'

  petsc_options_iname = '-pc_type -pc_asm_overlap -sub_pc_type -ksp_type -ksp_gmres_restart'
  petsc_options_value = ' asm      2              lu            gmres     200'
  nl_abs_tol = 1e-8
  nl_rel_tol = 1e-6
  nl_abs_step_tol = 1e-8
  nl_max_its = 15

  start_time = 0.0
  end_time = 10
  dtmin = 1.0e-5
  dtmax = 0.25

  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.1
    optimal_iterations = 6
    growth_factor = 1.25
    cutback_factor = 0.5
  []
[]

[Outputs]
  exodus = true
  perf_graph = true
  csv = true
[]
