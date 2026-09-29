#pragma once

#include "CrystalPlasticityStressUpdateBase.h"

class CrystalPlasticityDislocationCreepUpdate : public CrystalPlasticityStressUpdateBase
{
public:
  static InputParameters validParams();
  CrystalPlasticityDislocationCreepUpdate(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override;
  void setInitialConstitutiveVariableValues() override;
  void setSubstepConstitutiveVariableValues() override;
  void updateSubstepConstitutiveVariableValues() override;
  void cacheStateVariablesBeforeUpdate() override;
  bool calculateSlipRate() override;
  void calculateConstitutiveSlipDerivative(std::vector<Real> & derivative) override;
  bool updateStateVariables() override;
  bool areConstitutiveStateVariablesConverged() override;

  const bool _climb;
  const Real _gamma0, _activation, _temperature, _tau0, _mu, _mu0, _p, _q;
  const Real _s0, _sbar, _hs, _dd, _hb, _h2, _gth, _muprime, _f;
  const Real _tau0c, _pc, _hc, _binf, _psi;
  const MaterialProperty<RankTwoTensor> & _crysrot;
  MaterialProperty<std::vector<Real>> & _backstress;
  const MaterialProperty<std::vector<Real>> & _backstress_old;
  std::vector<Real> _previous_b, _previous_s, _before_b, _before_s;
};
