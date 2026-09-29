[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
    file = poly_crystal.inp
    construct_side_list_from_node_list=true
[]

[AuxVariables]
  [pk2]
    order = CONSTANT
    family = MONOMIAL
  []
  [fp_xx]
    order = CONSTANT
    family = MONOMIAL
  []
  [e_xx]
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
  [climb_slip_increment]
   order = CONSTANT
   family = MONOMIAL
  []
  [glide_backstress]
   order = CONSTANT
   family = MONOMIAL
  []
  [climb_backstress]
   order = CONSTANT
   family = MONOMIAL
  []
[]

[Physics/SolidMechanics/QuasiStatic/all]
  strain = FINITE
  add_variables = true
  generate_output = stress_xx
[]

[AuxKernels]
  [pk2]
   type = RankTwoAux
   variable = pk2
   rank_two_tensor = second_piola_kirchhoff_stress
   index_j = 0
   index_i = 0
   execute_on = timestep_end
  []
  [fp_xx]
    type = RankTwoAux
    variable = fp_xx
    rank_two_tensor = plastic_deformation_gradient
    index_j = 0
    index_i = 0
    execute_on = timestep_end
  []
  [e_xx]
    type = RankTwoAux
    variable = e_xx
    rank_two_tensor = total_lagrangian_strain
    index_j = 0
    index_i = 0
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
  [climb_slip_inc]
   type = MaterialStdVectorAux
   variable = climb_slip_increment
   property = climb_slip_increment
   index = 0
   execute_on = timestep_end
  []
  [glide_backstress]
   type = MaterialStdVectorAux
   variable = glide_backstress
   property = backstress
   index = 0
   execute_on = timestep_end
  []
  [climb_backstress]
   type = MaterialStdVectorAux
   variable = climb_backstress
   property = climb_backstress
   index = 0
   execute_on = timestep_end
  []
[]

[BCs]
    [fix_x]
        type = DirichletBC
        variable = disp_x
        value = 0
        boundary = "MICRO-1_fix_x"
    []
    [fix_y]
        type = DirichletBC
        variable = disp_y
        value = 0
        boundary = "MICRO-1_fix_y"
    []
    [fix_z]
        type = DirichletBC
        variable = disp_z
        value = 0
        boundary = "MICRO-1_fix_z"
    []
    [tdisp]
        type = FunctionDirichletBC
        variable = disp_x
        boundary = "MICRO-1_load_x"
        function = strain_history
    []
[]

[Materials]
  [elasticity_tensor_A]
    type = ComputeElasticityTensorCP
    C_ijkl = '170640 108390 108390 170640 108390 170640 77820 77820 77820'
    fill_method = symmetric9
    block = "MICRO-1_GRAIN_1_TET4"
    euler_angle_1 = 101.98
    euler_angle_2 = 145.03
    euler_angle_3 = 249.44
  []
  [elasticity_tensor_B]
    type = ComputeElasticityTensorCP
    C_ijkl = '170640 108390 108390 170640 108390 170640 77820 77820 77820'
    fill_method = symmetric9
    block = "MICRO-1_GRAIN_2_TET4"
    euler_angle_1 = 131.73
    euler_angle_2 = 86.26
    euler_angle_3 = 229.29
  []
  [elasticity_tensor_C]
    type = ComputeElasticityTensorCP
    C_ijkl = '170640 108390 108390 170640 108390 170640 77820 77820 77820'
    fill_method = symmetric9
    block = "MICRO-1_GRAIN_3_TET4"
    euler_angle_1 = 13.58
    euler_angle_2 = 153.68
    euler_angle_3 = 314.40
  []
  [elasticity_tensor_D]
    type = ComputeElasticityTensorCP
    C_ijkl = '170640 108390 108390 170640 108390 170640 77820 77820 77820'
    fill_method = symmetric9
    block = "MICRO-1_GRAIN_4_TET4"
    euler_angle_1 = 88.98
    euler_angle_2 = 124.12
    euler_angle_3 = 115.16
  []
  [stress]
    type = ComputeMultipleCrystalPlasticityStress
    crystal_plasticity_models = 'glide_xtalpl climb_xtalpl'
    tan_mod_type = exact
  []
  [glide_xtalpl]
    type = CrystalPlasticityDislocationCreepUpdate
    mechanism = glide
    number_slip_systems = 12
    slip_sys_file_name = input_slip_sys.txt
    slip_increment_tolerance = 2e-2
    stol = 1e-4
  []
  [climb_xtalpl]
    type = CrystalPlasticityDislocationCreepUpdate
    mechanism = climb
    base_name = climb
    number_slip_systems = 12
    slip_sys_file_name = input_slip_sys.txt
    slip_increment_tolerance = 2e-2
    stol = 1e-4
  []
[]

[Postprocessors]
  [stress_xx]
    type = ElementAverageValue
    variable = stress_xx
  []
  [pk2]
   type = ElementAverageValue
   variable = pk2
  []
  [fp_xx]
    type = ElementAverageValue
    variable = fp_xx
  []
  [e_xx]
    type = ElementAverageValue
    variable = e_xx
  []
  [gss]
    type = ElementAverageValue
    variable = gss
  []
  [slip_increment]
   type = ElementAverageValue
   variable = slip_increment
  []
  [climb_slip_increment]
   type = ElementAverageValue
   variable = climb_slip_increment
  []
  [glide_backstress]
   type = ElementAverageValue
   variable = glide_backstress
  []
  [climb_backstress]
   type = ElementAverageValue
   variable = climb_backstress
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
  solve_type = 'PJFNK'

  petsc_options_iname = '-pc_type -pc_asm_overlap -sub_pc_type -ksp_type -ksp_gmres_restart'
  petsc_options_value = ' asm      2              lu            gmres     200'
  nl_abs_tol = 1e-10
  nl_rel_tol = 1e-10
  nl_abs_step_tol = 1e-10

  dt = 0.25
  dtmin = 0.01
  dtmax = 10.0
  end_time = 205.0
  [TimeStepper]
    type = FunctionDT
    function = cycle_dt
  []
[]

[Outputs]
  exodus = true
  perf_graph = true
  csv = true
[]

[Functions]
  [strain_history]
    type = PiecewiseLinear
    x = '0 5 185 195 205'
    y = '0 0.02 0.02 -0.02 0.02'
  []
  [cycle_dt]
    type = PiecewiseConstant
    x = '0 5 185 195'
    y = '0.25 10 0.25 0.25'
  []
[]
