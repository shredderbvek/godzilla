#pragma once

#include "ComputeStressBase.h"

/** Demonstration only: small strain isotropic stiffness degradation, not a calibrated fracture law. */
class LinearIsotropicDamage : public ComputeStressBase
{
public:
  static InputParameters validParams();
  LinearIsotropicDamage(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override;
  void computeQpStress() override;

  const Real _E;
  const Real _nu;
  const Real _threshold;
  const Real _coefficient;
  const Real _max_damage;
  MaterialProperty<Real> & _damage;
  const MaterialProperty<Real> & _damage_old;
};
