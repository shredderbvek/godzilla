# ==============================================================================
# Validation Benchmark: Single Crystal Aluminum Uniaxial Compression along [421]
# Reference: E.B. Marin (2006) Sandia Report SAND2006-4170 /
#            S. Groh, E.B. Marin, M.F. Horstemeyer, H.M. Zbib (2009) Int. J. Plasticity
#
# Geometry: Cylinder D = 7.3 mm, L0 = 11.0 mm (Abaqus C3D8R mesh: single_crys_Al.inp)
# Loading:  Uniaxial compression along Z-axis ([421] crystallographic orientation)
#           Constant true strain rate = 1.0e-3 s^-1 to true strain level = 0.60 (t = 600 s)
# Platens:  Frictionless platen compression (u_z = 0 on fixed_face, 2 pin nodes to
#           prevent rigid-body translations/rotations while allowing free lateral ovalization)
# ==============================================================================

[Mesh]
  [fmg]
    type = FileMeshGenerator
    file = single_crys_Al.inp
  []

  # Pin node 1 at bottom face center (-25.0, -5.0, 0.0) to eliminate x/y rigid-body translations
  [pin_center]
    type = ExtraNodesetGenerator
    input = fmg
    new_boundary = 'pin_node_center'
    coord = '-25.0 -5.0 0.0'
    use_closest_node = true
  []

  # Pin node 2 at bottom face perimeter (-21.35, -5.0, 0.0) along y = -5.0 to eliminate z-rotation
  # while leaving radial/lateral Poisson expansion completely unconstrained
  [pin_rotation]
    type = ExtraNodesetGenerator
    input = pin_center
    new_boundary = 'pin_node_rotation'
    coord = '-21.35 -5.0 0.0'
    use_closest_node = true
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
  # Frictionless bottom platen (z = 0): zero vertical displacement
  [fix_z_bottom]
    type = DirichletBC
    variable = disp_z
    boundary = fixed_face
    value = 0.0
  []

  # Rigid-body translation constraints on bottom center node
  [fix_pin_x]
    type = DirichletBC
    variable = disp_x
    boundary = pin_node_center
    value = 0.0
  []
  [fix_pin_y]
    type = DirichletBC
    variable = disp_y
    boundary = pin_node_center
    value = 0.0
  []

  # Rigid-body rotation constraint on bottom perimeter node (allows free radial expansion in x)
  [fix_pin_rot_y]
    type = DirichletBC
    variable = disp_y
    boundary = pin_node_rotation
    value = 0.0
  []

  # Prescribed compressive displacement on top face (z = 11.0 mm)
  # Variable displacement imposing constant true strain rate eps_dot = 1e-3 s^-1:
  #   L(t) = L0 * exp(-eps_dot * t) => u_z(t) = L0 * (exp(-0.001 * t) - 1.0)
  [compress_z_top]
    type = FunctionDirichletBC
    variable = disp_z
    boundary = load_face
    function = '11.0 * (exp(-0.001 * t) - 1.0)'
  []
[]

[Materials]
  # Single crystal Aluminum anisotropic elasticity (Table 4.3 in Marin 2006)
  # C11 = 108.2 GPa, C12 = 61.3 GPa, C44 = 28.5 GPa (units: MPa)
  # Crystal orientation: axes 1-2-3 (x-y-z) aligned with [2 1 -10], [-1 2 0], [4 2 1]
  # Bunge Euler angles: phi1 = 270.0°, Phi = 77.3956°, phi2 = 63.4349°
  # (Corresponding to Kocks Euler angles: phi1 = 180°, psi = 77.4°, phi2 = 26.6°)
  [elasticity_tensor]
    type = ComputeElasticityTensorCP
    C_ijkl = '108200 61300 61300 108200 61300 108200 28500 28500 28500'
    fill_method = symmetric9
    euler_angle_1 = 270.0
    euler_angle_2 = 77.3956
    euler_angle_3 = 63.4349
  []

  # Stress update manager with exact algorithmic tangent modulus
  [stress]
    type = ComputeMultipleCrystalPlasticityStress
    crystal_plasticity_models = 'voce_update'
    tan_mod_type = exact
    maximum_substep_iteration = 5
  []

  # Constitutive hardening model for single crystal Al (Table 4.3 in Marin 2006)
  [voce_update]
    type = CrystalPlasticityKalidindiVoceUpdate
    number_slip_systems = 12
    slip_sys_file_name = slip_systems_FCC.txt
    slip_increment_tolerance = 0.05

    # Flow rule parameters
    ao = 1.0e-3                         # Reference slip shear rate gamma_dot_0 (1/s)
    xm = 0.01                           # Strain rate sensitivity exponent m

    # Voce saturation hardening parameters
    r = 1.0                             # Latent hardening ratio q (q = 1.0 isotropic latent hardening)
    h = 28.4                            # Hardening coefficient h_0 (MPa)
    gss_initial = 3.7                   # Initial slip resistance g_0 (MPa)
    gss_sat_initial = 37.8              # Reference saturation strength g_s0 (MPa)
    xm_gss = 5.0e-4                     # Saturation rate exponent m'
    ao_sat = 5.0e10                     # Reference saturation shear rate gamma_dot_s0 (1/s)
  []
[]

[Postprocessors]
  # Volume-averaged axial Cauchy stress (compressive, negative)
  [stress_zz]
    type = ElementAverageValue
    variable = stress_zz
  []

  # True compressive stress magnitude |sigma_zz| (MPa)
  [true_stress]
    type = ParsedPostprocessor
    pp_names = 'stress_zz'
    expression = 'abs(stress_zz)'
  []

  # Average vertical displacement on load face (mm)
  [disp_z]
    type = AverageNodalVariableValue
    variable = disp_z
    boundary = load_face
  []

  # True compressive strain: eps_true = -ln(1 + u_z / L0)
  [true_strain]
    type = ParsedPostprocessor
    pp_names = 'disp_z'
    expression = '-log(1.0 + disp_z / 11.0)'
  []

  # Engineering compressive strain: eps_eng = -u_z / L0
  [eng_strain]
    type = ParsedPostprocessor
    pp_names = 'disp_z'
    expression = '-disp_z / 11.0'
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

  # Parallel ASM domain decomposition with local LU sub-solvers
  petsc_options_iname = '-pc_type -pc_asm_overlap -sub_pc_type -ksp_type -ksp_gmres_restart'
  petsc_options_value = ' asm      2              lu            gmres     200'

  nl_abs_tol = 1.0e-6
  nl_rel_tol = 1.0e-5
  nl_abs_step_tol = 1.0e-6
  nl_max_its = 20

  start_time = 0.0
  end_time = 600.0                      # Total time = 600 s corresponds to true strain = 0.60

  dtmin = 1.0e-5
  dtmax = 4.0                           # Matches maximum step size used in Abaqus

  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.005                         # Initial small step to smoothly resolve elastic entry
    optimal_iterations = 6
    linear_iteration_ratio = 100        # Accommodates parallel ASM linear iterations so dt can grow
    growth_factor = 1.5
    cutback_factor = 0.5
  []
[]

[Outputs]
  exodus = true
  csv = true
  perf_graph = true
[]
