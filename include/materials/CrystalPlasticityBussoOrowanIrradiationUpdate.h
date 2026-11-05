#pragma once

#include "CrystalPlasticityStressUpdateBase.h"

/*
 * CrystalPlasticityBussoOrowanIrradiationUpdate uses the multiplicative decomposition
 * of the deformation gradient and solves the PK2 stress residual equation at
 * the intermediate configuration to evolve the material state. The internal variables
 * are updated using a predictor-corrector algorithm. Backward Euler Integration
 * scheme is used for the dislocation and defect rate equations.
 */
class CrystalPlasticityBussoOrowanIrradiationUpdate : public CrystalPlasticityStressUpdateBase
{
public:
  static InputParameters validParams();
  CrystalPlasticityBussoOrowanIrradiationUpdate(const InputParameters & parameters);

protected:
  virtual void initQpStatefulProperties() override;

  virtual void setInitialConstitutiveVariableValues() override;

  virtual void setSubstepConstitutiveVariableValues() override;

  virtual void updateSubstepConstitutiveVariableValues() override;

  virtual void calculateSlipResistance() override;

  virtual bool calculateSlipRate() override;

  virtual void calculateEquivalentSlipIncrement(RankTwoTensor & equivalent_slip_increment) override;

  virtual void calculateConstitutiveSlipDerivative(std::vector<Real> & dslip_dtau) override;

  virtual void cacheStateVariablesBeforeUpdate() override;

  virtual void calculateStateVariableEvolutionRateComponent() override;

  virtual bool updateStateVariables() override;

  virtual bool areConstitutiveStateVariablesConverged() override;

  const Real _dislocation_density_mobile_tol;
  const Real _dislocation_density_immobile_tol;
  const Real _loop_density_tol;

  // Material properties for dislocation and loop densities
  MaterialProperty<std::vector<Real>> & _dislocation_density_mobile;
  const MaterialProperty<std::vector<Real>> & _dislocation_density_mobile_old;

  MaterialProperty<std::vector<Real>> & _dislocation_density_immobile;
  const MaterialProperty<std::vector<Real>> & _dislocation_density_immobile_old;

  MaterialProperty<std::vector<Real>> & _loop_density;
  const MaterialProperty<std::vector<Real>> & _loop_density_old;

  // Constitutive parameters
  const Real _ao, _p, _q, _activation, _k, _T, _tau_not, _G, _G_not, _gss_initial;
  const Real _q_rho, _q_d, _A, _B, _b, _k_mul, _l_d, _R_c, _k_dyn, _c, _lambda;
  const Real _dpa;
  const Real _dislocation_density_mobile_initial, _dislocation_density_immobile_initial;
  const Real _r;

  // Increments
  std::vector<Real> _slip_resistance_increment;
  std::vector<Real> _dislocation_density_mobile_increment;
  std::vector<Real> _dislocation_density_immobile_increment;
  std::vector<Real> _loop_density_increment;

  // Substepping cache
  std::vector<Real> _previous_substep_slip_resistance;
  std::vector<Real> _previous_substep_dislocation_density_mobile;
  std::vector<Real> _previous_substep_dislocation_density_immobile;
  std::vector<Real> _previous_substep_loop_density;

  // Iteration cache for convergence check
  std::vector<Real> _slip_resistance_before_update;
  std::vector<Real> _dislocation_density_mobile_before_update;
  std::vector<Real> _dislocation_density_immobile_before_update;
  std::vector<Real> _loop_density_before_update;
};