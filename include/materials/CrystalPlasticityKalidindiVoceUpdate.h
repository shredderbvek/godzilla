//
// Created by ghostrobot96 on 11/6/26.
//
#pragma once

#include "CrystalPlasticityKalidindiUpdate.h"

class CrystalPlasticityKalidindiVoceUpdate;
/*
 * This class inhertis from CrystalPlasticityKalidindiUpdate as changes it's hardening
 * law to Voce Type with saturation strength evolution and anisotropic hardening.
 */
class CrystalPlasticityKalidindiVoceUpdate : public CrystalPlasticityKalidindiUpdate
{
public:
  static InputParameters validParams();
  CrystalPlasticityKalidindiVoceUpdate(const InputParameters & parameters);
protected:
  /*overide the existing hardening law with Voce hardening law with saturation strength
   * evolution and anisotropic hardening.
   */
  virtual void calculateStateVariableEvolutionRateComponent() override;

  ///@{additional variable required for the hardening law update
  const Real _gss_sat_initial;
  const Real _xm_gss;
  const Real _ao_sat;
  const Real _n_gss;
  ///}@
};